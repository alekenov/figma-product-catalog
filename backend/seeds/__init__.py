"""
Seed scripts for initial data population
"""
from sqlalchemy.ext.asyncio import AsyncSession
from .faqs import seed_faqs
from .reviews import seed_reviews
from .test_data import seed_test_shop


async def seed_all(session: AsyncSession):
    """
    Run all seed scripts in order.
    Safe to run multiple times - checks for existing data.
    """
    print("🌱 Running seed scripts...")

    # Seed test shop and products (for testing framework)
    await seed_test_shop(session)

    # Seed FAQs
    await seed_faqs(session)

    # Seed Reviews
    await seed_reviews(session)

    print("✅ All seeds completed!")