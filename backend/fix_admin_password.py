"""Fix admin user password for testing"""
import asyncio
from sqlmodel import select
from database import get_session
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

async def fix_admin_password():
    """Update admin password to testpass123"""
    async for session in get_session():
        try:
            # Find admin user
            result = await session.execute(
                select(User).where(User.phone == '+77015211545')
            )
            user = result.scalar_one_or_none()

            if not user:
                print("❌ Admin user not found!")
                return

            # Update password
            user.password_hash = pwd_context.hash('testpass123')
            session.add(user)
            await session.commit()

            print(f"✅ Password updated for user: {user.name} ({user.phone})")
            print(f"   Role: {user.role}")
            print(f"   Shop ID: {user.shop_id}")

        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()

        break

if __name__ == "__main__":
    asyncio.run(fix_admin_password())
