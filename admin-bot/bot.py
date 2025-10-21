"""
Telegram Bot for Flower Shop with Claude AI integration.
Supports natural language ordering and catalog browsing.
"""
import os
import uuid
from typing import Optional, Dict
from dotenv import load_dotenv

from telegram import (
    Update,
    InputMediaPhoto,
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

from mcp_client import create_mcp_client, NetworkError
from formatters import extract_product_images, chunk_list
import httpx
import asyncio
from aiohttp import web

# Load environment variables
load_dotenv()

# Configure structured logging
from logging_config import configure_logging, get_logger, bind_request_context, clear_request_context

configure_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)
logger.info("telegram_bot_starting", shop_id=os.getenv('DEFAULT_SHOP_ID', '8'))


class FlowerShopBot:
    """Main Telegram bot class."""

    def __init__(self):
        # Load configuration
        # Use production token if available, otherwise fall back to test token for local development
        self.telegram_token = os.getenv("TELEGRAM_TOKEN") or os.getenv("TEST_TELEGRAM_TOKEN")
        if not self.telegram_token:
            raise ValueError("TELEGRAM_TOKEN or TEST_TELEGRAM_TOKEN must be set in environment")

        self.mcp_server_url = os.getenv("MCP_SERVER_URL")
        self.shop_id = int(os.getenv("DEFAULT_SHOP_ID", "8"))
        self.webhook_url = os.getenv("WEBHOOK_URL")
        self.webhook_port = int(os.getenv("WEBHOOK_PORT", "8080"))

        # AI Agent Service URL
        self.ai_agent_url = os.getenv("AI_AGENT_URL", "http://localhost:8000")

        # Initialize MCP client (still needed for authorization checks)
        self.mcp_client = create_mcp_client(self.mcp_server_url)

        # HTTP client for AI Agent calls (will be initialized in post_init)
        self.http_client: Optional[httpx.AsyncClient] = None

        # Create application
        self.app = Application.builder().token(self.telegram_token).build()

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register all command and message handlers."""
        # Commands
        self.app.add_handler(CommandHandler("start", self.start_command))

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
            logger.info(f"authorization_check", user_id=user_id, shop_id=self.shop_id)
            client = await self.mcp_client.get_telegram_client(
                telegram_user_id=str(user_id),
                shop_id=self.shop_id
            )
            is_authorized = client is not None
            logger.info(f"authorization_result", user_id=user_id, is_authorized=is_authorized)
            return is_authorized

        except NetworkError as e:
            logger.error(f"authorization_network_error", user_id=user_id, error=str(e))
            return False

        except Exception as e:
            logger.error(f"authorization_unexpected_error", user_id=user_id, error=str(e))
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
            "📱 Для полного доступа к функциям бота необходимо поделиться контактом.\n\n"
            "Это нужно для:\n"
            "• Оформления заказов\n"
            "• Отслеживания доставки\n"
            "• Сохранения ваших данных\n\n"
            "Нажмите кнопку ниже, чтобы авторизоваться:",
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

        # User is already authorized - no need for welcome message
        # AI will handle the conversation


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
            logger.info(f"registration_started", user_id=user.id, shop_id=self.shop_id)

            # Register client via backend API (with MCP fallback)
            client_data = await self.mcp_client.register_telegram_client(
                telegram_user_id=str(user.id),
                phone=contact.phone_number,
                customer_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or "Клиент",
                shop_id=self.shop_id,
                telegram_username=user.username,
                telegram_first_name=user.first_name
            )

            # Verify registration was successful (must have 'id' field)
            if not client_data or "id" not in client_data:
                raise Exception("Registration returned invalid data (missing 'id' field)")

            logger.info(f"registration_completed", user_id=user.id, client_id=client_data.get("id"))

            # Send minimal success message - AI will handle conversation
            await update.message.reply_text(
                f"✅ Спасибо, {user.first_name}! Вы успешно авторизованы.",
                reply_markup=ReplyKeyboardRemove()
            )

        except NetworkError as e:
            logger.error(f"registration_network_error", user_id=user.id, error=str(e))
            await update.message.reply_text(
                "😔 Не удалось подключиться к серверу.\n\n"
                "Проверьте подключение к интернету и попробуйте еще раз через /start",
                reply_markup=ReplyKeyboardRemove()
            )

        except Exception as e:
            logger.error(f"registration_unexpected_error", user_id=user.id, error=str(e), error_type=type(e).__name__)
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
        """Handle photo messages for visual search."""
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
                    "image_url": image_url,  # Add image URL for visual search
                    "user_id": str(user_id),
                    "channel": "telegram",
                    "context": {
                        "username": update.effective_user.username,
                        "first_name": update.effective_user.first_name,
                        "phone": client_data.get("phone") if client_data else None,
                        "customer_name": client_data.get("customerName") if client_data else None,
                        "telegram_id": str(user_id)
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

            # Call AI Agent Service via HTTP with request_id in headers
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
                        "telegram_id": str(user_id)
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
            product_ids = result.get("product_ids")  # Extract filtered product IDs if present

            # Handle empty AI response (safety check)
            if not response_text or not response_text.strip():
                logger.warning("empty_ai_response",
                             user_id=user_id,
                             show_products=show_products)
                response_text = ("😔 Извините, произошла ошибка обработки запроса.\n\n"
                               "Попробуйте:\n"
                               "• Переформулировать запрос\n"
                               "• Связаться с поддержкой через /help")

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
                    logger.error(f"product_fetch_failed", error=str(e))

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
        logger.info("Bot initialized successfully")

    async def post_shutdown(self, application: Application):
        """Post-shutdown hook."""
        await self.mcp_client.close()
        if self.http_client:
            await self.http_client.aclose()
        logger.info("Bot shut down successfully")

    def run_polling(self):
        """Run bot in polling mode (for local development)."""
        logger.info("Starting bot in polling mode...")
        self.app.post_init = self.post_init
        self.app.post_shutdown = self.post_shutdown
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

    async def health_check(self, request):
        """Health check endpoint for Railway monitoring."""
        return web.Response(
            text='{"status":"ok","service":"telegram-bot"}',
            content_type="application/json",
            status=200
        )

    def run_webhook(self):
        """Run bot in webhook mode (for Railway deployment)."""
        logger.info(f"Starting bot in webhook mode on port {self.webhook_port}...")
        self.app.post_init = self.post_init
        self.app.post_shutdown = self.post_shutdown

        # Create custom webhook with health check endpoint
        async def custom_webhook():
            # Start the telegram bot webhook
            await self.app.initialize()
            await self.app.start()
            # Manually call post_init to initialize HTTP client in webhook mode
            # (In polling mode, this is called automatically by Application.run_polling())
            await self.post_init(self.app)

            # Create aiohttp web server with health check
            web_app = web.Application()
            web_app.router.add_get("/health", self.health_check)

            # Add telegram webhook endpoint
            from telegram.ext import Updater
            async def telegram_webhook(request):
                """Handle incoming telegram updates."""
                data = await request.json()
                update = Update.de_json(data, self.app.bot)
                await self.app.update_queue.put(update)
                return web.Response(status=200)

            web_app.router.add_post("/webhook", telegram_webhook)

            # Start web server
            runner = web.AppRunner(web_app)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", self.webhook_port)
            await site.start()

            # Set webhook
            await self.app.bot.set_webhook(
                url=f"{self.webhook_url}/webhook",
                allowed_updates=Update.ALL_TYPES
            )

            logger.info(f"✅ Webhook server running on port {self.webhook_port}")
            logger.info(f"✅ Health check available at /health")

            # Keep running
            await asyncio.Event().wait()

        # Run the custom webhook
        asyncio.run(custom_webhook())


def main():
    """Main entry point."""
    bot = FlowerShopBot()

    # Use webhook mode if WEBHOOK_URL is set, otherwise polling
    if os.getenv("WEBHOOK_URL"):
        bot.run_webhook()
    else:
        bot.run_polling()


if __name__ == "__main__":
    main()
