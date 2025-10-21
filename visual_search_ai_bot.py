"""
Visual Search AI Bot for Flower Shop (shop_id=17008)
Telegram Bot with Claude AI integration for visual product search and natural language ordering.

Architecture:
- Uses existing AI Agent Service (port 8002) with Claude Haiku 4.5
- Full MCP tools integration (40+ tools for products, orders, payments, etc.)
- Simplified polling mode (no webhook) for local development
- Shares MCP client and formatters with main telegram-bot
"""
import os
import sys
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

# Add telegram-bot directory to path for importing shared modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'telegram-bot'))

from mcp_client import create_mcp_client, NetworkError
from formatters import extract_product_images
import httpx
import asyncio

# Load environment variables from .env.visual_search
env_file = os.path.join(os.path.dirname(__file__), '.env.visual_search')
if os.path.exists(env_file):
    load_dotenv(env_file)
    print(f"✅ Loaded configuration from {env_file}")
else:
    print(f"⚠️  Configuration file {env_file} not found, using defaults")
    load_dotenv()

# Configure structured logging (reuse from telegram-bot)
from logging_config import configure_logging, get_logger, bind_request_context, clear_request_context

configure_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)
logger.info("visual_search_ai_bot_starting", shop_id=os.getenv('DEFAULT_SHOP_ID', '17008'))


