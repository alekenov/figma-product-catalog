"""
Superadmin seed data - creates superadmin user for platform management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from models import User, Shop
from models.enums import UserRole
from auth_utils import get_password_hash


async def seed_superadmin(session: AsyncSession):
    """
    Create superadmin user if doesn't exist.
    Superadmin credentials:
    - Phone: +77015211545 (with + prefix for frontend compatibility)
    - Password: 1234
    - Role: DIRECTOR
    - is_superadmin: True
    """
    superadmin_phone = "+77015211545"

    # Check if superadmin already exists
    result = await session.execute(
        select(User).where(User.phone == superadmin_phone)
    )
    existing_superadmin = result.scalar_one_or_none()

    if existing_superadmin:
        # Always update is_superadmin flag and password to ensure correct credentials
        needs_update = False

        if not existing_superadmin.is_superadmin:
            print(f"  🔧 Promoting existing user {superadmin_phone} to superadmin...")
            existing_superadmin.is_superadmin = True
            needs_update = True

        # Always ensure password is correct (in case user was created with different password)
        correct_password_hash = get_password_hash("1234")
        if existing_superadmin.password_hash != correct_password_hash:
            print(f"  🔑 Updating superadmin password...")
            existing_superadmin.password_hash = correct_password_hash
            needs_update = True

        if needs_update:
            await session.commit()
            print(f"  ✅ Superadmin {superadmin_phone} updated successfully")
        else:
            print(f"  ℹ️  Superadmin {superadmin_phone} already exists with correct credentials")
        return

    print(f"  👤 Creating superadmin user...")

    # Get test shop (shop_id=8) for superadmin
    result = await session.execute(
        select(Shop).where(Shop.id == 8)
    )
    test_shop = result.scalar_one_or_none()

    # Create superadmin user
    superadmin = User(
        name="Алексей Кенов",
        phone=superadmin_phone,
        password_hash=get_password_hash("1234"),  # Password: 1234
        role=UserRole.DIRECTOR,
        is_superadmin=True,
        shop_id=test_shop.id if test_shop else None  # Link to test shop if it exists
    )
    session.add(superadmin)
    await session.commit()

    print(f"  ✅ Superadmin created:")
    print(f"     📱 Phone: +77015211545")
    print(f"     🔑 Password: 1234")
    print(f"     🛡️  is_superadmin: True")
    print(f"     🏪 shop_id: {superadmin.shop_id}")
