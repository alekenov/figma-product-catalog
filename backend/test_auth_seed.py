"""
Simple test script to verify seeded authentication data
"""
import asyncio
from database import async_session
from models import User, UserRole, ShopSettings
from auth_utils import verify_password
from sqlmodel import select


async def test_seeded_auth_data():
    """Test that seeded authentication data is correct"""
    print("🧪 Testing seeded authentication data...")

    async with async_session() as session:
        # Test director user
        director_query = select(User).where(User.phone == "+77015211545")
        result = await session.execute(director_query)
        director = result.scalar_one_or_none()

        if director:
            print("✅ Director user found:")
            print(f"   Name: {director.name}")
            print(f"   Phone: {director.phone}")
            print(f"   Role: {director.role}")
            print(f"   Active: {director.is_active}")

            # Test password
            if verify_password("password", director.password_hash):
                print("✅ Director password verification successful")
            else:
                print("❌ Director password verification failed")
        else:
            print("❌ Director user not found")

        # Test team members
        team_phones = ["+77012345678", "+77013456789"]
        for phone in team_phones:
            user_query = select(User).where(User.phone == phone)
            result = await session.execute(user_query)
            user = result.scalar_one_or_none()

            if user:
                print(f"✅ Team member found: {user.name} ({user.role})")
                if verify_password("password", user.password_hash):
                    print(f"✅ Password verification successful for {user.name}")
                else:
                    print(f"❌ Password verification failed for {user.name}")
            else:
                print(f"❌ Team member not found: {phone}")

        # Test shop settings
        settings_query = select(ShopSettings)
        result = await session.execute(settings_query)
        settings = result.scalar_one_or_none()

        if settings:
            print("✅ Shop settings found:")
            print(f"   Shop: {settings.shop_name}")
            print(f"   Address: {settings.address}")
            print(f"   City: {settings.city}")
            print(f"   Delivery cost: {settings.delivery_cost // 100}₸")
            print(f"   Free delivery over: {settings.free_delivery_amount // 100}₸")
        else:
            print("❌ Shop settings not found")

        print("\n🎯 Test Summary:")
        print("All seeded authentication data should now be available for login testing.")
        print("Use phone numbers and password 'password' to test authentication endpoints.")


if __name__ == "__main__":
    asyncio.run(test_seeded_auth_data())