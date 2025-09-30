"""
FAQ seed data - populates initial FAQ questions from frontend mock data
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from models import FAQ


async def seed_faqs(session: AsyncSession):
    """
    Seed FAQ data from FAQSection.jsx mockFAQs.
    Only seeds if no FAQs exist in database.
    """
    # Check if FAQs already exist
    check_query = select(FAQ).limit(1)
    check_result = await session.execute(check_query)
    existing_faqs = check_result.first()

    if existing_faqs:
        print("  ⏭️  FAQs already exist, skipping seed")
        return

    faqs_data = [
        {
            "question": "Почему заказывать цветы в Астане стоит в Cvety.kz?",
            "answer": "Мы предлагаем широкий ассортимент свежих цветов, быструю доставку и отличное обслуживание.",
            "category": "general",
            "display_order": 1
        },
        {
            "question": "Как именно выполняется доставка цветов по Астане?",
            "answer": "Доставка цветов по Астане может быть анонимной или нет. В первом случае букет будет доставлен курьером «инкогнито». Мы не сообщим получателю ваше имя. При этом вы можете дополнить букет цветов открыткой, в которой будет указано специальное послание. При обычной доставке же имя отправителя сообщается.",
            "category": "delivery",
            "display_order": 2
        },
        {
            "question": "Сколько стоит доставка?",
            "answer": "Стоимость доставки зависит от района и времени доставки. Подробности уточняйте при оформлении заказа.",
            "category": "delivery",
            "display_order": 3
        },
        {
            "question": "Как я узнаю, что заказ доставлен?",
            "answer": "Вы получите уведомление на телефон или email сразу после доставки букета.",
            "category": "orders",
            "display_order": 4
        },
        {
            "question": "В какие города Казахстана вы доставляете цветы?",
            "answer": "Мы осуществляем доставку цветов в Астану, Алматы и другие крупные города Казахстана.",
            "category": "delivery",
            "display_order": 5
        },
        {
            "question": "Цветы точно будут свежими?",
            "answer": "Да, мы гарантируем свежесть всех цветов. Букеты собираются непосредственно перед доставкой.",
            "category": "quality",
            "display_order": 6
        },
        {
            "question": "В какие сроки выполняется доставка букетов по Астане?",
            "answer": "Мы предлагаем доставку в день заказа, а также можем договориться о доставке на конкретное время.",
            "category": "delivery",
            "display_order": 7
        },
        {
            "question": "В какое время возможна доставка цветов по Астане?",
            "answer": "Доставка возможна с 9:00 до 21:00 ежедневно. Доступна также срочная доставка.",
            "category": "delivery",
            "display_order": 8
        }
    ]

    # Create FAQ records
    for faq_data in faqs_data:
        faq = FAQ(**faq_data)
        session.add(faq)

    await session.commit()
    print(f"  ✅ Seeded {len(faqs_data)} FAQs")