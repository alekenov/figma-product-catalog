"""
Seed data for local SQLite database development.
Creates test shop, users, products, and clients.
"""
import asyncio
from sqlmodel import select
from database import async_session
from models import (
    Shop, User, Product, ProductType, Client,
    UserRole, City
)
from auth_utils import get_password_hash

# Test data configuration
SHOP_ID = 8
ADMIN_PHONE = "+77015211545"
ADMIN_PASSWORD = "1234"  # Test password for local dev
TEST_CLIENT_TELEGRAM_ID = "123456789"


async def create_shop(owner_id: int):
    """Create test shop with owner."""
    async with async_session() as session:
        # Check if shop already exists
        result = await session.execute(
            select(Shop).where(Shop.id == SHOP_ID)
        )
        existing_shop = result.scalars().first()

        if existing_shop:
            print(f"✅ Shop #{SHOP_ID} already exists: {existing_shop.name}")
            return existing_shop

        shop = Shop(
            id=SHOP_ID,
            name="Cvety.kz Test Shop",
            owner_id=owner_id,  # Link to admin user
            address="Алматы, ул. Абая 150",
            phone="+77012345678",
            city=City.ALMATY,
            is_active=True,
            delivery_cost=150000,  # 1500 tenge in kopecks
            free_delivery_amount=1000000,  # 10000 tenge in kopecks
            pickup_available=True,
            delivery_available=True
        )

        session.add(shop)
        await session.commit()
        await session.refresh(shop)
        print(f"✅ Created shop: {shop.name} (ID: {shop.id}, Owner ID: {owner_id})")
        return shop


async def create_admin_user():
    """Create admin user WITHOUT shop_id (will be set later)."""
    async with async_session() as session:
        # Check if admin exists
        result = await session.execute(
            select(User).where(User.phone == ADMIN_PHONE)
        )
        existing_user = result.scalars().first()

        if existing_user:
            print(f"✅ Admin user already exists: {existing_user.phone}")
            return existing_user

        admin = User(
            name="Test Admin",
            phone=ADMIN_PHONE,
            password_hash=get_password_hash(ADMIN_PASSWORD),
            role=UserRole.DIRECTOR,
            is_active=True,
            is_superadmin=False,
            shop_id=None  # Will be set after shop creation
        )

        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        print(f"✅ Created admin user: {admin.phone} (password: {ADMIN_PASSWORD})")
        return admin


async def link_admin_to_shop(admin_id: int, shop_id: int):
    """Link admin user to shop after shop creation."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == admin_id)
        )
        admin = result.scalars().first()

        if not admin:
            print(f"❌ Admin user {admin_id} not found")
            return

        admin.shop_id = shop_id
        session.add(admin)
        await session.commit()
        print(f"✅ Linked admin {admin.phone} to shop #{shop_id}")


async def create_test_products():
    """Create test products."""
    async with async_session() as session:
        # Check if products already exist
        result = await session.execute(
            select(Product).where(Product.shop_id == SHOP_ID)
        )
        existing_products = result.scalars().all()

        if existing_products:
            print(f"✅ {len(existing_products)} products already exist")
            return existing_products

        products = [
            Product(
                name="Букет роз (21 шт)",
                description="Классический букет из 21 красной розы",
                price=1500000,  # 15000 tenge in kopecks
                type=ProductType.FLOWERS,
                enabled=True,
                shop_id=SHOP_ID,
                image="https://flower-shop-images.alekenov.workers.dev/test-roses-21.png"
            ),
            Product(
                name="Букет тюльпанов (25 шт)",
                description="Весенний букет из 25 желтых тюльпанов",
                price=1200000,  # 12000 tenge
                type=ProductType.FLOWERS,
                enabled=True,
                shop_id=SHOP_ID,
                image="https://flower-shop-images.alekenov.workers.dev/test-tulips-25.png"
            ),
            Product(
                name="Букет невесты",
                description="Элегантный свадебный букет из белых роз и пионов",
                price=2500000,  # 25000 tenge
                type=ProductType.FLOWERS,
                enabled=True,
                shop_id=SHOP_ID,
                image="https://flower-shop-images.alekenov.workers.dev/test-bride-bouquet.png"
            ),
            Product(
                name="Букет ромашек (11 шт)",
                description="Летний букет из 11 ромашек",
                price=800000,  # 8000 tenge
                type=ProductType.FLOWERS,
                enabled=True,
                shop_id=SHOP_ID,
                image="https://flower-shop-images.alekenov.workers.dev/test-daisies-11.png"
            ),
            Product(
                name="Набор конфет Raffaello",
                description="Элитные конфеты с кокосовой стружкой и миндалем",
                price=300000,  # 3000 tenge
                type=ProductType.SWEETS,
                enabled=True,
                shop_id=SHOP_ID,
                image="https://flower-shop-images.alekenov.workers.dev/test-raffaello.png"
            ),
        ]

        for product in products:
            session.add(product)

        await session.commit()

        for product in products:
            await session.refresh(product)

        print(f"✅ Created {len(products)} test products")
        return products


async def create_test_client():
    """Create test client for Telegram bot authorization."""
    async with async_session() as session:
        # Check if client exists
        result = await session.execute(
            select(Client).where(
                Client.telegram_user_id == TEST_CLIENT_TELEGRAM_ID,
                Client.shop_id == SHOP_ID
            )
        )
        existing_client = result.scalars().first()

        if existing_client:
            print(f"✅ Test client already exists: {existing_client.phone}")
            return existing_client

        client = Client(
            phone=ADMIN_PHONE,
            customerName="Test User",
            shop_id=SHOP_ID,
            telegram_user_id=TEST_CLIENT_TELEGRAM_ID,
            telegram_username="test_user",
            telegram_first_name="Test",
            notes="Auto-generated test client for local development"
        )

        session.add(client)
        await session.commit()
        await session.refresh(client)
        print(f"✅ Created test client: {client.phone} (Telegram ID: {client.telegram_user_id})")
        return client


async def main():
    """Run all seed data creation."""
    print("🌱 Loading seed data for local development...")
    print("")

    try:
        # Step 1: Create admin user WITHOUT shop_id
        admin = await create_admin_user()
        print("")

        # Step 2: Create shop with admin as owner
        shop = await create_shop(owner_id=admin.id)
        print("")

        # Step 3: Link admin to shop
        await link_admin_to_shop(admin.id, shop.id)
        print("")

        # Step 4: Create test products
        products = await create_test_products()
        print("")

        # Step 5: Create test client
        client = await create_test_client()
        print("")

        print("=" * 50)
        print("✅ Seed data loaded successfully!")
        print("=" * 50)
        print("")
        print("📝 Test Credentials:")
        print(f"   Admin Login: {ADMIN_PHONE}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print("")
        print(f"   Shop ID: {SHOP_ID}")
        print(f"   Products: {len(products) if isinstance(products, list) else 'existing'}")
        print(f"   Test Telegram ID: {TEST_CLIENT_TELEGRAM_ID}")
        print("")

    except Exception as e:
        print(f"❌ Error loading seed data: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