class VisualSearchAIBot:
    """
    Visual Search AI Bot - simplified version focused on local development.

    Key differences from main telegram-bot:
    - shop_id=17008 (vs 8 for main bot)
    - Polling mode only (no webhook support)
    - Reuses AI Agent Service and MCP infrastructure
    """

    def __init__(self):
        # Load configuration
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        if not self.telegram_token:
            raise ValueError("TELEGRAM_TOKEN must be set in .env.visual_search")

        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        self.shop_id = int(os.getenv("DEFAULT_SHOP_ID", "17008"))
        self.ai_agent_url = os.getenv("AI_AGENT_URL", "http://localhost:8002")

        logger.info("bot_configuration",
                   shop_id=self.shop_id,
                   ai_agent_url=self.ai_agent_url,
                   mcp_server_url=self.mcp_server_url)

        # Initialize MCP client (for authorization checks)
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
            "🌸 Добро пожаловать в Visual Search Bot!\n\n"
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
            "🌸 **Visual Search AI Bot - Помощь**\n\n"
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

            # Register client via backend API (with MCP fallback)
            client_data = await self.mcp_client.register_telegram_client(
                telegram_user_id=str(user.id),
                phone=contact.phone_number,
                customer_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or "Клиент",
                shop_id=self.shop_id,
                telegram_username=user.username,
                telegram_first_name=user.first_name
            )

            # Verify registration was successful
            if not client_data or "id" not in client_data:
                raise Exception("Registration returned invalid data (missing 'id' field)")

            logger.info("registration_completed", user_id=user.id, client_id=client_data.get("id"))

            # Send success message
            await update.message.reply_text(
                f"✅ Спасибо, {user.first_name}! Вы успешно авторизованы.\n\n"
                f"Отправьте фото букета или напишите ваш запрос!",
                reply_markup=ReplyKeyboardRemove()
            )

        except NetworkError as e:
            logger.error("registration_network_error", user_id=user.id, error=str(e))
            await update.message.reply_text(
                "😔 Не удалось подключиться к серверу.\n\n"
                "Проверьте подключение к интернету и попробуйте еще раз через /start",
                reply_markup=ReplyKeyboardRemove()
            )

        except Exception as e:
            logger.error("registration_unexpected_error", user_id=user.id, error=str(e), error_type=type(e).__name__)
            await update.message.reply_text(
                "😔 Произошла ошибка при регистрации.\n\n"
                "Попробуйте еще раз через /start или свяжитесь с поддержкой.",
                reply_markup=ReplyKeyboardRemove()
            )

    async def handle_photo(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle photo messages for AI-powered visual search."""
        user_id = update.effective_user.id

        # Check authorization first
        is_authorized = await self.check_authorization(user_id)
        if not is_authorized:
            await self._request_authorization(update)
            return

        # Generate request ID for tracing
        request_id = f"req_{uuid.uuid4().hex[:12]}"

        # Bind request context to structured logging
        bind_request_context(
            request_id=request_id,
            telegram_user_id=str(user_id),
            chat_id=update.message.chat.id
        )

        logger.info("photo_received",
                   photo_count=len(update.message.photo),
                   caption=update.message.caption,
                   username=update.effective_user.username)

        # Show typing indicator
        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            # Get largest photo (best quality)
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()

            # Use Telegram CDN URL directly
            image_url = photo_file.file_path

            logger.info("photo_url_obtained",
                       image_url=image_url,
                       file_size=photo.file_size)

            # Get caption text (if any)
            caption = update.message.caption or "Найди похожие букеты"

            # Get client data from backend to enrich context
            client_data = await self.mcp_client.get_telegram_client(
                telegram_user_id=str(user_id),
                shop_id=self.shop_id
            )

            # Call AI Agent Service with image_url
            response = await self.http_client.post(
                f"{self.ai_agent_url}/chat",
                json={
                    "message": caption,
                    "image_url": image_url,  # AI Agent will auto-trigger visual search
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
                headers={
                    "X-Request-ID": request_id
                },
                timeout=90.0  # Longer timeout for visual search
            )
            response.raise_for_status()
            result = response.json()

            logger.info("visual_search_response_received",
                       response_length=len(result.get("text", "")),
                       show_products=result.get("show_products"))

            response_text = result.get("text", "")

            # Handle empty AI response
            if not response_text or not response_text.strip():
                logger.warning("empty_visual_search_response", user_id=user_id)
                response_text = ("😔 Не удалось найти похожие букеты.\n\n"
                               "Попробуйте:\n"
                               "• Отправить другое фото\n"
                               "• Написать описание букета текстом")

            # Send response
            await update.message.reply_text(response_text)

        except httpx.HTTPStatusError as e:
            logger.error("visual_search_http_error",
                        user_id=user_id,
                        status_code=e.response.status_code,
                        error=str(e))
            await update.message.reply_text(
                f"😔 Ошибка сервера визуального поиска ({e.response.status_code}).\n\n"
                "Попробуйте еще раз или напишите текстом."
            )

        except Exception as e:
            logger.error("visual_search_unexpected_error",
                        user_id=user_id,
                        error=str(e),
                        error_type=type(e).__name__)
            await update.message.reply_text(
                "😔 Произошла ошибка при обработке фото.\n\n"
                "Попробуйте еще раз или напишите текстом."
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

        # Check authorization first
        is_authorized = await self.check_authorization(user_id)
        if not is_authorized:
            await self._request_authorization(update)
            return

        # Generate request ID for tracing
        request_id = f"req_{uuid.uuid4().hex[:12]}"

        # Bind request context to structured logging
        bind_request_context(
            request_id=request_id,
            telegram_user_id=str(user_id),
            chat_id=update.message.chat.id
        )

        logger.info("message_received",
                   message_length=len(message_text),
                   username=update.effective_user.username)

        # Show typing indicator
        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            # Get client data from backend to enrich context
            client_data = await self.mcp_client.get_telegram_client(
                telegram_user_id=str(user_id),
                shop_id=self.shop_id
            )

            # Call AI Agent Service via HTTP
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
                headers={
                    "X-Request-ID": request_id
                },
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()

            logger.info("ai_agent_response_received",
                       response_length=len(result.get("text", "")),
                       show_products=result.get("show_products"))

            response_text = result.get("text", "")
            show_products = bool(result.get("show_products"))
            product_ids = result.get("product_ids")

            # Handle empty AI response (safety check)
            if not response_text or not response_text.strip():
                logger.warning("empty_ai_response",
                             user_id=user_id,
                             show_products=show_products)
                response_text = ("😔 Извините, произошла ошибка обработки запроса.\n\n"
                               "Попробуйте:\n"
                               "• Переформулировать запрос\n"
                               "• Использовать /help для примеров")

            # If AI decided to show products
            if show_products:
                try:
                    # If AI provided filtered product IDs, use the new endpoint
                    if product_ids:
                        logger.info("using_filtered_products",
                                   product_count=len(product_ids),
                                   product_ids=product_ids,
                                   user_id=user_id)
                        products_response = await self.http_client.post(
                            f"{self.ai_agent_url}/products/by_ids",
                            json={"product_ids": product_ids},
                            timeout=30.0
                        )
                    else:
                        # Fallback to all products (legacy behavior)
                        logger.info("using_all_products", user_id=user_id)
                        products_response = await self.http_client.get(
                            f"{self.ai_agent_url}/products/{user_id}",
                            params={"channel": "telegram"},
                            timeout=30.0
                        )

                    if products_response.status_code == 200:
                        products_data = products_response.json()
                        products = products_data.get("products", [])

                        logger.info("products_fetched",
                                   product_count=len(products),
                                   user_id=user_id)

                        if products:
                            # Extract product images using formatter module (max 5)
                            images = extract_product_images(products, max_products=5)

                            if images:
                                logger.info("sending_product_photos",
                                           total_images=len(images),
                                           user_id=user_id)

                                # Send each product as a separate message with 0.5s delay
                                for img in images:
                                    await update.message.reply_photo(
                                        photo=img["url"],
                                        caption=img["caption"]
                                    )
                                    logger.info("sent_individual_photo",
                                               caption=img["caption"],
                                               user_id=user_id)
                                    # 0.5s delay to ensure proper order
                                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.error("product_fetch_failed", error=str(e))

            # Send text response (split if too long)
            if len(response_text) > 4096:
                for i in range(0, len(response_text), 4096):
                    await update.message.reply_text(response_text[i:i+4096])
            else:
                await update.message.reply_text(response_text)

            logger.info("message_handled_successfully")

        except Exception as e:
            logger.error("message_handling_failed",
                        error=str(e),
                        error_type=type(e).__name__)
            await update.message.reply_text(
                "😔 Извините, произошла ошибка. Попробуйте еще раз или используйте /help"
            )
        finally:
            # Clear request context for next message
            clear_request_context()

    async def post_init(self, application: Application):
        """Post-initialization hook."""
        # Initialize HTTP client for AI Agent calls
        self.http_client = httpx.AsyncClient(timeout=60.0)
        logger.info("bot_initialized_successfully",
                   shop_id=self.shop_id,
                   ai_agent_url=self.ai_agent_url)

    async def post_shutdown(self, application: Application):
        """Post-shutdown hook."""
        await self.mcp_client.close()
        if self.http_client:
            await self.http_client.aclose()
        logger.info("bot_shutdown_successfully")

    def run(self):
        """Run bot in polling mode (local development only)."""
        logger.info("starting_visual_search_ai_bot_polling_mode",
                   shop_id=self.shop_id)
        self.app.post_init = self.post_init
        self.app.post_shutdown = self.post_shutdown
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point."""
    print("🌸 Visual Search AI Bot - Starting...")
    print(f"📍 Shop ID: {os.getenv('DEFAULT_SHOP_ID', '17008')}")
    print(f"🤖 AI Agent: {os.getenv('AI_AGENT_URL', 'http://localhost:8002')}")
    print(f"🔧 MCP Server: {os.getenv('MCP_SERVER_URL', 'http://localhost:8000')}")
    print("")

    bot = VisualSearchAIBot()
    bot.run()


if __name__ == "__main__":
    main()
