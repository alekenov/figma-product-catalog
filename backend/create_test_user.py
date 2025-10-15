"""
Create test user for Kaspi integration testing

Creates user with:
- Phone: 77015211545
- Password: 1234
- Role: admin
- Shop ID: 8
"""
import asyncio
from passlib.context import CryptContext
from database import get_session
from models.users import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_test_user():
    """Create test user for integration testing"""
    phone = "77015211545"
    password = "1234"
    name = "Test User"
    shop_id = 8

    async for session in get_session():
        # Check if user already exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.phone == phone)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"✅ User already exists:")
            print(f"   Phone: {existing_user.phone}")
            print(f"   Name: {existing_user.name}")
            print(f"   Role: {existing_user.role}")
            print(f"   Shop ID: {existing_user.shop_id}")
            print(f"   Active: {existing_user.is_active}")
            return existing_user

        # Create new user
        password_hash = pwd_context.hash(password)

        user = User(
            phone=phone,
            name=name,
            password_hash=password_hash,
            role="admin",
            shop_id=shop_id,
            is_active=True,
            is_superadmin=False
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        print(f"✅ Test user created successfully:")
        print(f"   Phone: {user.phone}")
        print(f"   Name: {user.name}")
        print(f"   Password: {password}")
        print(f"   Role: {user.role}")
        print(f"   Shop ID: {user.shop_id}")

        return user


if __name__ == "__main__":
    asyncio.run(create_test_user())
