"""
Telegram Bot for Flower Shop with Claude AI integration.
Supports natural language ordering and catalog browsing.
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from mcp_client import create_mcp_client
from ai_handler import AIHandler


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class FlowerShopBot:
    """Main Telegram bot class."""

    def __init__(self):
        # Load configuration
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        self.mcp_server_url = os.getenv("MCP_SERVER_URL")
        self.shop_id = int(os.getenv("DEFAULT_SHOP_ID", "8"))
        self.webhook_url = os.getenv("WEBHOOK_URL")
        self.webhook_port = int(os.getenv("WEBHOOK_PORT", "8080"))

        # Initialize MCP client
        self.mcp_client = create_mcp_client(self.mcp_server_url)

        # Initialize AI handler
        self.ai_handler = AIHandler(
            mcp_client=self.mcp_client,
            shop_id=self.shop_id
        )

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

        # Callback queries (inline keyboard buttons)
        self.app.add_handler(CallbackQueryHandler(self.button_callback))

        # Text messages (AI conversation)
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    async def start_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /start command."""
        user = update.effective_user
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
        await update.message.reply_text(welcome_text)

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
        # Ask user for phone number to track orders
        await update.message.reply_text(
            "📱 Укажите номер телефона, который использовали при заказе:\n\n"
            "Например: +77011234567"
        )
        # Store state to expect phone number
        context.user_data['expecting_phone'] = True

    async def clear_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /clear command - clear conversation history."""
        user_id = update.effective_user.id
        self.ai_handler.clear_conversation(user_id)
        await update.message.reply_text(
            "✅ История диалога очищена. Можем начать заново!"
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

                # Process with AI
                response = await self.ai_handler.process_message(user_id, prompt)
                await query.edit_message_text(response)

    async def handle_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle text messages via AI."""
        user_id = update.effective_user.id
        message_text = update.message.text

        # Check if we're expecting phone number for order tracking
        if context.user_data.get('expecting_phone'):
            context.user_data['expecting_phone'] = False
            prompt = f"Отследи заказы по номеру телефона: {message_text}"
        else:
            prompt = message_text

        # Show typing indicator
        await update.message.chat.send_action("typing")

        try:
            # Process message with AI
            response = await self.ai_handler.process_message(user_id, prompt)

            # Send response (split if too long)
            if len(response) > 4096:
                # Split into chunks
                for i in range(0, len(response), 4096):
                    await update.message.reply_text(response[i:i+4096])
            else:
                await update.message.reply_text(response)

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
