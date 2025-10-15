#!/usr/bin/env python3
"""
Send production shops report to Telegram.
Shows all 20 shops currently in production database.
"""
import os
import asyncio
import requests
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

PRODUCTION_URL = "https://figma-product-catalog-production.up.railway.app"


def get_production_shops():
    """Get all shops from production via public API"""
    try:
        print("📊 Fetching shops from production...")
        response = requests.get(f"{PRODUCTION_URL}/api/v1/shops/", timeout=10)

        if response.status_code == 200:
            shops = response.json()
            print(f"✅ Found {len(shops)} shops in production\n")
            return shops
        else:
            print(f"❌ Failed to fetch shops: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching production data: {e}")
        return []


def format_production_report(shops):
    """Format production shops report for Telegram"""
    if not shops:
        return "📊 <b>PRODUCTION DATABASE REPORT</b>\n\nNo shops found."

    # Header
    message = f"""📊 <b>PRODUCTION DATABASE REPORT</b>
<b>Date:</b> 14 October 2025

<b>Total Shops:</b> {len(shops)} шт

━━━━━━━━━━━━━━━━━━━━"""

    # Group shops by status
    active_shops = [s for s in shops if s.get('is_active')]
    inactive_shops = [s for s in shops if not s.get('is_active')]

    # Active shops first
    if active_shops:
        message += f"\n\n<b>🟢 ОТКРЫТЫЕ МАГАЗИНЫ ({len(active_shops)} шт)</b>\n"
        for idx, shop in enumerate(active_shops, 1):
            shop_name = shop.get('name', 'Без названия')
            shop_id = shop.get('id')
            city = shop.get('city', 'Город не указан')
            phone = shop.get('phone', 'Не указан')

            # WhatsApp link
            if phone and phone != 'Не указан':
                clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
                wa_link = f"https://wa.me/{clean_phone}"
                phone_display = f'<a href="{wa_link}">{phone}</a>'
            else:
                phone_display = phone

            message += f"""
<b>{idx}. {shop_name}</b>
   🆔 ID: {shop_id}
   📍 {city}
   📞 {phone_display}"""

    # Inactive shops
    if inactive_shops:
        message += f"\n\n<b>🔴 ЗАКРЫТЫЕ МАГАЗИНЫ ({len(inactive_shops)} шт)</b>\n"
        for idx, shop in enumerate(inactive_shops, 1):
            shop_name = shop.get('name', 'Без названия')
            shop_id = shop.get('id')
            city = shop.get('city', 'Город не указан')
            phone = shop.get('phone', 'Не указан')

            # WhatsApp link
            if phone and phone != 'Не указан':
                clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
                wa_link = f"https://wa.me/{clean_phone}"
                phone_display = f'<a href="{wa_link}">{phone}</a>'
            else:
                phone_display = phone

            message += f"""
<b>{idx}. {shop_name}</b>
   🆔 ID: {shop_id}
   📍 {city}
   📞 {phone_display}"""

    # Footer
    message += "\n\n━━━━━━━━━━━━━━━━━━━━"
    message += "\n🔗 <b>Production:</b> figma-product-catalog-production.up.railway.app"

    return message


async def main():
    """Send production report to Telegram"""
    print("📊 Collecting production data...\n")

    shops = get_production_shops()

    if shops:
        print("Found shops:")
        for shop in shops:
            status = "🟢" if shop.get('is_active') else "🔴"
            print(f"   {status} {shop.get('name')} (ID: {shop.get('id')}) - {shop.get('city')}")

    print("\n📤 Formatting and sending report to Telegram...")
    message = format_production_report(shops)

    success = await send_telegram_notification(message)

    if success:
        print("✅ Production report sent successfully to Telegram!")
    else:
        print("❌ Failed to send report. Check Telegram credentials in .env")


if __name__ == "__main__":
    asyncio.run(main())
