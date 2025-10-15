#!/usr/bin/env python3
"""
Send historical report to Telegram about users registered from Oct 11 to today.
One-time script to catch up on missed notifications.
"""
import os
import asyncio
import sqlite3
from datetime import datetime
from pathlib import Path

# Load .env manually
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

from services.telegram_notifications import send_telegram_notification


def get_historical_data():
    """Get all users and their activity from Oct 11 to today"""
    conn = sqlite3.connect('figma_catalog.db')
    cursor = conn.cursor()

    # Get users registered from Oct 9 onwards (when first active users appeared)
    cursor.execute("""
        SELECT
            u.id, u.name, u.phone, u.created_at,
            s.id as shop_id, s.name as shop_name, s.city, s.is_active
        FROM user u
        LEFT JOIN shop s ON u.shop_id = s.id
        WHERE u.created_at >= '2025-10-09'
        ORDER BY u.created_at
    """)

    users = []
    for row in cursor.fetchall():
        user_id, name, phone, created_at, shop_id, shop_name, city, is_active = row

        # Get products count
        cursor.execute("SELECT COUNT(*) FROM product WHERE shop_id = ?", (shop_id,))
        products_count = cursor.fetchone()[0]

        # Get orders count
        cursor.execute('SELECT COUNT(*) FROM "order" WHERE shop_id = ?', (shop_id,))
        orders_count = cursor.fetchone()[0]

        users.append({
            'user_id': user_id,
            'name': name,
            'phone': phone,
            'created_at': created_at,
            'shop_id': shop_id,
            'shop_name': shop_name,
            'city': city,
            'is_active': is_active,
            'products_count': products_count,
            'orders_count': orders_count
        })

    conn.close()
    return users


def format_report(users):
    """Format historical report message"""
    if not users:
        return "📊 <b>ИСТОРИЧЕСКИЙ ОТЧЕТ (9-14 октября)</b>\n\nНовых регистраций не было."

    # Header
    message = f"""📊 <b>ИСТОРИЧЕСКИЙ ОТЧЕТ</b>
<b>Период:</b> 9 - 14 октября 2025

<b>Всего регистраций:</b> {len(users)} шт

━━━━━━━━━━━━━━━━━━━━"""

    # Each user
    for idx, user in enumerate(users, 1):
        # Format datetime
        dt = datetime.fromisoformat(user['created_at'])
        date_str = dt.strftime("%d %b, %H:%M")

        # Status emoji
        status = "🟢 Открыт" if user['is_active'] else "🔴 Закрыт"
        city_text = f"📍 {user['city']}" if user['city'] else "📍 Город не указан"

        # WhatsApp link
        clean_phone = user['phone'].replace("+", "").replace(" ", "").replace("-", "")
        wa_link = f"https://wa.me/{clean_phone}"

        user_block = f"""

<b>{idx}️⃣ {user['name']}</b>
📞 <a href="{wa_link}">{user['phone']}</a>
🏪 {user['shop_name']} (ID: {user['shop_id']})
{city_text}
📅 {date_str}

<b>Активность:</b>
📦 Продукты: {user['products_count']} шт
🛒 Заказы: {user['orders_count']} шт
{status}"""

        message += user_block

    # Footer
    message += "\n\n━━━━━━━━━━━━━━━━━━━━"
    message += "\n💡 <i>Единоразовый отчет за пропущенный период</i>"

    return message


async def main():
    """Send historical report to Telegram"""
    print("📊 Collecting historical data from Oct 11 to today...")

    users = get_historical_data()
    print(f"✅ Found {len(users)} registrations")

    if users:
        for user in users:
            print(f"   - {user['name']} ({user['phone']}) - {user['products_count']} products, {user['orders_count']} orders")

    print("\n📤 Formatting and sending report to Telegram...")
    message = format_report(users)

    success = await send_telegram_notification(message)

    if success:
        print("✅ Historical report sent successfully to Telegram!")
    else:
        print("❌ Failed to send report. Check Telegram credentials in .env")


if __name__ == "__main__":
    asyncio.run(main())
