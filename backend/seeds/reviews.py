"""
Review seed data - populates initial company reviews from frontend mock data
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from models import CompanyReview


async def seed_reviews(session: AsyncSession):
    """
    Seed company review data from ReviewsSection.jsx mockReviews.
    Only seeds if no company reviews exist in database.
    """
    # Check if reviews already exist
    check_query = select(CompanyReview).limit(1)
    check_result = await session.execute(check_query)
    existing_reviews = check_result.first()

    if existing_reviews:
        print("  ⏭️  Company reviews already exist, skipping seed")
        return

    shop_id = 8  # Test shop ID

    reviews_data = [
        {
            "author_name": "Alekenov C.",
            "rating": 5,
            "text": "Один из лучших цветочных магазинов в городе. Букеты всегда свежие, доставка быстрая, цены адекватные.",
            "likes": 12,
            "dislikes": 0,
            "shop_id": shop_id
        },
        {
            "author_name": "Мария К.",
            "rating": 5,
            "text": "Хороший букет, вовремя доставили. Цветы простояли больше недели!",
            "likes": 8,
            "dislikes": 0,
            "shop_id": shop_id
        },
        {
            "author_name": "Асель Т.",
            "rating": 4,
            "text": "Заказывала несколько раз, в целом довольна. Один раз была небольшая задержка с доставкой, но цветы были свежие.",
            "likes": 5,
            "dislikes": 1,
            "shop_id": shop_id
        },
        {
            "author_name": "Даулет Б.",
            "rating": 5,
            "text": "Отличный сервис! Заказал букет для жены на годовщину - она была в восторге. Спасибо!",
            "likes": 15,
            "dislikes": 0,
            "shop_id": shop_id
        },
        {
            "author_name": "Лаура Ж.",
            "rating": 5,
            "text": "Всегда заказываю цветы только здесь. Широкий выбор, есть необычные композиции.",
            "likes": 10,
            "dislikes": 0,
            "shop_id": shop_id
        },
        {
            "author_name": "Ержан М.",
            "rating": 4,
            "text": "Хороший магазин, но хотелось бы больше акций и скидок для постоянных клиентов.",
            "likes": 6,
            "dislikes": 2,
            "shop_id": shop_id
        }
    ]

    # Create review records
    for review_data in reviews_data:
        review = CompanyReview(**review_data)
        session.add(review)

    await session.commit()
    print(f"  ✅ Seeded {len(reviews_data)} company reviews")