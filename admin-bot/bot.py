"""
Admin Bot for Flower Shop Staff
Telegram Bot for floristi

sts/managers to manage products, orders, and inventory.

Supports multiple environments:
- Production (shop_id=17008, Bitrix): ENVIRONMENT=production
- Development (shop_id=8, Railway PostgreSQL): ENVIRONMENT=development

Architecture:
- Direct MCP integration for admin operations
- Multi-environment support
- Webhook mode for production, polling mode for development
"""
import os
import uuid
from typing import Optional
from dotenv import load_dotenv

# Load environment-specific .env file
environment = os.getenv('ENVIRONMENT', 'development')
env_file = f'.env.{environment}'

# Try to load environment-specific file, fall back to default .env
if os.path.exists(env_file):
    load_dotenv(env_file)
    print(f"✅ Loaded {env_file}")
else:
    load_dotenv()
    print(f"⚠️  {env_file} not found, using default .env")

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

# Import shared modules from shared-telegram directory
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared-telegram'))

from mcp_client import create_mcp_client, NetworkError
from formatters import extract_product_images
from logging_config import configure_logging, get_logger, bind_request_context, clear_request_context

import httpx
import asyncio

# Import admin handlers
from admin_handlers import (
    handle_list_orders,
    handle_order_details,
    handle_change_order_status,
    handle_add_product_start,
    handle_warehouse_status,
)

configure_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)
logger.info("admin_bot_starting",
           environment=environment,
           shop_id=os.getenv('DEFAULT_SHOP_ID'),
           mcp_url=os.getenv('MCP_SERVER_URL'))


# Conversation states for multi-step flows
ADD_PRODUCT_PHOTO, ADD_PRODUCT_DETAILS = range(2)


