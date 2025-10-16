"""
Telegram Bot for Flower Shop with Claude AI integration.
Supports natural language ordering and catalog browsing.
"""
import os
import uuid
import time
from typing import Optional, Dict, Tuple
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from mcp_client import create_mcp_client, NetworkError
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

        # Authorization cache: user_id -> (is_authorized, timestamp)
        self.auth_cache: Dict[int, Tuple[bool, float]] = {}
        self.auth_cache_ttl = 300  # 5 minutes TTL

        # Client data cache: user_id -> (client_data, timestamp)
        self.client_cache: Dict[int, Tuple[Optional[Dict], float]] = {}
        self.client_cache_ttl = 300  # 5 minutes TTL

        # Create application
        self.app = Application.builder().token(self.telegram_token).build()

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register all command and message handlers."""
        # Commands
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("catalog", self.catalog_command))
        self.app.add_handler(CommandHandler("myorders", self.myorders_command))
        self.app.add_handler(CommandHandler("clear", self.clear_command))

        # Contact sharing (for authorization)
        self.app.add_handler(MessageHandler(filters.CONTACT, self.handle_contact))

        # Callback queries (inline keyboard buttons)
        self.app.add_handler(CallbackQueryHandler(self.button_callback))

        # Text messages (AI conversation)
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    async def check_authorization(self, user_id: int) -> bool:
        """
        Check if user is authorized (has shared contact) with caching and TTL.
        Returns True if authorized, False if not found or error occurs.
        """
        # Check cache first
        if user_id in self.auth_cache:
            is_authorized, timestamp = self.auth_cache[user_id]
            if time.time() - timestamp < self.auth_cache_ttl:
                logger.info(f"authorization_cache_hit", user_id=user_id)
                return is_authorized

        try:
            logger.info(f"authorization_check", user_id=user_id, shop_id=self.shop_id)
            client = await self.mcp_client.get_telegram_client(
                telegram_user_id=str(user_id),
                shop_id=self.shop_id
            )
            is_authorized = client is not None

            # Update cache only on successful check
            self.auth_cache[user_id] = (is_authorized, time.time())
            logger.info(f"authorization_result", user_id=user_id, is_authorized=is_authorized)
            return is_authorized

        except NetworkError as e:
            logger.error(f"authorization_network_error", user_id=user_id, error=str(e))
            # Return False on network errors - user should attempt authorization
            # This prevents auto-authorizing everyone when backend is down
            return False

        except Exception as e:
            logger.error(f"authorization_unexpected_error", user_id=user_id, error=str(e))
            # Return False on unexpected errors too - safer to require authorization
            return False

    async def get_client_data_cached(self, user_id: int) -> Optional[Dict]:
        """Get client data from backend with caching and TTL."""
        # Check cache first
        if user_id in self.client_cache:
            client_data, timestamp = self.client_cache[user_id]
            if time.time() - timestamp < self.client_cache_ttl:
                logger.info(f"client_data_cache_hit", user_id=user_id)
                return client_data

        try:
            logger.info(f"client_data_fetch", user_id=user_id)
            client_data = await self.mcp_client.get_telegram_client(
                telegram_user_id=str(user_id),
                shop_id=self.shop_id
            )
            # Update cache
            self.client_cache[user_id] = (client_data, time.time())
            logger.info(f"client_data_cached", user_id=user_id, has_phone=bool(client_data and client_data.get("phone")))
            return client_data

        except Exception as e:
            logger.error(f"client_data_fetch_failed", user_id=user_id, error=str(e))
            return None

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

        # User is authorized - show normal welcome
        welcome_text = f"""👋 Здравствуйте, {user.first_name}!

Я AI-помощник цветочного магазина. Помогу вам:

🌹 Выбрать букет из каталога
🛒 Оформить заказ на доставку
📦 Отследить ваш заказ
⏰ Узнать режим работы

Просто напишите мне, что вам нужно, например:
• "Покажи букеты до 10000 тенге"
• "Хочу заказать розы на завтра"
• "Где мой заказ?"

