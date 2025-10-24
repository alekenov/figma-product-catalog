"""
Admin Handlers for Flower Shop Admin Bot
Functions for managing orders, products, and warehouse operations.
"""
import asyncio
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def handle_list_orders(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    mcp_client,
    shop_id: int
):
    """
    Handle /orders command - show list of recent orders with filters.

    MVP: Shows last 10 orders with NEW/PAID status
    Future: Add pagination, filters, search
    """
    try:
        # Use MCP to get orders (admin endpoint would be ideal, but we'll use list_orders)
        # This is a placeholder - actual implementation depends on MCP tools availability

        response_text = (
            "📦 **Список заказов** (MVP)\n\n"
            "Эта функция будет показывать:\n"
            "• Новые заказы (NEW)\n"
            "• Оплаченные заказы (PAID)\n"
            "• Фильтры по статусу\n\n"
            "**Пока используйте:**\n"
            "• Веб-панель: frontend/ (порт 5176)\n"
            "• Backend API: /api/v1/orders/\n\n"
            "**Будет реализовано:**\n"
            "/order <id> - детали заказа\n"
            "/status <id> <статус> - изменить статус"
        )

        await update.message.reply_text(response_text, parse_mode="Markdown")

    except Exception as e:
        raise Exception(f"Failed to list orders: {str(e)}")


async def handle_order_details(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    mcp_client,
    shop_id: int,
    order_id: int
):
    """
    Handle /order <id> command - show detailed order information.

    Shows:
    - Order ID, status, total
    - Customer info
    - Items
    - Delivery details
    - Quick action buttons to change status
    """
    try:
        # Placeholder - will use MCP get_order tool when available
        response_text = (
            f"📦 **Заказ #{order_id}** (MVP)\n\n"
            f"**Детали заказа будут включать:**\n"
            f"• Статус: NEW/PAID/IN_PRODUCTION/etc\n"
            f"• Клиент: Имя, телефон\n"
            f"• Товары: Список с ценами\n"
            f"• Доставка: Адрес, дата, время\n"
            f"• Общая сумма: ₸\n\n"
            f"**Пока используйте веб-панель или API**\n\n"
            f"Изменить статус: /status {order_id} <СТАТУС>"
        )

        # Add quick action buttons for status changes
        keyboard = [
            [
                InlineKeyboardButton("✅ ACCEPTED", callback_data=f"status:{order_id}:ACCEPTED"),
                InlineKeyboardButton("🔨 IN_PRODUCTION", callback_data=f"status:{order_id}:IN_PRODUCTION"),
            ],
            [
                InlineKeyboardButton("📦 READY", callback_data=f"status:{order_id}:READY"),
                InlineKeyboardButton("🚚 IN_DELIVERY", callback_data=f"status:{order_id}:IN_DELIVERY"),
            ],
            [
                InlineKeyboardButton("✅ DELIVERED", callback_data=f"status:{order_id}:DELIVERED"),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            response_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    except Exception as e:
        raise Exception(f"Failed to get order details: {str(e)}")


async def handle_change_order_status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    mcp_client,
    shop_id: int,
    order_id: int,
    new_status: str
):
    """
    Handle status change for an order.

    Valid statuses:
    - NEW
    - PAID
    - ACCEPTED
    - IN_PRODUCTION
    - READY
    - IN_DELIVERY
    - DELIVERED
    - CANCELLED
    """
    valid_statuses = [
        "NEW", "PAID", "ACCEPTED", "IN_PRODUCTION",
        "READY", "IN_DELIVERY", "DELIVERED", "CANCELLED"
    ]

    if new_status not in valid_statuses:
        error_text = (
            f"❌ Неверный статус: {new_status}\n\n"
            f"Доступные статусы:\n" + "\n".join(f"• {s}" for s in valid_statuses)
        )
        await update.message.reply_text(error_text)
        return

    try:
        # Use MCP update_order_status tool
        # This is a placeholder - actual implementation will use MCP client

        response_text = (
            f"✅ **Статус заказа изменен** (MVP)\n\n"
            f"Заказ: #{order_id}\n"
            f"Новый статус: {new_status}\n\n"
            f"**Эта функция будет:**\n"
            f"• Обновлять статус в БД\n"
            f"• Отправлять уведомление клиенту\n"
            f"• Логировать изменение\n\n"
            f"Пока используйте веб-панель"
        )

        await update.message.reply_text(response_text, parse_mode="Markdown")

    except Exception as e:
        raise Exception(f"Failed to change order status: {str(e)}")


async def handle_add_product_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """
    Handle /add_product command - start the product creation flow.

    Flow:
    1. Send instructions to upload photo
    2. Wait for photo
    3. Ask for product details (name, type, price)
    4. Upload photo to Cloudflare R2
    5. Create product via MCP
    """
    instructions = (
        "➕ **Добавить товар** (MVP)\n\n"
        "**Процесс добавления товара:**\n\n"
        "1️⃣ Отправьте фото букета\n"
        "2️⃣ Введите данные:\n"
        "   • Название: Букет \"Романтика\"\n"
        "   • Тип: bouquet/composition/box\n"
        "   • Цена: 15000 (в копейках)\n"
        "3️⃣ Подтвердите\n\n"
        "**Функция будет реализована:**\n"
        "• Загрузка фото в Cloudflare R2\n"
        "• Создание товара через MCP\n"
        "• Автоматическая публикация\n\n"
        "Пока используйте веб-панель: /add-product"
    )

    await update.message.reply_text(instructions, parse_mode="Markdown")


async def handle_warehouse_status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    mcp_client,
    shop_id: int
):
    """
    Handle /warehouse command - show warehouse inventory status.

    Shows:
    - Current stock levels
    - Low stock warnings
    - Recent operations
    """
    try:
        # Use MCP list_warehouse_items tool
        # This is a placeholder

        response_text = (
            "📦 **Склад - Остатки** (MVP)\n\n"
            "**Будет показывать:**\n\n"
            "🌹 **Цветы:**\n"
            "• Розы красные: 50 шт ✅\n"
            "• Розы белые: 30 шт ⚠️ Мало\n"
            "• Лилии: 5 шт ❌ Критично\n\n"
            "🎀 **Материалы:**\n"
            "• Лента атласная: 100 м ✅\n"
            "• Коробки большие: 15 шт ✅\n"
            "• Упаковка: 8 шт ⚠️ Мало\n\n"
            "**Функции:**\n"
            "• Добавление товара: /add_stock <id> <кол-во>\n"
            "• История операций\n"
            "• Критические остатки\n\n"
            "Пока используйте веб-панель"
        )

        await update.message.reply_text(response_text, parse_mode="Markdown")

    except Exception as e:
        raise Exception(f"Failed to get warehouse status: {str(e)}")


# Additional helper functions

def format_order_status(status: str) -> str:
    """Format order status with emoji."""
    status_emoji = {
        "NEW": "🆕",
        "PAID": "💳",
        "ACCEPTED": "✅",
        "IN_PRODUCTION": "🔨",
        "READY": "📦",
        "IN_DELIVERY": "🚚",
        "DELIVERED": "✅",
        "CANCELLED": "❌",
    }
    return f"{status_emoji.get(status, '❓')} {status}"


def format_price(price_kopecks: int) -> str:
    """Format price from kopecks to readable tenge."""
    tenge = price_kopecks / 100
    return f"{tenge:,.0f}₸"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