class AdminBot:
    """
    Admin Bot for Flower Shop Staff.

    Key features:
    - Manage orders (view, update status)
    - Publish products (add, edit, disable)
    - Manage inventory (warehouse operations)
    - Multi-environment support (production/development)
    """

    def __init__(self):
        # Load configuration from environment variables
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        if not self.telegram_token:
            raise ValueError("TELEGRAM_TOKEN must be set in .env file")

        self.mcp_server_url = os.getenv("MCP_SERVER_URL")
        if not self.mcp_server_url:
            raise ValueError("MCP_SERVER_URL must be set in .env file")

        self.ai_agent_url = os.getenv("AI_AGENT_URL")
        if not self.ai_agent_url:
            raise ValueError("AI_AGENT_URL must be set in .env file")

        self.shop_id = int(os.getenv("DEFAULT_SHOP_ID", "8"))
        self.webhook_url = os.getenv("WEBHOOK_URL")  # Optional: if set, uses webhook mode

        logger.info("admin_bot_configuration",
                   environment=environment,
                   shop_id=self.shop_id,
                   ai_agent_url=self.ai_agent_url,
                   mcp_server_url=self.mcp_server_url,
                   webhook_mode=bool(self.webhook_url))

        # Initialize MCP client
        self.mcp_client = create_mcp_client(self.mcp_server_url)

        # HTTP client for AI Agent calls (initialized in post_init)
        self.http_client: Optional[httpx.AsyncClient] = None

        # Create application
        self.app = Application.builder().token(self.telegram_token).build()

        # Initialize post_init handlers
        self.app.post_init = self.post_init
        self.app.post_shutdown = self.post_shutdown

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register all command and message handlers."""
        # Basic commands
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))

        # Contact sharing (for authorization)
        self.app.add_handler(MessageHandler(filters.CONTACT, self.handle_contact))

        # Text messages (AI conversation) - natural language admin interface
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    async def check_admin_authorization(self, user_id: int) -> tuple[bool, Optional[dict]]:
        """
        Check if user is authorized admin/staff member.
        Returns: (is_authorized, client_data)
        """
        try:
            logger.info("admin_authorization_check", user_id=user_id, shop_id=self.shop_id)
            client = await self.mcp_client.get_telegram_client(
                telegram_user_id=str(user_id),
                shop_id=self.shop_id
            )

            if not client:
                logger.info("admin_not_found", user_id=user_id)
                return False, None

            # TODO: Add role check when roles are implemented
            # For now, anyone registered is considered authorized
            # Future: role = client.get('role')
            # return role in ['DIRECTOR', 'MANAGER', 'WORKER'], client

            logger.info("admin_authorized", user_id=user_id, client_id=client.get('id'))
            return True, client

        except NetworkError as e:
            logger.error("admin_auth_network_error", user_id=user_id, error=str(e))
            return False, None

        except Exception as e:
            logger.error("admin_auth_unexpected_error", user_id=user_id, error=str(e))
            return False, None

    async def _request_authorization(self, update: Update):
        """Request staff authorization via contact sharing."""
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
            "🔒 Админ-бот для сотрудников\n\n"
            "Для доступа необходимо авторизоваться.\n\n"
            "Возможности:\n"
            "• 📦 Управление заказами\n"
            "• ➕ Публикация товаров\n"
            "• 📊 Управление складом\n\n"
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
        is_authorized, client_data = await self.check_admin_authorization(user.id)

        if not is_authorized:
            await self._request_authorization(update)
            return

        # User is authorized - show admin menu
        await update.message.reply_text(
            f"✅ Добро пожаловать, {user.first_name}!\n\n"
            f"**Админ-панель** ({environment})\n"
            f"Shop ID: {self.shop_id}\n\n"
            f"Используйте /help для списка команд",
            parse_mode="Markdown"
        )

    async def help_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /help command."""
        help_text = """
🛠️ **Админ-бот для сотрудников**

💬 **Просто пишите на естественном языке!**

Я понимаю ваши запросы и помогу управлять магазином:

**Примеры запросов:**
📦 "покажи заказы за сегодня"
📦 "покажи заказ №234"
✅ "переведи заказ 234 в статус IN_PRODUCTION"

🌹 "сколько роз на складе?"
📊 "покажи остатки на складе"

➕ "добавь новый товар"
📝 "покажи список всех товаров"

**Статусы заказов:**
NEW → PAID → ACCEPTED → IN_PRODUCTION → READY → IN_DELIVERY → DELIVERED

**Окружение:** {environment}
**Shop ID:** {shop_id}
        """.format(environment=environment, shop_id=self.shop_id)
        await update.message.reply_text(help_text, parse_mode="Markdown")

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
            logger.info("admin_registration_started", user_id=user.id, shop_id=self.shop_id)

            # Register staff member via MCP
            client_data = await self.mcp_client.register_telegram_client(
                telegram_user_id=str(user.id),
                phone=contact.phone_number,
                customer_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or "Staff",
                shop_id=self.shop_id,
                telegram_username=user.username,
                telegram_first_name=user.first_name
            )

            # Verify registration
            if not client_data or "id" not in client_data:
                raise Exception("Registration returned invalid data")

            logger.info("admin_registration_completed", user_id=user.id, client_id=client_data.get("id"))

            await update.message.reply_text(
                f"✅ Авторизация успешна, {user.first_name}!\n\n"
                f"Используйте /help для списка команд",
                reply_markup=ReplyKeyboardRemove()
            )

        except NetworkError as e:
            logger.error("admin_registration_network_error", user_id=user.id, error=str(e))
            await update.message.reply_text(
                "😔 Не удалось подключиться к серверу.\n\n"
                "Попробуйте еще раз через /start",
                reply_markup=ReplyKeyboardRemove()
            )

        except Exception as e:
            logger.error("admin_registration_unexpected_error", user_id=user.id, error=str(e))
            await update.message.reply_text(
                "😔 Произошла ошибка при регистрации.\n\n"
                "Попробуйте еще раз через /start",
                reply_markup=ReplyKeyboardRemove()
            )

    async def handle_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle text messages via AI Agent Service."""
        user_id = update.effective_user.id
        message_text = update.message.text

        # Check admin authorization
        is_authorized, client_data = await self.check_admin_authorization(user_id)
        if not is_authorized:
            await self._request_authorization(update)
            return

        request_id = f"req_{uuid.uuid4().hex[:12]}"
        bind_request_context(request_id=request_id, telegram_user_id=str(user_id), chat_id=update.message.chat.id)

        logger.info("admin_message_received", message_length=len(message_text))

        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            # Call AI Agent with admin context
            response = await self.http_client.post(
                f"{self.ai_agent_url}/chat",
                json={
                    "message": message_text,
                    "user_id": str(user_id),
                    "channel": "telegram",
                    "context": {
                        "role": "admin",  # Critical: triggers admin-specific system prompt
                        "username": update.effective_user.username,
                        "first_name": update.effective_user.first_name,
                        "phone": client_data.get("phone") if client_data else None,
                        "customer_name": client_data.get("customerName") if client_data else None,
                        "telegram_id": str(user_id),
                        "shop_id": self.shop_id,
                        "environment": environment
                    }
                },
                headers={"X-Request-ID": request_id},
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()

            response_text = result.get("text", "")
            if response_text:
                await update.message.reply_text(response_text)
            else:
                logger.warning("empty_ai_response", request_id=request_id)
                await update.message.reply_text("🤔 Не получил ответ от AI. Попробуйте еще раз.")

        except httpx.TimeoutException:
            logger.error("ai_agent_timeout", request_id=request_id)
            await update.message.reply_text("⏱️ Превышено время ожидания. Попробуйте еще раз.")

        except httpx.HTTPStatusError as e:
            logger.error("ai_agent_http_error", status_code=e.response.status_code, request_id=request_id)
            await update.message.reply_text("😔 Ошибка сервера AI. Попробуйте позже.")

        except Exception as e:
            logger.error("ai_agent_error", error=str(e), request_id=request_id)
            await update.message.reply_text("😔 Произошла ошибка. Попробуйте еще раз.")

        finally:
            clear_request_context()

    async def orders_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /orders command - list recent orders."""
        user_id = update.effective_user.id

        # Check authorization
        is_authorized, _ = await self.check_admin_authorization(user_id)
        if not is_authorized:
            await self._request_authorization(update)
            return

        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            await handle_list_orders(update, context, self.mcp_client, self.shop_id)
        except Exception as e:
            logger.error("orders_command_failed", error=str(e))
            await update.message.reply_text("😔 Ошибка при загрузке заказов")

    async def order_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /order <id> command - show order details."""
        user_id = update.effective_user.id

        # Check authorization
        is_authorized, _ = await self.check_admin_authorization(user_id)
        if not is_authorized:
            await self._request_authorization(update)
            return

        # Get order ID from command
        if not context.args or not context.args[0].isdigit():
            await update.message.reply_text("Использование: /order <номер_заказа>")
            return

        order_id = int(context.args[0])

        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            await handle_order_details(update, context, self.mcp_client, self.shop_id, order_id)
        except Exception as e:
            logger.error("order_command_failed", error=str(e), order_id=order_id)
            await update.message.reply_text(f"😔 Ошибка при загрузке заказа #{order_id}")

    async def status_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /status <id> <new_status> command."""
        user_id = update.effective_user.id

        # Check authorization
        is_authorized, _ = await self.check_admin_authorization(user_id)
        if not is_authorized:
            await self._request_authorization(update)
            return

        # Parse arguments
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "Использование: /status <номер_заказа> <статус>\n\n"
                "Доступные статусы:\n"
                "NEW, PAID, ACCEPTED, IN_PRODUCTION, READY, IN_DELIVERY, DELIVERED"
            )
            return

        order_id = int(context.args[0])
        new_status = context.args[1].upper()

        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            await handle_change_order_status(update, context, self.mcp_client, self.shop_id, order_id, new_status)
        except Exception as e:
            logger.error("status_command_failed", error=str(e), order_id=order_id, new_status=new_status)
            await update.message.reply_text(f"😔 Ошибка при изменении статуса заказа #{order_id}")

    async def add_product_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /add_product command - start product creation flow."""
        user_id = update.effective_user.id

        # Check authorization
        is_authorized, _ = await self.check_admin_authorization(user_id)
        if not is_authorized:
            await self._request_authorization(update)
            return

        await handle_add_product_start(update, context)

    async def products_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /products command - list all products."""
        user_id = update.effective_user.id

        # Check authorization
        is_authorized, _ = await self.check_admin_authorization(user_id)
        if not is_authorized:
            await self._request_authorization(update)
            return

        await update.message.reply_text(
            "📦 Список товаров будет реализован в следующей версии.\n\n"
            "Пока используйте веб-панель: frontend/ на порту 5176"
        )

    async def warehouse_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /warehouse command - show warehouse status."""
        user_id = update.effective_user.id

        # Check authorization
        is_authorized, _ = await self.check_admin_authorization(user_id)
        if not is_authorized:
            await self._request_authorization(update)
            return

        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            await handle_warehouse_status(update, context, self.mcp_client, self.shop_id)
        except Exception as e:
            logger.error("warehouse_command_failed", error=str(e))
            await update.message.reply_text("😔 Ошибка при загрузке данных склада")

    async def button_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle inline button callbacks."""
        query = update.callback_query
        await query.answer()

        # Parse callback data
        # Format: action:data (e.g., "status:156:PAID")
        callback_data = query.data.split(":")

        if callback_data[0] == "status":
            # Order status change via button
            order_id = int(callback_data[1])
            new_status = callback_data[2]

            try:
                await handle_change_order_status(
                    query, context, self.mcp_client, self.shop_id, order_id, new_status
                )
            except Exception as e:
                logger.error("button_status_change_failed", error=str(e))
                await query.edit_message_text(f"😔 Ошибка при изменении статуса")

    async def post_init(self, application: Application):
        """Post-initialization hook - initialize HTTP client for AI Agent."""
        self.http_client = httpx.AsyncClient()
        logger.info("admin_bot_initialized_successfully",
                   shop_id=self.shop_id,
                   environment=environment,
                   ai_agent_url=self.ai_agent_url)

    async def post_shutdown(self, application: Application):
        """Post-shutdown hook - clean up resources."""
        if self.http_client:
            await self.http_client.aclose()
        await self.mcp_client.close()
        logger.info("admin_bot_shutdown_successfully")

    def run_webhook(self, port: int = 8080):
        """Run bot in webhook mode (for production deployment)."""
        logger.info("starting_admin_bot_webhook_mode",
                   environment=environment,
                   shop_id=self.shop_id,
                   port=port)

        self.app.post_init = self.post_init
        self.app.post_shutdown = self.post_shutdown

        # Run webhook on 0.0.0.0 to accept connections from Railway
        webhook_path = "/webhook"
        full_webhook_url = f"{self.webhook_url}{webhook_path}"

        self.app.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=full_webhook_url,
            url_path=webhook_path,
            allowed_updates=Update.ALL_TYPES
        )

    def run_polling(self):
        """Run bot in polling mode (for local development)."""
        logger.info("starting_admin_bot_polling_mode",
                   environment=environment,
                   shop_id=self.shop_id)

        self.app.post_init = self.post_init
        self.app.post_shutdown = self.post_shutdown
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point - supports both webhook (production) and polling (development) modes."""
    port = int(os.getenv("PORT", "8080"))
    webhook_url = os.getenv('WEBHOOK_URL')

    print(f"🛠️  Admin Bot - Starting ({environment} environment)...")
    print(f"📍 Shop ID: {os.getenv('DEFAULT_SHOP_ID')}")
    print(f"🔧 MCP Server: {os.getenv('MCP_SERVER_URL')}")
    if webhook_url:
        print(f"🌐 Webhook URL: {webhook_url}")
        print(f"🔌 Port: {port}")
    else:
        print("🔄 Mode: Polling (local development)")
    print("")

    bot = AdminBot()

    # Use webhook if WEBHOOK_URL is set, otherwise polling
    if webhook_url:
        bot.run_webhook(port=port)
    else:
        bot.run_polling()


if __name__ == "__main__":
    main()
