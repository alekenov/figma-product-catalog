import os
from dotenv import load_dotenv
import requests

load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")

# Delete webhook
url = f"https://api.telegram.org/bot{token}/deleteWebhook?drop_pending_updates=true"
response = requests.get(url)
print(f"Webhook cleared: {response.json()}")

# Get bot info
info_url = f"https://api.telegram.org/bot{token}/getMe"
info = requests.get(info_url).json()
if info.get('ok'):
    bot = info['result']
    print(f"\n✅ Бот готов к работе:")
    print(f"   Имя: {bot.get('first_name')}")
    print(f"   Username: @{bot.get('username')}")
    print(f"   ID: {bot.get('id')}")