Или используйте команды:
/catalog - Посмотреть каталог
/myorders - Мои заказы
/help - Помощь
"""
        await update.message.reply_text(
            welcome_text,
            reply_markup=ReplyKeyboardRemove()
        )

    async def help_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /help command."""
        help_text = """📖 **Как пользоваться ботом:**

**Команды:**
/start - Начать работу с ботом
/catalog - Показать каталог цветов
/myorders - Отследить мои заказы
/clear - Очистить историю диалога
/help - Показать эту справку

**Возможности:**
• Поиск букетов по описанию, цене, типу
• Оформление заказов с доставкой
• Отслеживание статуса заказов
• Консультация по ассортименту

**Примеры запросов:**
• "Покажи готовые букеты"
• "Букет из роз до 15000 тенге"
• "Хочу заказать букет на день рождения завтра в 15:00"
• "Какой статус моего заказа?"

Просто пишите как обычному человеку - я пойму! 😊
"""
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def catalog_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /catalog command."""
        # Check authorization
        is_authorized = await self.check_authorization(update.effective_user.id)
        if not is_authorized:
            await self._request_authorization(update)
            return

        keyboard = [
            [
                InlineKeyboardButton("🌹 Готовые букеты", callback_data="catalog_ready"),
                InlineKeyboardButton("✨ На заказ", callback_data="catalog_custom")
            ],
            [
                InlineKeyboardButton("🔄 Подписки", callback_data="catalog_subscription"),
                InlineKeyboardButton("🔍 Поиск", callback_data="catalog_search")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Выберите категорию:",
            reply_markup=reply_markup
        )

    async def myorders_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /myorders command."""
        # Check authorization
        is_authorized = await self.check_authorization(update.effective_user.id)
        if not is_authorized:
            await update.message.reply_text(
                "📱 Сначала необходимо авторизоваться.\n"
                "Используйте /start для регистрации."
            )
            return

        # Get client data
        client = await self.mcp_client.get_telegram_client(
            telegram_user_id=str(update.effective_user.id),
            shop_id=self.shop_id
        )

        if client and client.get("phone"):
            # Use AI Agent to track orders by saved phone number
            phone = client["phone"]
            prompt = f"Отследи мои заказы по номеру {phone}"

            await update.message.chat.send_action(ChatAction.TYPING)

            # Call AI Agent Service
            try:
                response = await self.http_client.post(
                    f"{self.ai_agent_url}/chat",
                    json={
                        "message": prompt,
                        "user_id": str(update.effective_user.id),
                        "channel": "telegram"
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                await update.message.reply_text(result["text"])
            except Exception as e:
                logger.error(f"myorders_fetch_failed", error=str(e))
                await update.message.reply_text("Ошибка при получении заказов. Попробуйте еще раз.")
        else:
            await update.message.reply_text(
                "Ошибка получения номера телефона. Попробуйте /start заново."
            )

    async def clear_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /clear command - clear conversation history."""
        user_id = update.effective_user.id

        try:
            # Call AI Agent Service to clear history
            response = await self.http_client.delete(
                f"{self.ai_agent_url}/conversations/{user_id}",
                params={"channel": "telegram"},
                timeout=30.0
            )
            response.raise_for_status()

            await update.message.reply_text(
                "✅ История диалога очищена. Можем начать заново!"
            )
        except Exception as e:
            logger.error(f"clear_history_failed", error=str(e))
            await update.message.reply_text(
                "😔 Произошла ошибка при очистке истории."
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

            # Update authorization cache immediately after successful registration
            self.auth_cache[user.id] = (True, time.time())
            logger.info(f"auth_cache_updated", user_id=user.id)

            # Update client data cache too
            self.client_cache[user.id] = (client_data, time.time())
            logger.info(f"client_cache_updated", user_id=user.id)

            # Send success message
            welcome_text = f"""✅ Спасибо, {user.first_name}! Вы успешно авторизованы.

Теперь вы можете:
🌹 Выбрать букет из каталога
🛒 Оформить заказ на доставку
📦 Отследить ваш заказ

Просто напишите мне, что вам нужно, или используйте:
/catalog - Каталог
/myorders - Мои заказы
/help - Помощь"""

            await update.message.reply_text(
                welcome_text,
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

    async def button_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle inline keyboard button presses."""
        query = update.callback_query
        await query.answer()

        callback_data = query.data

        if callback_data.startswith("catalog_"):
            product_type = callback_data.replace("catalog_", "")

            if product_type == "search":
                await query.edit_message_text(
                    "🔍 Напишите, что ищете:\n\n"
                    "Например: \"розы\", \"букет невесты\", \"цветы до 10000 тенге\""
                )
            else:
                # Check authorization first
                is_authorized = await self.check_authorization(update.effective_user.id)
                if not is_authorized:
                    await query.edit_message_text(
                        "📱 Для использования каталога необходимо авторизоваться.\n\n"
                        "Используйте /start для регистрации."
                    )
                    return

                # Trigger AI to list products of this type
                user_id = update.effective_user.id
                prompt = f"Покажи мне товары типа {product_type}"

                # Process with AI Agent Service
                try:
                    response = await self.http_client.post(
                        f"{self.ai_agent_url}/chat",
                        json={
                            "message": prompt,
                            "user_id": str(user_id),
                            "channel": "telegram"
                        },
                        timeout=60.0
                    )
                    response.raise_for_status()
                    result = response.json()
                    await query.edit_message_text(result["text"])
                except Exception as e:
                    logger.error(f"catalog_fetch_failed", error=str(e))
                    await query.edit_message_text("Ошибка при загрузке каталога. Попробуйте еще раз.")

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
            client_data = await self.get_client_data_cached(user_id)

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

            response_text = result["text"]
            show_products = bool(result.get("show_products"))

            if show_products:
                try:
                    products_response = await self.http_client.get(
                        f"{self.ai_agent_url}/products/{user_id}",
                        params={"channel": "telegram"},
                        timeout=30.0
                    )
                    if products_response.status_code == 200:
                        products_data = products_response.json()
                        products = products_data.get("products", [])

                        if products:
                            images = []
                            for product in products[:10]:  # Max 10 images
                                product_images = product.get("images") or []
                                if product_images:
                                    price = product.get("price", 0)
                                    price_tenge = int(price) // 100 if isinstance(price, (int, float)) else 0
                                    images.append({
                                        "url": product_images[0]["url"],
                                        "caption": f"{product.get('name', 'Товар')} - {price_tenge:,} ₸".replace(',', ' ')
                                    })

                            if images:
                                for i in range(0, len(images), 10):
                                    batch = images[i:i+10]
                                    if len(batch) == 1:
                                        await update.message.reply_photo(
                                            photo=batch[0]["url"],
                                            caption=batch[0]["caption"]
                                        )
                                    else:
                                        media_group = [
                                            InputMediaPhoto(
                                                media=img["url"],
                                                caption=img["caption"]
                                            )
                                            for img in batch
                                        ]
                                        await update.message.reply_media_group(media=media_group)
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
