"""
Telegram Notification Service for Product Analytics.

Sends real-time notifications to admin Telegram channel about:
- New shop registrations
- Onboarding progress
- First products, orders, and milestones
"""
import os
import asyncio
from datetime import datetime
from typing import Optional
from pytz import timezone

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Lazy import to avoid startup errors if telegram not installed
telegram_available = False
try:
    from telegram import Bot
    from telegram.error import TelegramError
    telegram_available = True
except ImportError:
    Bot = None
    TelegramError = Exception

from core.logging import get_logger

logger = get_logger(__name__)

# Configuration from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
FRONTEND_ADMIN_URL = os.getenv("FRONTEND_ADMIN_URL", "https://frontend-production-6869.up.railway.app")

# Timezone for Astana
ASTANA_TZ = timezone("Asia/Almaty")  # UTC+6 (Almaty/Astana same timezone)


def format_phone_for_whatsapp(phone: str) -> str:
    """
    Format phone number for WhatsApp link.
    Remove + and any spaces/dashes.
    """
    return phone.replace("+", "").replace(" ", "").replace("-", "")


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format datetime in Astana timezone"""
    if dt is None:
        dt = datetime.utcnow()
    astana_time = dt.replace(tzinfo=timezone("UTC")).astimezone(ASTANA_TZ)
    return astana_time.strftime("%d %b %Y, %H:%M")


def create_whatsapp_link(phone: str, message: str = "") -> str:
    """Create WhatsApp Web link with pre-filled message"""
    clean_phone = format_phone_for_whatsapp(phone)
    if message:
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{clean_phone}?text={encoded_message}"
    return f"https://wa.me/{clean_phone}"


def create_admin_link(shop_id: int, path: str = "") -> str:
    """Create link to admin panel shop profile"""
    return f"{FRONTEND_ADMIN_URL}/shop/{shop_id}{path}"


async def send_telegram_notification(message: str, parse_mode: str = "HTML") -> bool:
    """
    Send notification to admin Telegram channel.

    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not telegram_available:
        logger.warning("telegram_not_available", message="python-telegram-bot not installed")
        return False

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ADMIN_CHAT_ID:
        logger.warning("telegram_not_configured",
                      has_token=bool(TELEGRAM_BOT_TOKEN),
                      has_chat_id=bool(TELEGRAM_ADMIN_CHAT_ID))
        return False

    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_ADMIN_CHAT_ID,
            text=message,
            parse_mode=parse_mode,
            disable_web_page_preview=True
        )
        logger.info("telegram_notification_sent", message_length=len(message))
        return True
    except TelegramError as e:
        logger.error("telegram_send_failed", error=str(e))
        return False
    except Exception as e:
        logger.error("telegram_unexpected_error", error=str(e))
        return False


# ============================================================================
# Notification Templates
# ============================================================================

async def notify_new_registration(
    shop_id: int,
    shop_name: str,
    owner_name: str,
    owner_phone: str,
    city: Optional[str] = None,
    address: Optional[str] = None
):
    """Send notification about new shop registration"""
    whatsapp_link = create_whatsapp_link(
        owner_phone,
        "Здравствуйте! Я из поддержки Cvety.kz. Помогу вам настроить магазин 🌸"
    )
    admin_link = create_admin_link(shop_id)

    city_text = f"📍 {city}" if city else "📍 Город не указан"
    address_text = f", {address}" if address else ""

    message = f"""🆕 <b>НОВАЯ РЕГИСТРАЦИЯ</b>

👤 {owner_name}
📞 <a href="{whatsapp_link}">{owner_phone}</a>
🏪 Магазин: "{shop_name}"
{city_text}{address_text}
⏰ {format_timestamp()}

<b>Статус онбординга:</b>
{'✅' if city else '❌'} Город указан
❌ Продукты не добавлены (0 шт)
❌ Магазин закрыт

━━━━━━━━━━━━━━━━━
🔗 <a href="{admin_link}">Открыть профиль в админке</a>"""

    await send_telegram_notification(message)


async def notify_shop_name_changed(
    shop_id: int,
    new_name: str,
    owner_name: str,
    owner_phone: str,
    city: Optional[str] = None
):
    """Notify when shop changes name from default"""
    whatsapp_link = create_whatsapp_link(owner_phone, "Здравствуйте! Отличное название магазина выбрали 🌸")
    admin_link = create_admin_link(shop_id)

    message = f"""✅ <b>НАЗВАНИЕ ИЗМЕНЕНО</b>

🏪 Новое название: "{new_name}"
👤 {owner_name}
📞 <a href="{whatsapp_link}">{owner_phone}</a>
{'📍 ' + city if city else ''}
⏰ {format_timestamp()}

<b>Прогресс онбординга:</b>
✅ Название изменено
{'✅' if city else '❌'} Город указан
❌ Продукты не добавлены
❌ Магазин закрыт

━━━━━━━━━━━━━━━━━
🔗 <a href="{admin_link}">Открыть профиль</a>"""

    await send_telegram_notification(message)


