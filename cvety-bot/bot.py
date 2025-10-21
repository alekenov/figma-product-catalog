"""
Cvety.kz Production Customer Bot (shop_id=17008)
Telegram Bot with Claude AI integration for visual product search and natural language ordering.

Architecture:
- Uses AI Agent Service (Railway) with Claude Sonnet 4.5
- Full MCP tools integration (40+ tools for products, orders, payments, etc.)
- Webhook mode for Railway deployment
- Production bot for cvety.kz customers (185.125.90.141)
"""
import os
import uuid
from typing import Optional
from dotenv import load_dotenv

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Load environment variables
load_dotenv()

# Import shared modules from parent telegram-bot directory
# Note: These will be copied to cvety-bot/ directory for deployment
from mcp_client import create_mcp_client, NetworkError
from formatters import extract_product_images
from logging_config import configure_logging, get_logger, bind_request_context, clear_request_context

import httpx
import asyncio

configure_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)
logger.info("cvety_bot_starting", shop_id=os.getenv('DEFAULT_SHOP_ID', '17008'))


class CvetyBot:
    """
    Cvety.kz Production Customer Bot.

    Key features:
    - shop_id=17008 (production cvety.kz)
    - Webhook mode for Railway
    - Visual search with Claude AI
    - Natural language ordering
    - Kaspi Pay integration
    """

    def __init__(self):
        # Load configuration
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        if not self.telegram_token:
            raise ValueError("TELEGRAM_TOKEN must be set")

        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "https://mcp-server-production-00cd.up.railway.app")
        self.shop_id = int(os.getenv("DEFAULT_SHOP_ID", "17008"))
        self.ai_agent_url = os.getenv("AI_AGENT_URL", "https://ai-agent-service-production-c331.up.railway.app")
        self.webhook_url = os.getenv("WEBHOOK_URL")  # Set by Railway: https://cvety-bot-production.up.railway.app
        self.webhook_secret = os.getenv("WEBHOOK_SECRET", "")  # For webhook security

        logger.info("bot_configuration",
                   shop_id=self.shop_id,
                   ai_agent_url=self.ai_agent_url,
                   mcp_server_url=self.mcp_server_url,
                   webhook_mode=True)

        # Initialize MCP client
        self.mcp_client = create_mcp_client(self.mcp_server_url)

        # HTTP client for AI Agent calls (initialized in post_init)
        self.http_client: Optional[httpx.AsyncClient] = None

        # Create application
        self.app = Application.builder().token(self.telegram_token).build()

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register all command and message handlers."""
        # Commands
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))

        # Contact sharing (for authorization)
        self.app.add_handler(MessageHandler(filters.CONTACT, self.handle_contact))

        # Photo messages (visual search)
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))

        # Text messages (AI conversation)
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    async def check_authorization(self, user_id: int) -> bool:
        """
        Check if user is authorized (has shared contact).
        Returns True if authorized, False if not found or error occurs.
        """
        try:
            logger.info("authorization_check", user_id=user_id, shop_id=self.shop_id)
            client = await self.mcp_client.get_telegram_client(
                telegram_user_id=str(user_id),
                shop_id=self.shop_id
            )
            is_authorized = client is not None
            logger.info("authorization_result", user_id=user_id, is_authorized=is_authorized)
            return is_authorized

        except NetworkError as e:
            logger.error("authorization_network_error", user_id=user_id, error=str(e))
            return False

        except Exception as e:
            logger.error("authorization_unexpected_error", user_id=user_id, error=str(e))
            return False

    async def _request_authorization(self, update: Update):
        """Request user authorization via contact sharing."""
        contact_button = KeyboardButton(
            text="📱 Поделиться контактом",
            request_contact=True
        )
        keyboard = ReplyKeyboardMarkup(
            [[contact_button]],
            one_time_keyboard=True,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "🌸 Добро пожаловать в Cvety.kz!\n\n"
            "Для использования бота необходимо авторизоваться.\n\n"
            "Возможности:\n"
            "• 🔍 Поиск букетов по фото\n"
            "• 💬 Заказ через естественный язык\n"
            "• 📦 Отслеживание заказов\n"
            "• 💳 Оплата Kaspi Pay\n\n"
            "Нажмите кнопку ниже, чтобы начать:",
            reply_markup=keyboard
        )

    async def start_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /start command."""
        user = update.effective_user

        # Check if user is already authorized
        is_authorized = await self.check_authorization(user.id)

        if not is_authorized:
            await self._request_authorization(update)
            return

        # User is authorized - send brief help message
        await update.message.reply_text(
            "✅ Вы авторизованы!\n\n"
            "Отправьте:\n"
            "📸 Фото букета — для визуального поиска\n"
            "💬 Текст — для заказа или вопросов\n\n"
            "Попробуйте: \"Покажи букеты до 15000 тенге\""
        )

    async def help_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /help command."""
        await update.message.reply_text(
            "🌸 **Cvety.kz Bot - Помощь**\n\n"
            "**Возможности:**\n"
            "• Поиск похожих букетов по фото\n"
            "• Фильтрация товаров по цене и типу\n"
            "• Оформление заказа естественным языком\n"
            "• Отслеживание статуса заказа\n\n"
            "**Примеры запросов:**\n"
            "• \"Покажи розы до 20000 тенге\"\n"
            "• \"Хочу заказать букет на завтра к 15:00\"\n"
            "• \"Где мой заказ #ABC123?\"\n"
            "• Отправьте фото букета для поиска похожих\n\n"
            "Нужна помощь? Напишите свой вопрос!",
            parse_mode="Markdown"
        )

    async def handle_contact(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle contact sharing for authorization."""
        user = update.effective_user
        contact = update.message.contact

        # Verify it's user's own contact
        if contact.user_id != user.id:
            await update.message.reply_text(
                "❌ Пожалуйста, поделитесь вашим собственным контактом.",
                reply_markup=ReplyKeyboardRemove()
            )
            return

        try:
            logger.info("registration_started", user_id=user.id, shop_id=self.shop_id)

            # Register client via MCP
            client_data = await self.mcp_client.register_telegram_client(
                telegram_user_id=str(user.id),
                phone=contact.phone_number,
                customer_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or "Клиент",
                shop_id=self.shop_id,
                telegram_username=user.username,
                telegram_first_name=user.first_name
            )

            # Verify registration
            if not client_data or "id" not in client_data:
                raise Exception("Registration returned invalid data")

            logger.info("registration_completed", user_id=user.id, client_id=client_data.get("id"))

            await update.message.reply_text(
                f"✅ Спасибо, {user.first_name}! Вы успешно авторизованы.\n\n"
                f"Отправьте фото букета или напишите ваш запрос!",
                reply_markup=ReplyKeyboardRemove()
            )

        except NetworkError as e:
            logger.error("registration_network_error", user_id=user.id, error=str(e))
            await update.message.reply_text(
                "😔 Не удалось подключиться к серверу.\n\n"
                "Попробуйте еще раз через /start",
                reply_markup=ReplyKeyboardRemove()
            )

        except Exception as e:
            logger.error("registration_unexpected_error", user_id=user.id, error=str(e))
            await update.message.reply_text(
                "😔 Произошла ошибка при регистрации.\n\n"
                "Попробуйте еще раз через /start",
                reply_markup=ReplyKeyboardRemove()
            )

    async def handle_photo(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle photo messages for AI-powered visual search."""
        user_id = update.effective_user.id

        # Check authorization
        is_authorized = await self.check_authorization(user_id)
        if not is_authorized:
            await self._request_authorization(update)
            return

        request_id = f"req_{uuid.uuid4().hex[:12]}"
        bind_request_context(
            request_id=request_id,
            telegram_user_id=str(user_id),
            chat_id=update.message.chat.id
        )

        logger.info("photo_received", photo_count=len(update.message.photo))

        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            # Get largest photo
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()
            image_url = photo_file.file_path

            caption = update.message.caption or "Найди похожие букеты"

            # Get client data
            client_data = await self.mcp_client.get_telegram_client(
                telegram_user_id=str(user_id),
                shop_id=self.shop_id
            )

            # Call AI Agent with image
            response = await self.http_client.post(
                f"{self.ai_agent_url}/chat",
                json={
                    "message": caption,
                    "image_url": image_url,
                    "user_id": str(user_id),
                    "channel": "telegram",
                    "context": {
                        "username": update.effective_user.username,
                        "first_name": update.effective_user.first_name,
                        "phone": client_data.get("phone") if client_data else None,
                        "customer_name": client_data.get("customerName") if client_data else None,
                        "telegram_id": str(user_id),
                        "shop_id": self.shop_id
                    }
                },
                headers={"X-Request-ID": request_id},
                timeout=90.0
            )
            response.raise_for_status()
            result = response.json()

            response_text = result.get("text", "")
            if not response_text.strip():
                response_text = "😔 Не удалось найти похожие букеты.\n\nПопробуйте отправить другое фото."

            await update.message.reply_text(response_text)

        except Exception as e:
            logger.error("visual_search_error", error=str(e))
            await update.message.reply_text(
                "😔 Ошибка при обработке фото. Попробуйте еще раз."
            )
        finally:
            clear_request_context()

    async def handle_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle text messages via AI Agent Service."""
        user_id = update.effective_user.id
        message_text = update.message.text

        # Check authorization
        is_authorized = await self.check_authorization(user_id)
        if not is_authorized:
            await self._request_authorization(update)
            return

        request_id = f"req_{uuid.uuid4().hex[:12]}"
        bind_request_context(
            request_id=request_id,
            telegram_user_id=str(user_id),
            chat_id=update.message.chat.id
        )

        logger.info("message_received", message_length=len(message_text))

        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            # Get client data
            client_data = await self.mcp_client.get_telegram_client(
                telegram_user_id=str(user_id),
                shop_id=self.shop_id
            )

            # Call AI Agent
            response = await self.http_client.post(
                f"{self.ai_agent_url}/chat",
                json={
                    "message": message_text,
                    "user_id": str(user_id),
                    "channel": "telegram",
                    "context": {
                        "username": update.effective_user.username,
                        "first_name": update.effective_user.first_name,
                        "phone": client_data.get("phone") if client_data else None,
                        "customer_name": client_data.get("customerName") if client_data else None,
                        "telegram_id": str(user_id),
                        "shop_id": self.shop_id
                    }
                },
                headers={"X-Request-ID": request_id},
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()

            response_text = result.get("text", "")
            show_products = bool(result.get("show_products"))
            product_ids = result.get("product_ids")

            if not response_text.strip():
                response_text = "😔 Извините, произошла ошибка. Попробуйте еще раз."

            # Show products if AI decided to
            if show_products:
                try:
                    if product_ids:
                        products_response = await self.http_client.post(
                            f"{self.ai_agent_url}/products/by_ids",
                            json={"product_ids": product_ids},
                            timeout=30.0
                        )
                    else:
                        products_response = await self.http_client.get(
                            f"{self.ai_agent_url}/products/{user_id}",
                            params={"channel": "telegram"},
                            timeout=30.0
                        )

                    if products_response.status_code == 200:
                        products_data = products_response.json()
                        products = products_data.get("products", [])

                        if products:
                            images = extract_product_images(products, max_products=5)
                            if images:
                                for img in images:
                                    await update.message.reply_photo(
                                        photo=img["url"],
                                        caption=img["caption"]
                                    )
                                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.error("product_fetch_failed", error=str(e))

            # Send text response
            if len(response_text) > 4096:
                for i in range(0, len(response_text), 4096):
                    await update.message.reply_text(response_text[i:i+4096])
            else:
                await update.message.reply_text(response_text)

            logger.info("message_handled_successfully")

        except Exception as e:
            logger.error("message_handling_failed", error=str(e))
            await update.message.reply_text(
                "😔 Извините, произошла ошибка. Попробуйте еще раз."
            )
        finally:
            clear_request_context()

    async def post_init(self, application: Application):
        """Post-initialization hook."""
        self.http_client = httpx.AsyncClient(timeout=60.0)
        # Note: webhook is configured by run_webhook() automatically
        logger.info("bot_initialized_successfully", shop_id=self.shop_id)

    async def post_shutdown(self, application: Application):
        """Post-shutdown hook."""
        await self.mcp_client.close()
        if self.http_client:
            await self.http_client.aclose()
        logger.info("bot_shutdown_successfully")

    def run_webhook(self, port: int = 8080):
        """Run bot in webhook mode (for Railway deployment)."""
        logger.info("starting_cvety_bot_webhook_mode", shop_id=self.shop_id, port=port)

        self.app.post_init = self.post_init
        self.app.post_shutdown = self.post_shutdown

        # Run webhook on 0.0.0.0 to accept connections from Railway
        webhook_path = f"/webhook/{self.webhook_secret}" if self.webhook_secret else "/webhook"
        full_webhook_url = f"{self.webhook_url}{webhook_path}"

        self.app.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=full_webhook_url,  # Must be FULL URL with path
            url_path=webhook_path,
            allowed_updates=Update.ALL_TYPES
        )


def main():
    """Main entry point for Railway deployment."""
    port = int(os.getenv("PORT", "8080"))

    print("🌸 Cvety.kz Production Customer Bot - Starting...")
    print(f"📍 Shop ID: {os.getenv('DEFAULT_SHOP_ID', '17008')}")
    print(f"🤖 AI Agent: {os.getenv('AI_AGENT_URL')}")
    print(f"🔧 MCP Server: {os.getenv('MCP_SERVER_URL')}")
    print(f"🌐 Webhook URL: {os.getenv('WEBHOOK_URL')}")
    print(f"🔌 Port: {port}")
    print("")

    bot = CvetyBot()
    bot.run_webhook(port=port)


if __name__ == "__main__":
    main()
