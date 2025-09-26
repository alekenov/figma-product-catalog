"""
Script to seed authentication and shop settings data independently
"""
import asyncio
from database import create_db_and_tables, async_session
from models import User, UserRole, ShopSettings, City
from auth_utils import get_password_hash


async def seed_auth_data():
    """
    Seed authentication users and shop settings.
    Can be called independently or as part of larger seeding process.
    """
    print("🔑 Starting authentication data seeding...")

    # Create tables if they don't exist
    await create_db_and_tables()
    print("📊 Database tables verified")

    # Seed users
    await seed_users()

    # Seed shop settings
    await seed_shop_settings()

    print("🎉 Authentication data seeding completed!")


async def seed_users():
    """Seed initial users for authentication system"""

    async with async_session() as session:
        try:
            # Check if director already exists
            from sqlmodel import select
            result = await session.exec(
                select(User).where(User.role == UserRole.DIRECTOR)
            )
            if result.first():
                print("⚠️  Director user already exists, skipping user creation")
                return

            # Hash password for development
            password = "password"
            password_hash = get_password_hash(password)

            # Create director user (from Profile.jsx and CLAUDE.md)
            director = User(
                name="Алексей Кенов",
                phone="+77015211545",
                role=UserRole.DIRECTOR,
                password_hash=password_hash,
                is_active=True,
                invited_by=None  # Director is the root user
            )
            session.add(director)
            await session.flush()  # Get the director's ID

            # Create sample team members
            team_members = [
                {
                    "name": "Анна Смирнова",
                    "phone": "+77012345678",
                    "role": UserRole.MANAGER,
                    "password_hash": password_hash,
                    "is_active": True,
                    "invited_by": director.id
                },
                {
                    "name": "Максим Петров",
                    "phone": "+77013456789",
                    "role": UserRole.FLORIST,
                    "password_hash": password_hash,
                    "is_active": True,
                    "invited_by": director.id
                }
            ]

            for member_data in team_members:
                member = User(**member_data)
                session.add(member)

            await session.commit()
            print("✅ Users seeded successfully")
            print("   📱 Director: Алексей Кенов (+77015211545)")
            print("   📱 Manager: Анна Смирнова (+77012345678)")
            print("   📱 Florist: Максим Петров (+77013456789)")
            print("   🔐 Password for all users: 'password'")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding users: {e}")
            raise


async def seed_shop_settings():
    """Seed initial shop settings"""

    async with async_session() as session:
        try:
            # Check if shop settings already exist
            from sqlmodel import select
            existing_settings = await session.exec(select(ShopSettings))
            if existing_settings.first():
                print("⚠️  Shop settings already exist, skipping shop settings creation")
                return

            # Create initial shop settings (from Profile.jsx example and Kazakhstan market conventions)
            shop_settings = ShopSettings(
                shop_name="Cvety.kz",
                address="ул. Абая 15, кв. 25",
                city=City.ALMATY,

                # Working hours
                weekday_start="09:00",
                weekday_end="18:00",
                weekday_closed=False,

                weekend_start="10:00",
                weekend_end="16:00",
                weekend_closed=False,

                # Delivery settings (in kopecks)
                delivery_cost=150000,  # 1500 tenge
                free_delivery_amount=1500000,  # 15000 tenge
                pickup_available=True,
                delivery_available=True
            )

            session.add(shop_settings)
            await session.commit()
            print("✅ Shop settings seeded successfully")
            print("   🏪 Shop: Cvety.kz")
            print("   📍 Address: ул. Абая 15, кв. 25")
            print("   🏙️  City: Almaty")
            print("   🚚 Delivery: 1500₸ (free over 15000₸)")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding shop settings: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_auth_data())