async def notify_first_product_added(
    shop_id: int,
    shop_name: str,
    product_name: str,
    price_tenge: int,
    owner_phone: str
):
    """Notify when shop adds their first product"""
    whatsapp_link = create_whatsapp_link(owner_phone, "Поздравляю с первым товаром! 🎉")
    admin_link = create_admin_link(shop_id)

    message = f"""🛍️ <b>ПЕРВЫЙ ПРОДУКТ ДОБАВЛЕН</b>

🏪 {shop_name}
📦 Товар: {product_name}
💰 {price_tenge:,} ₸
⏰ {format_timestamp()}

<b>Прогресс онбординга:</b>
✅ Название изменено
✅ Первый продукт добавлен
❌ Магазин закрыт

━━━━━━━━━━━━━━━━━
📞 <a href="{whatsapp_link}">{owner_phone}</a>
🔗 <a href="{admin_link}">Открыть магазин</a>"""

    await send_telegram_notification(message)


async def notify_product_added(
    shop_id: int,
    shop_name: str,
    product_name: str,
    price_tenge: int,
    total_products: int,
    owner_phone: str
):
    """Notify when shop adds another product"""
    whatsapp_link = create_whatsapp_link(owner_phone)
    admin_link = create_admin_link(shop_id)

    message = f"""🛍️ <b>НОВЫЙ ПРОДУКТ</b>

🏪 {shop_name} (ID: {shop_id})
📦 {product_name}
💰 {price_tenge:,} ₸
⏰ {format_timestamp()}

Всего продуктов в магазине: {total_products} шт

━━━━━━━━━━━━━━━━━
📞 <a href="{whatsapp_link}">{owner_phone}</a>"""

    await send_telegram_notification(message)


async def notify_first_order_received(
    shop_id: int,
    shop_name: str,
    order_number: str,
    customer_name: str,
    customer_phone: str,
    total_tenge: int,
    delivery_address: Optional[str],
    owner_phone: str
):
    """Notify when shop receives their first order"""
    customer_whatsapp = create_whatsapp_link(customer_phone)
    owner_whatsapp = create_whatsapp_link(owner_phone, "Поздравляю с первым заказом! 🎉🎊")
    admin_link = create_admin_link(shop_id, f"/orders/{order_number}")

    delivery_text = f"📍 Доставка: {delivery_address}" if delivery_address else "📦 Самовывоз"

    message = f"""🛒 <b>ПЕРВЫЙ ЗАКАЗ!</b> 🎉

🏪 {shop_name} (ID: {shop_id})
📦 Заказ {order_number}
💰 {total_tenge:,} ₸

👤 Клиент: {customer_name}
📞 <a href="{customer_whatsapp}">{customer_phone}</a>
{delivery_text}

⏰ {format_timestamp()}

━━━━━━━━━━━━━━━━━
🔗 <a href="{admin_link}">Посмотреть заказ</a>
📞 <a href="{owner_whatsapp}">Связаться с владельцем</a>"""

    await send_telegram_notification(message)


async def notify_shop_opened(
    shop_id: int,
    shop_name: str,
    owner_name: str,
    owner_phone: str,
    total_products: int
):
    """Notify when shop opens for business"""
    whatsapp_link = create_whatsapp_link(owner_phone, "Поздравляю с открытием магазина! 🎊")
    admin_link = create_admin_link(shop_id)

    message = f"""🟢 <b>МАГАЗИН ОТКРЫТ</b>

🏪 {shop_name}
👤 {owner_name}
📦 Товаров в каталоге: {total_products}
⏰ {format_timestamp()}

Магазин готов принимать заказы! 🎉

━━━━━━━━━━━━━━━━━
📞 <a href="{whatsapp_link}">{owner_phone}</a>
🔗 <a href="{admin_link}">Посмотреть магазин</a>"""

    await send_telegram_notification(message)


async def notify_onboarding_completed(
    shop_id: int,
    shop_name: str,
    owner_name: str,
    owner_phone: str,
    registration_time: datetime,
    completion_time: datetime
):
    """Notify when shop completes full onboarding"""
    time_diff = completion_time - registration_time
    hours = int(time_diff.total_seconds() // 3600)
    minutes = int((time_diff.total_seconds() % 3600) // 60)
    time_to_complete = f"{hours} ч {minutes} мин" if hours > 0 else f"{minutes} мин"

    whatsapp_link = create_whatsapp_link(owner_phone, "Поздравляю с завершением настройки магазина! 🎉")
    admin_link = create_admin_link(shop_id)

    message = f"""🎉 <b>ОНБОРДИНГ ЗАВЕРШЕН!</b>

🏪 {shop_name}
👤 {owner_name}
📞 <a href="{whatsapp_link}">{owner_phone}</a>

✅ Название изменено
✅ Город и адрес указаны
✅ Добавлены продукты
✅ Магазин открыт 🟢

⏱ Time to completion: {time_to_complete}
⏰ {format_timestamp(completion_time)}

━━━━━━━━━━━━━━━━━
🔗 <a href="{admin_link}">Поздравить владельца</a>"""

    await send_telegram_notification(message)
