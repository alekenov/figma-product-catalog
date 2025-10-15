#!/usr/bin/env python3
"""
Diagnostic script to check Telegram bot status and identify conflicts.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Production bot token (from Railway environment TELEGRAM_TOKEN)
# For diagnosis only - never hardcode tokens!
PROD_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

# Local test bot token (from .env TEST_TELEGRAM_TOKEN for local development)
# Set different token if you have separate test bot
TEST_TOKEN = os.getenv("TEST_TELEGRAM_TOKEN", os.getenv("TELEGRAM_TOKEN", ""))

def check_bot_info(token, name):
    """Check bot information."""
    print(f"\n{'='*60}")
    print(f"Checking {name}")
    print(f"{'='*60}")

    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url, timeout=5)
        if response.ok:
            data = response.json()
            if data.get('ok'):
                bot = data['result']
                print(f"✅ Bot is valid:")
                print(f"   Name: {bot.get('first_name')}")
                print(f"   Username: @{bot.get('username')}")
                print(f"   ID: {bot.get('id')}")
                return True
            else:
                print(f"❌ Invalid bot: {data}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_webhook(token, name):
    """Check webhook status."""
    print(f"\n{'-'*60}")
    print(f"Webhook Status for {name}")
    print(f"{'-'*60}")

    url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    try:
        response = requests.get(url, timeout=5)
        if response.ok:
            data = response.json()
            if data.get('ok'):
                info = data['result']
                webhook_url = info.get('url', '')

                if webhook_url:
                    print(f"🌐 Webhook Mode:")
                    print(f"   URL: {webhook_url}")
                    print(f"   Pending updates: {info.get('pending_update_count', 0)}")
                    print(f"   Max connections: {info.get('max_connections', 0)}")
                    print(f"   IP: {info.get('ip_address', 'N/A')}")

                    # Check if webhook is accessible
                    try:
                        webhook_response = requests.get(webhook_url, timeout=5)
                        print(f"   Webhook accessible: {webhook_response.status_code}")
                    except Exception as e:
                        print(f"   ⚠️  Webhook not accessible: {e}")
                else:
                    print(f"🔄 Polling Mode (no webhook set)")

                return webhook_url
            else:
                print(f"❌ Error: {data}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def check_updates(token, name):
    """Try to get updates (will fail if webhook is active)."""
    print(f"\n{'-'*60}")
    print(f"Testing getUpdates for {name}")
    print(f"{'-'*60}")

    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        response = requests.get(url, timeout=5)
        if response.ok:
            data = response.json()
            if data.get('ok'):
                print(f"✅ getUpdates works (no webhook conflict)")
                print(f"   Updates: {len(data.get('result', []))}")
            else:
                error_desc = data.get('description', 'Unknown error')
                if 'webhook' in error_desc.lower():
                    print(f"⚠️  Webhook is active: {error_desc}")
                else:
                    print(f"❌ Error: {error_desc}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main diagnostic routine."""
    print("\n" + "="*60)
    print("TELEGRAM BOT DIAGNOSTIC TOOL")
    print("="*60)

    # Check production bot
    if check_bot_info(PROD_TOKEN, "Production Bot (@cvetykzsupportbot)"):
        webhook_url = check_webhook(PROD_TOKEN, "Production Bot")
        check_updates(PROD_TOKEN, "Production Bot")

        # Provide recommendations
        print(f"\n{'='*60}")
        print("RECOMMENDATIONS")
        print(f"{'='*60}")

        if webhook_url:
            print("\n✅ Production bot is using WEBHOOK mode (correct)")
            print(f"   Webhook URL: {webhook_url}")
            print("\n⚠️  If you're seeing conflicts:")
            print("   1. Check if webhook URL is responding correctly")
            print("   2. Check if AI Agent Service is running")
            print("   3. Make sure no other bot instance is using this token")
            print("   4. Check Railway logs: railway logs --service telegram-bot")
        else:
            print("\n⚠️  Production bot has NO webhook set!")
            print("   This is incorrect for Railway deployment.")
            print("   Expected webhook: https://telegram-bot-production-75a7.up.railway.app/webhook")

    # Check test bot
    if TEST_TOKEN and TEST_TOKEN != PROD_TOKEN:
        print("\n")
        if check_bot_info(TEST_TOKEN, "Test Bot (local)"):
            check_webhook(TEST_TOKEN, "Test Bot")

    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
