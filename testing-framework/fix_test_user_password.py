"""
Fix test user password hash.
Updates existing test user (77088888888) with proper bcrypt hash for "test123"
"""
import asyncio
from sqlalchemy import select
from database import get_session
from models import User
from auth_utils import get_password_hash


async def fix_password():
    async for session in get_session():
        # Find test user
        result = await session.execute(
            select(User).where(User.phone == "77088888888")
        )
        user = result.scalar_one_or_none()

        if not user:
            print("❌ Test user not found")
            return

        print(f"Found user: {user.name} ({user.phone})")
        print(f"Current hash: {user.password_hash[:30]}...")

        # Update password hash
        new_hash = get_password_hash("test123")
        user.password_hash = new_hash

        await session.commit()
        print(f"✅ Password updated!")
        print(f"New hash: {new_hash[:30]}...")
        break


if __name__ == "__main__":
    asyncio.run(fix_password())
