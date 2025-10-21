#!/usr/bin/env python3
"""
Telegram Bot для визуального поиска товаров
Отправьте фото букета - получите похожие товары из каталога!
"""
import os
import logging
import requests
import asyncio
from dotenv import load_dotenv
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Загрузка переменных окружения
load_dotenv()

# Настройки
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "https://figma-product-catalog-production.up.railway.app/api/v1")
SHOP_ID = int(os.getenv("SHOP_ID", "17008"))

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def format_price(price_kopecks: int) -> str:
    """Форматирование цены с пробелами: 15000 -> 15 000"""
    price_tenge = price_kopecks / 100
    return f"{price_tenge:,.0f}".replace(",", " ")


async def send_product_with_buttons(message, product: dict, show_similar_btn: bool = False):
    """Отправить товар с кнопками действий"""
    caption = f"{product['name']}\n💰 {format_price(product['price'])}₸"

    keyboard = [
        [InlineKeyboardButton("🛒 Заказать", callback_data=f"order_{product['id']}")],
        [InlineKeyboardButton("📋 Подробнее", callback_data=f"details_{product['id']}")]
    ]

    if show_similar_btn:
        keyboard.append([InlineKeyboardButton("🔍 Показать похожие", callback_data="show_more_similar")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_photo(
        photo=product['image'],
        caption=caption,
        reply_markup=reply_markup
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(
        "🌸 Привет! Я помогу найти похожие букеты.\n\n"
        "📸 Просто отправь мне фото букета, и я покажу похожие товары из нашего каталога!\n\n"
        "Команды:\n"
        "/catalog - Показать каталог товаров"
    )


async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать каталог товаров с выбором бюджета"""
    keyboard = [
        [
            InlineKeyboardButton("До 10 000₸", callback_data="price_0_10000"),
            InlineKeyboardButton("10 000 - 20 000₸", callback_data="price_10000_20000"),
        ],
        [
            InlineKeyboardButton("20 000 - 50 000₸", callback_data="price_20000_50000"),
            InlineKeyboardButton("Свыше 50 000₸", callback_data="price_50000_999999"),
        ],
        [
            InlineKeyboardButton("📦 Показать все", callback_data="price_all"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "💰 На какую сумму товары интересуют?",
        reply_markup=reply_markup
    )


async def show_products(query, min_price: int, max_price: int, show_all: bool = False):
    """Показать товары в выбранном ценовом диапазоне (последовательно)"""
    await query.edit_message_text("📦 Загружаю каталог...")

    try:
        response = requests.get(f"{API_BASE_URL}/products", params={"shop_id": SHOP_ID, "limit": 100})
        all_products = response.json()

        if not all_products:
            await query.edit_message_text("📦 Каталог пуст")
            return

        # Фильтрация по цене
        if show_all:
            products = all_products[:5]
            price_label = "все товары"
        else:
            products = [p for p in all_products if min_price <= p['price'] <= max_price][:5]
            price_label = f"{format_price(min_price)} - {format_price(max_price)}₸"

        if not products:
            await query.edit_message_text(
                f"😔 Товаров в диапазоне {price_label} не найдено.\n"
                f"Попробуйте выбрать другой диапазон."
            )
            return

        # Удаляем сообщение с кнопками
        await query.delete_message()

        # Показываем товары по одному с задержкой
        for i, product in enumerate(products):
            await send_product_with_buttons(query.message, product, show_similar_btn=False)
            if i < len(products) - 1:
                await asyncio.sleep(1)  # Задержка 1 секунда между товарами

    except Exception as e:
        logger.error(f"Error fetching catalog: {e}")
        await query.edit_message_text("❌ Ошибка загрузки каталога")


async def catalog_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на все типы кнопок"""
    query = update.callback_query
    await query.answer()

    data = query.data

    # Кнопки выбора бюджета в каталоге
    if data.startswith("price_"):
        if data == "price_all":
            await show_products(query, 0, 999999999, show_all=True)
        else:
            # Парсим диапазон: price_10000_20000 -> min=1000000, max=2000000 (kopecks)
            _, min_str, max_str = data.split("_")
            min_price = int(min_str) * 100  # tenge to kopecks
            max_price = int(max_str) * 100
            await show_products(query, min_price, max_price)

    # Кнопка "Показать похожие"
    elif data == "show_more_similar":
        similar_products = context.user_data.get('similar_products', [])

        if not similar_products:
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n❌ Больше похожих товаров нет"
            )
            return

        # Показываем похожие товары по одному с задержкой
        for i, product in enumerate(similar_products[:4]):  # Максимум 4 товара
            await send_product_with_buttons(query.message, product, show_similar_btn=False)
            if i < len(similar_products) - 1:
                await asyncio.sleep(1)  # Задержка 1 секунда между товарами

        # Очищаем сохраненные товары
        context.user_data['similar_products'] = []

    # Кнопка "Заказать"
    elif data.startswith("order_"):
        product_id = data.split("_")[1]
        await query.answer("🛒 Для заказа свяжитесь с менеджером", show_alert=True)
        await query.message.reply_text(
            f"📞 Для заказа товара свяжитесь с менеджером:\n"
            f"Телефон: +7 (701) 521-15-45\n"
            f"WhatsApp: wa.me/77015211545"
        )

    # Кнопка "Подробнее"
    elif data.startswith("details_"):
        product_id = data.split("_")[1]
        await query.answer("📋 Загружаю подробности...")

        try:
            # Получаем детальную информацию о товаре
            response = requests.get(f"{API_BASE_URL}/products/{product_id}", params={"shop_id": SHOP_ID})
            product = response.json()

            details_text = (
                f"📋 **Подробная информация**\n\n"
                f"**Название**: {product['name']}\n"
                f"**Цена**: {format_price(product['price'])}₸\n"
                f"**ID**: {product['id']}\n"
            )

            if product.get('description'):
                details_text += f"**Описание**: {product['description']}\n"

            await query.message.reply_text(details_text, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error fetching product details: {e}")
            await query.message.reply_text("❌ Ошибка загрузки деталей товара")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика visual search"""
    try:
        response = requests.get(f"{API_BASE_URL}/products/search/stats", params={"shop_id": SHOP_ID})
        stats = response.json()

        message = (
            "📊 Статистика Visual Search:\n\n"
            f"📦 Всего товаров: {stats['total_products']}\n"
            f"🧠 С embeddings: {stats['products_with_embeddings']}\n"
            f"📈 Покрытие: {stats['coverage_percentage']}%\n"
            f"{'✅' if stats['search_ready'] else '❌'} Готовность к поиску"
        )

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        await update.message.reply_text("❌ Ошибка загрузки статистики")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка фото от пользователя"""
    await update.message.reply_text("🔍 Ищу похожие букеты...")

    try:
        # Получаем наибольшее фото
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        # URL фото из Telegram
        image_url = file.file_path

        # Поиск похожих товаров (запрашиваем больше для кнопки "Показать похожие")
        response = requests.post(
            f"{API_BASE_URL}/products/search/similar",
            json={
                "image_url": image_url,
                "shop_id": SHOP_ID,
                "limit": 5,
                "min_similarity": 0.6
            }
        )

        results = response.json()

        if not results.get('results'):
            await update.message.reply_text("😔 Похожие товары не найдены. Попробуйте другое фото!")
            return

        # Показываем только самый похожий товар (топ-1)
        top_product = results['results'][0]

        # Сохраняем остальные товары в context для кнопки "Показать похожие"
        if len(results['results']) > 1:
            context.user_data['similar_products'] = results['results'][1:]
            show_similar_button = True
        else:
            context.user_data['similar_products'] = []
            show_similar_button = False

        # Отправляем топ-1 товар с кнопками
        await send_product_with_buttons(update.message, top_product, show_similar_btn=show_similar_button)

    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await update.message.reply_text(
            "❌ Ошибка поиска. Возможно:\n"
            "• Фото слишком большое\n"
            "• Проблема с сетью\n"
            "• Сервер недоступен\n\n"
            "Попробуйте ещё раз!"
        )


def main():
    """Запуск бота"""
    if not TELEGRAM_TOKEN:
        print("❌ Ошибка: Токен не найден!")
        print("Создайте файл .env с переменной TELEGRAM_TOKEN")
        print("Или запустите: export TELEGRAM_TOKEN='ваш_токен'")
        return

    print(f"🤖 Запуск бота...")
    print(f"📡 API: {API_BASE_URL}")
    print(f"🏪 Shop ID: {SHOP_ID}")

    # Создаём приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("catalog", catalog))

    # Обработчик callback-кнопок
    application.add_handler(CallbackQueryHandler(catalog_button_callback))

    # Обработчик фото
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Запуск
    logger.info("🤖 Бот запущен! Отправьте фото букета для поиска.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
