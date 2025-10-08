"""
Script to fix the demo user authentication issues:
1. Create a shop if it doesn't exist
2. Assign shop to demo user
3. Set correct password
"""
import asyncio
from database import get_session
from models import User, Shop
from auth_utils import get_password_hash
from sqlmodel import select


async def fix_demo_user():
    """Fix demo user for authentication testing"""

    print("🔧 Fixing demo user authentication...")

    async for session in get_session():
        try:
            # Find demo user
            query = select(User).where(User.phone == '+77015211545')
            result = await session.execute(query)
            demo_user = result.scalar_one_or_none()

            if not demo_user:
                print("❌ Demo user not found with phone +77015211545")
                return

            print(f"✅ Found demo user: {demo_user.name} (ID: {demo_user.id})")
            print(f"   Current shop_id: {demo_user.shop_id}")

            # Check if user already has a shop
            if demo_user.shop_id:
                print(f"   User already has shop_id: {demo_user.shop_id}")
            else:
                # Find or create a shop
                shop_query = select(Shop).limit(1)
                shop_result = await session.execute(shop_query)
                shop = shop_result.scalar_one_or_none()

                if not shop:
                    # Create a new shop
                    print("   📦 Creating new shop...")
                    shop = Shop(
                        owner_id=demo_user.id,
                        name="Cvety.kz",
                        phone=demo_user.phone,
                        address="ул. Абая 15, кв. 25",
                        email="info@cvety.kz"
                    )
                    session.add(shop)
                    await session.flush()  # Get shop.id
                    print(f"   ✅ Created shop: {shop.name} (ID: {shop.id})")
                else:
                    print(f"   ✅ Using existing shop: {shop.name} (ID: {shop.id})")

                # Assign shop to user
                demo_user.shop_id = shop.id
                print(f"   ✅ Assigned shop_id {shop.id} to user")

            # Update password to "password"
            new_password = "password"
            new_password_hash = get_password_hash(new_password)
            demo_user.password_hash = new_password_hash
            print(f"   ✅ Updated password to: \"{new_password}\"")

            # Commit changes
            await session.commit()
            await session.refresh(demo_user)

            print("\n🎉 Demo user fixed successfully!")
            print(f"   📱 Phone: {demo_user.phone}")
            print(f"   🔐 Password: {new_password}")
            print(f"   🏪 Shop ID: {demo_user.shop_id}")
            print(f"   👤 Role: {demo_user.role}")
            print("\n   You can now login at http://localhost:5176/login")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error fixing demo user: {e}")
            raise

        break  # Exit after first session


if __name__ == "__main__":
    asyncio.run(fix_demo_user())
