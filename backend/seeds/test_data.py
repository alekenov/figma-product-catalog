"""
Seed test data for testing framework.
Creates shop_id=8 with products for automated testing.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Shop, Product, WarehouseItem, User
from models.enums import UserRole, ProductType
from auth_utils import get_password_hash


async def seed_test_shop(session: AsyncSession):
    """
    Create test shop with products for testing framework.
    Safe to run multiple times.
    """
    shop_id = 8
    test_phone = "77088888888"  # Different from auth test phone

    # Check if shop already exists
    result = await session.execute(
        select(Shop).where(Shop.id == shop_id)
    )
    existing_shop = result.scalar_one_or_none()

    if existing_shop:
        print(f"  ℹ️  Test shop {shop_id} already exists, skipping...")

        # But still check and fix the test user password if needed
        result = await session.execute(
            select(User).where(User.phone == test_phone)
        )
        test_user = result.scalar_one_or_none()

        if test_user and len(test_user.password_hash) < 60:
            print(f"  🔧 Fixing invalid password hash for test user...")
            test_user.password_hash = get_password_hash("test123")
            await session.commit()
            print(f"  ✅ Password hash fixed!")

        return

    print(f"  🏪 Creating test shop {shop_id}...")

    # Check if test user already exists
    result = await session.execute(
        select(User).where(User.phone == test_phone)
    )
    test_user = result.scalar_one_or_none()

    if not test_user:
        # Create test director user first (without shop_id to avoid circular dependency)
        test_user = User(
            name="Test Admin",
            phone=test_phone,
            password_hash=get_password_hash("test123"),  # Password: test123
            role=UserRole.DIRECTOR,  # Changed from ADMIN to DIRECTOR for compatibility
            shop_id=None  # Set to None initially
        )
        session.add(test_user)
        await session.flush()  # Flush to get user ID
        print(f"  👤 Created test user {test_user.phone}")
    else:
        print(f"  ℹ️  Test user {test_user.phone} already exists")

    # Create test shop with owner_id
    shop = Shop(
        id=shop_id,
        name="Тестовый цветочный магазин",
        description="Магазин для автоматического тестирования AI системы",
        owner_id=test_user.id,  # Set owner_id
        phone="+77011234567",
        email="test@flowers.test",
        address="ул. Тестовая 1, Алматы",
        weekday_start="09:00",
        weekday_end="21:00",
        weekend_start="10:00",
        weekend_end="20:00",
        delivery_price=150000  # 1500 тенге
    )
    session.add(shop)
    await session.flush()

    # Update user with shop_id now that shop exists
    test_user.shop_id = shop_id
    await session.flush()

    print(f"  ✅ Shop '{shop.name}' created with owner user {test_user.phone}")

    # Create test products with various prices
    test_products = [
        # Budget range (5000-12000 tenge)
        {
            "name": "Букет 'Нежность' из 7 роз",
            "type": ProductType.FLOWERS,
            "price": 900000,  # 9000 tenge
            "description": "Классический букет из 7 розовых роз с зеленью",
            "enabled": True
        },
        {
            "name": "Букет 'Весенний' из тюльпанов",
            "type": ProductType.FLOWERS,
            "price": 800000,  # 8000 tenge
            "description": "15 разноцветных тюльпанов",
            "enabled": True
        },
        {
            "name": "Букет 'Радость' из гербер",
            "type": ProductType.FLOWERS,
            "price": 700000,  # 7000 tenge
            "description": "Яркие герберы с зеленью",
            "enabled": True
        },
        {
            "name": "Букет 'Микс' эконом",
            "type": ProductType.FLOWERS,
            "price": 600000,  # 6000 tenge
            "description": "Микс из хризантем и альстромерий",
            "enabled": True
        },

        # Medium range (12000-25000 tenge)
        {
            "name": "Букет '15 роз' классика",
            "type": ProductType.FLOWERS,
            "price": 1500000,  # 15000 tenge
            "description": "15 красных роз премиум класса",
            "enabled": True
        },
        {
            "name": "Букет 'Романтика' из роз и лилий",
            "type": ProductType.FLOWERS,
            "price": 1800000,  # 18000 tenge
            "description": "Роскошный букет из роз и белых лилий",
            "enabled": True
        },
        {
            "name": "Букет 'Ассорти премиум'",
            "type": ProductType.FLOWERS,
            "price": 2000000,  # 20000 tenge
            "description": "Эксклюзивный микс премиум цветов",
            "enabled": True
        },
        {
            "name": "Букет 'Пионы'",
            "type": ProductType.FLOWERS,
            "price": 2200000,  # 22000 tenge
            "description": "Нежные пионы в дизайнерской упаковке",
            "enabled": True
        },

        # Premium range (25000+ tenge)
        {
            "name": "Букет '25 роз' VIP",
            "type": ProductType.FLOWERS,
            "price": 3000000,  # 30000 tenge
            "description": "25 роз премиум-класса с эвкалиптом",
            "enabled": True
        },
        {
            "name": "Букет '51 роза'",
            "type": ProductType.FLOWERS,
            "price": 5500000,  # 55000 tenge
            "description": "Роскошный букет из 51 розы",
            "enabled": True
        },
        {
            "name": "Букет 'Белые розы премиум'",
            "type": ProductType.FLOWERS,
            "price": 3500000,  # 35000 tenge
            "description": "Изысканный букет белых роз для особых случаев",
            "enabled": True
        },
        {
            "name": "Букет 'Орхидеи экзотик'",
            "type": ProductType.FLOWERS,
            "price": 4500000,  # 45000 tenge
            "description": "Экзотические орхидеи в премиум оформлении",
            "enabled": True
        },

        # Additional categories
        {
            "name": "Коробка конфет 'Рафаэлло'",
            "type": ProductType.SWEETS,
            "price": 300000,  # 3000 tenge
            "description": "Конфеты Rafaello 150г",
            "enabled": True
        },
        {
            "name": "Коробка конфет 'Ferrero Rocher'",
            "type": ProductType.SWEETS,
            "price": 450000,  # 4500 tenge
            "description": "Элитные конфеты Ferrero Rocher",
            "enabled": True
        },
        {
            "name": "Плюшевый мишка средний",
            "type": ProductType.GIFTS,
            "price": 500000,  # 5000 tenge
            "description": "Милый плюшевый мишка 40см",
            "enabled": True
        },
    ]

    created_products = []
    for product_data in test_products:
        product = Product(
            shop_id=shop_id,
            **product_data
        )
        session.add(product)
        created_products.append(product)

    await session.flush()
    print(f"  ✅ Created {len(created_products)} test products")

    # Warehouse items not needed for AI customer service testing
    # (inventory management is not used in AI conversations)

    await session.commit()
    print(f"  ✨ Test shop {shop_id} setup complete!")


async def seed_test_order(session: AsyncSession):
    """
    Create a test order for 07_modify_order scenario.
    Phone: 77012345678
    Delivery: Tomorrow at 14:00
    """
    from datetime import datetime, timedelta
    from models.orders import Order, OrderItem
    from models.enums import OrderStatus
    import random

    shop_id = 8
    test_phone = "+77012345678"

    # Check if order already exists for this phone
    result = await session.execute(
        select(Order).where(
            Order.phone == test_phone,
            Order.shop_id == shop_id
        )
    )
    existing_order = result.scalar_one_or_none()

    if existing_order:
        print(f"  ℹ️  Test order for {test_phone} already exists (tracking: {existing_order.tracking_id})")
        return existing_order.tracking_id

    # Get product ID 21 (Букет 'Романтика')
    result = await session.execute(
        select(Product).where(Product.id == 21, Product.shop_id == shop_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        print(f"  ⚠️  Product 21 not found for shop_id={shop_id}, skipping test order")
        return None

    # Create order for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    delivery_datetime = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)

    # Generate tracking_id
    tracking_id = f"{random.randint(100000000, 999999999)}"

    order = Order(
        shop_id=shop_id,
        tracking_id=tracking_id,
        orderNumber=f"#TEST-{tracking_id[:5]}",
        customerName="Айгуль Тестовая",
        phone=test_phone,
        delivery_address="ул. Абая, дом 10, кв. 5",
        delivery_date=delivery_datetime,
        scheduled_time="14:00",
        subtotal=product.price,
        total=product.price,
        status=OrderStatus.ACCEPTED,  # Order is accepted and ready for delivery
        notes="Тестовый заказ для сценария 07_modify_order.yaml"
    )
    session.add(order)
    await session.flush()

    # Add order item
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=product.name,
        product_price=product.price,
        quantity=1,
        item_total=product.price
    )
    session.add(order_item)

    await session.commit()
    print(f"  ✅ Created test order {tracking_id} for {test_phone}")
    print(f"     Delivery: {delivery_datetime.strftime('%Y-%m-%d %H:%M')}")
    print(f"     Product: {product.name}")
    return tracking_id
