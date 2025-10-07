"""
Telegram Bot for Flower Shop with Claude AI integration.
Supports natural language ordering and catalog browsing.
"""
import os
import logging
from typing import Optional
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
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from mcp_client import create_mcp_client
import httpx


# Load environment variables
load_dotenv()

# Configure logging with file output
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"bot_{os.getenv('DEFAULT_SHOP_ID', '8')}.log")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"📁 Logging to: {log_file}")


class FlowerShopBot:
    """Main Telegram bot class."""

    def __init__(self):
        # Load configuration
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        self.mcp_server_url = os.getenv("MCP_SERVER_URL")
        self.shop_id = int(os.getenv("DEFAULT_SHOP_ID", "8"))
        self.webhook_url = os.getenv("WEBHOOK_URL")
        self.webhook_port = int(os.getenv("WEBHOOK_PORT", "8080"))

        # AI Agent Service URL
        self.ai_agent_url = os.getenv("AI_AGENT_URL", "http://localhost:8000")

        # Initialize MCP client (still needed for authorization checks)
        self.mcp_client = create_mcp_client(self.mcp_server_url)

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
        """Check if user is authorized (has shared contact)."""
        try:
            client = await self.mcp_client.get_telegram_client(
                telegram_user_id=str(user_id),
                shop_id=self.shop_id
            )
            return client is not None
        except Exception as e:
            logger.error(f"Error checking authorization: {e}")
            return False

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
            # Request contact for authorization
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
                f"👋 Здравствуйте, {user.first_name}!\n\n"
                "Для использования бота необходимо поделиться вашим контактом.\n"
                "Это нужно для:\n"
                "• Оформления заказов\n"
                "• Отслеживания доставки\n"
                "• Связи с вами по важным вопросам\n\n"
                "Нажмите кнопку ниже, чтобы продолжить:",
                reply_markup=keyboard
            )
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

            await update.message.chat.send_action("typing")

            # Call AI Agent Service
            async with httpx.AsyncClient(timeout=60.0) as http_client:
                response = await http_client.post(
                    f"{self.ai_agent_url}/chat",
                    json={
                        "message": prompt,
                        "user_id": str(update.effective_user.id),
                        "channel": "telegram"
                    }
                )
                response.raise_for_status()
                result = response.json()

            await update.message.reply_text(result["text"])
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
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ai_agent_url}/clear-history/{user_id}",
                    params={"channel": "telegram"}
                )
                response.raise_for_status()

            await update.message.reply_text(
                "✅ История диалога очищена. Можем начать заново!"
            )
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
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
            # Register client via MCP
            client_data = await self.mcp_client.register_telegram_client(
                telegram_user_id=str(user.id),
                phone=contact.phone_number,
                customer_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or "Клиент",
                shop_id=self.shop_id,
                telegram_username=user.username,
                telegram_first_name=user.first_name
            )

            logger.info(f"User {user.id} registered with phone {contact.phone_number}")

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

        except Exception as e:
            logger.error(f"Error registering client: {e}")
            await update.message.reply_text(
                "😔 Произошла ошибка при регистрации. Попробуйте еще раз или напишите /start",
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
                # Trigger AI to list products of this type
                user_id = update.effective_user.id
                prompt = f"Покажи мне товары типа {product_type}"

                # Process with AI Agent Service
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.ai_agent_url}/chat",
                        json={
                            "message": prompt,
                            "user_id": str(user_id),
                            "channel": "telegram"
                        }
                    )
                    response.raise_for_status()
                    result = response.json()

                await query.edit_message_text(result["text"])

    async def handle_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle text messages via AI Agent Service."""
        user_id = update.effective_user.id
        message_text = update.message.text

        # Show typing indicator
        await update.message.chat.send_action("typing")

        try:
            # Call AI Agent Service via HTTP
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.ai_agent_url}/chat",
                    json={
                        "message": message_text,
                        "user_id": str(user_id),
                        "channel": "telegram",
                        "context": {
                            "username": update.effective_user.username,
                            "first_name": update.effective_user.first_name
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()

            response_text = result["text"]
            show_products = bool(result.get("show_products"))

            if show_products:
                async with httpx.AsyncClient() as client:
                    products_response = await client.get(
                        f"{self.ai_agent_url}/products/{user_id}",
                        params={"channel": "telegram"}
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
                                        "url": product_images[0],
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

            # Send text response (split if too long)
            if len(response_text) > 4096:
                for i in range(0, len(response_text), 4096):
                    await update.message.reply_text(response_text[i:i+4096])
            else:
                await update.message.reply_text(response_text)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(
                "😔 Извините, произошла ошибка. Попробуйте еще раз или используйте /help"
            )

    async def post_init(self, application: Application):
        """Post-initialization hook."""
        logger.info("Bot initialized successfully")

    async def post_shutdown(self, application: Application):
        """Post-shutdown hook."""
        await self.mcp_client.close()
        logger.info("Bot shut down successfully")

    def run_polling(self):
        """Run bot in polling mode (for local development)."""
        logger.info("Starting bot in polling mode...")
        self.app.post_init = self.post_init
        self.app.post_shutdown = self.post_shutdown
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

    def run_webhook(self):
        """Run bot in webhook mode (for Railway deployment)."""
        logger.info(f"Starting bot in webhook mode on port {self.webhook_port}...")
        self.app.post_init = self.post_init
        self.app.post_shutdown = self.post_shutdown

        self.app.run_webhook(
            listen="0.0.0.0",
            port=self.webhook_port,
            url_path="webhook",
            webhook_url=f"{self.webhook_url}/webhook",
            allowed_updates=Update.ALL_TYPES
        )


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
