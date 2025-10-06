"""
Production database seeding script.
Run with: railway run python seed_production.py

This script populates production database with:
- Test shop (id=8) with products
- Test order with tracking_id for verification
- FAQs and reviews
"""
import os
import asyncio
from database import create_db_and_tables, get_session
from seeds import seed_all


async def main():
    """Run production seeds"""
    print("🌱 Starting production database seeding...")

    # Verify we're connecting to production
    db_url = os.getenv('DATABASE_URL', '')
    if not db_url:
        print("❌ DATABASE_URL not set - are you running via 'railway run'?")
        return

    print(f"🔗 Connected to: {db_url[:50]}...")

    # Ensure tables exist
    await create_db_and_tables()
    print("✅ Tables verified")

    # Run seed scripts
    async for session in get_session():
        await seed_all(session)
        break

    print("✨ Production seeding complete!")
    print("\n📊 You can now test:")
    print("  - Tracking URL: https://cvety-website.pages.dev/status/{tracking_id}")
    print("  - Shop products: https://cvety-website.pages.dev/?shop_id=8")


if __name__ == "__main__":
    asyncio.run(main())
