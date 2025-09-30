"""
Script to seed the database with test data that matches the frontend requirements
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database import create_db_and_tables, async_session
from models import (
    Product, Order, OrderItem, ProductType, OrderStatus, User, UserRole, ShopSettings, City, ProductImage,
    ProductVariant, ProductRecipe, WarehouseItem, ProductAddon, ProductBundle, PickupLocation,
    ProductReview, ReviewPhoto, CompanyReview
)
from auth_utils import get_password_hash


async def seed_products():
    """Seed products that match the frontend ProductCatalogFixed.jsx data"""

    async with async_session() as session:
        # Products from frontend (matching the mock data)
        products_data = [
            {
                "name": "Красный букет",
                "price": 12000 * 100,  # Convert to kopecks
                "type": ProductType.FLOWERS,
                "image": "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa",
                "enabled": True,
                "is_featured": True,  # Featured for homepage
                "colors": ["red"],
                "occasions": ["birthday", "valentine"],
                "cities": ["almaty", "astana"],
                "tags": ["roses", "valentine", "urgent"],  # NEW: Filter tags
                "manufacturingTime": 30,
                "shelfLife": 5
            },
            {
                "name": "Сердечное признание в любви",
                "price": 12000 * 100,
                "type": ProductType.FLOWERS,
                "image": "https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5",
                "enabled": True,
                "is_featured": True,  # Featured for homepage
                "colors": ["pink", "red"],
                "occasions": ["valentine", "anniversary"],
                "cities": ["almaty"],
                "tags": ["roses", "valentine", "budget"],  # NEW: Filter tags
                "manufacturingTime": 25,
                "shelfLife": 7
            },
            {
                "name": "Шоколадный набор",
                "price": 8000 * 100,
                "type": ProductType.SWEETS,
                "image": "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa",
                "enabled": True,
                "is_featured": False,
                "colors": ["brown"],
                "occasions": ["birthday"],
                "cities": ["almaty", "astana", "shymkent"],
                "tags": ["budget", "discount"],  # NEW
                "manufacturingTime": 10,
                "shelfLife": 30
            },
            {
                "name": "Макаронс",
                "price": 6000 * 100,
                "type": ProductType.SWEETS,
                "image": "https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5",
                "enabled": True,
                "is_featured": True,
                "colors": ["mixed"],
                "occasions": ["birthday", "celebration"],
                "cities": ["almaty"],
                "tags": ["budget"],  # NEW
                "manufacturingTime": 15,
                "shelfLife": 7
            },
            {
                "name": "Фруктовая корзина",
                "price": 15000 * 100,
                "type": ProductType.FRUITS,
                "image": "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa",
                "enabled": True,
                "is_featured": False,
                "colors": ["green", "red", "yellow"],
                "occasions": ["get_well", "healthy"],
                "cities": ["almaty", "astana"],
                "tags": ["wholesale", "mom"],  # NEW
                "manufacturingTime": 20,
                "shelfLife": 3
            },
            {
                "name": "Ягодный букет",
                "price": 10000 * 100,
                "type": ProductType.FRUITS,
                "image": "https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5",
                "enabled": True,
                "is_featured": True,
                "colors": ["red", "purple"],
                "occasions": ["healthy", "birthday"],
                "cities": ["almaty"],
                "tags": ["urgent", "mom"],  # NEW
                "manufacturingTime": 35,
                "shelfLife": 2
            }
        ]

        # Create products
        for product_data in products_data:
            product = Product(**product_data)
            session.add(product)

        await session.commit()
        print("✅ Products seeded successfully")


async def seed_product_images():
    """Seed multiple images for each product"""

    async with async_session() as session:
        try:
            # Get all products
            from sqlmodel import select
            result = await session.execute(select(Product))
            products = result.scalars().all()

            # Image URLs (reusing Figma URLs for demo)
            image_urls = [
                "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa",
                "https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5",
                "https://s3-alpha-sig.figma.com/img/a763/c5f3/3269c2bbd4306454e16d47682fec708c"
            ]

            for product in products:
                # Add 2-3 images per product
                for i in range(min(3, len(image_urls))):
                    image = ProductImage(
                        product_id=product.id,
                        url=image_urls[i],
                        order=i,
                        is_primary=(i == 0)  # First image is primary
                    )
                    session.add(image)

            await session.commit()
            print("✅ Product images seeded successfully")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding product images: {e}")
            raise


async def seed_orders():
    """Seed orders that match the frontend Orders.jsx data"""

    async with async_session() as session:
        # Sample orders from frontend (matching Order model fields)
        orders_data = [
            {
                "orderNumber": "#12345",
                "customerName": "Анна Петрова",
                "phone": "+7 701 234 5678",
                "customer_email": "anna@example.com",
                "delivery_address": "ул. Абая 150, кв. 25",
                "status": OrderStatus.NEW,
                "subtotal": 20000 * 100,  # Convert to kopecks
                "delivery_cost": 1000 * 100,
                "total": 21000 * 100,
                "notes": "Поздравление с днем рождения"
            },
            {
                "orderNumber": "#12346",
                "customerName": "Марат Абаев",
                "phone": "+7 777 987 6543",
                "delivery_address": "пр. Достык 123",
                "status": OrderStatus.PAID,
                "subtotal": 12000 * 100,
                "delivery_cost": 0,
                "total": 12000 * 100
            },
            {
                "orderNumber": "#12347",
                "customerName": "Елена Смирнова",
                "phone": "+7 708 111 2233",
                "delivery_address": "ул. Сатпаева 90/1",
                "status": OrderStatus.DELIVERED,
                "subtotal": 15000 * 100,
                "delivery_cost": 1500 * 100,
                "total": 16500 * 100
            }
        ]

        # Create orders
        for order_data in orders_data:
            order = Order(**order_data)
            session.add(order)

        await session.flush()  # Flush to get IDs

        # Add sample order items
        from sqlmodel import select
        orders_result = await session.execute(select(Order))
        orders_list = list(orders_result.scalars().all())

        if orders_list:
            # Add items to first order
            order1 = orders_list[0]
            item1 = OrderItem(
                order_id=order1.id,
                product_id=1,  # Assuming first product exists
                product_name="Красный букет",
                product_price=12000 * 100,
                quantity=1,
                item_total=12000 * 100
            )
            item2 = OrderItem(
                order_id=order1.id,
                product_id=3,
                product_name="Шоколадный набор",
                product_price=8000 * 100,
                quantity=1,
                item_total=8000 * 100
            )
            session.add_all([item1, item2])

        await session.commit()
        print("✅ Orders seeded successfully")


async def seed_users():
    """Seed initial users for authentication system"""

    async with async_session() as session:
        try:
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

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding users: {e}")
            raise


async def seed_shop_settings():
    """Seed initial shop settings"""

    async with async_session() as session:
        try:
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

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding shop settings: {e}")
            raise


async def seed_product_variants():
    """Seed product variants (sizes) for flower products"""

    async with async_session() as session:
        try:
            from sqlmodel import select

            # Get flower products (first 3 products are flowers)
            result = await session.execute(
                select(Product).where(Product.type == ProductType.FLOWERS).limit(3)
            )
            products = result.scalars().all()

            # Size variations with multipliers
            size_variants = [
                {"size": "S", "price_multiplier": 0.67},   # ~67% of base price
                {"size": "M", "price_multiplier": 1.0},    # Base price
                {"size": "L", "price_multiplier": 1.33},   # ~133% of base price
                {"size": "XL", "price_multiplier": 1.67},  # ~167% of base price
            ]

            for product in products:
                for variant_data in size_variants:
                    variant_price = int(product.price * variant_data["price_multiplier"])
                    variant = ProductVariant(
                        product_id=product.id,
                        size=variant_data["size"],
                        price=variant_price,
                        enabled=True
                    )
                    session.add(variant)

            await session.commit()
            print("✅ Product variants seeded successfully")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding product variants: {e}")
            raise


async def seed_warehouse_items():
    """Seed warehouse items for product composition"""

    async with async_session() as session:
        try:
            # Flower components
            warehouse_items = [
                {"name": "Роза розовая", "quantity": 150, "cost_price": 50000, "retail_price": 80000},
                {"name": "Пион розовый", "quantity": 80, "cost_price": 80000, "retail_price": 120000},
                {"name": "Эвкалипт", "quantity": 200, "cost_price": 15000, "retail_price": 25000},
                {"name": "Зелень декоративная", "quantity": 300, "cost_price": 10000, "retail_price": 20000},
                {"name": "Роза красная", "quantity": 200, "cost_price": 50000, "retail_price": 80000},
                {"name": "Гортензия", "quantity": 60, "cost_price": 100000, "retail_price": 150000},
                {"name": "Упаковочная бумага", "quantity": 500, "cost_price": 5000, "retail_price": 10000},
                {"name": "Лента декоративная", "quantity": 300, "cost_price": 3000, "retail_price": 7000},
            ]

            for item_data in warehouse_items:
                item = WarehouseItem(**item_data)
                session.add(item)

            await session.commit()
            print("✅ Warehouse items seeded successfully")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding warehouse items: {e}")
            raise


async def seed_product_recipes():
    """Seed product recipes (composition) for flower products"""

    async with async_session() as session:
        try:
            from sqlmodel import select

            # Get products and warehouse items
            products_result = await session.execute(
                select(Product).where(Product.type == ProductType.FLOWERS).limit(3)
            )
            products = products_result.scalars().all()

            warehouse_result = await session.execute(select(WarehouseItem))
            warehouse_items = {item.name: item.id for item in warehouse_result.scalars().all()}

            # Recipes for each product
            recipes = {
                "Красный букет": [
                    {"item": "Роза красная", "quantity": 15},
                    {"item": "Гортензия", "quantity": 3},
                    {"item": "Эвкалипт", "quantity": 5},
                    {"item": "Зелень декоративная", "quantity": 5},
                ],
                "Сердечное признание в любви": [
                    {"item": "Роза розовая", "quantity": 15},
                    {"item": "Пион розовый", "quantity": 7},
                    {"item": "Эвкалипт", "quantity": 3},
                    {"item": "Зелень декоративная", "quantity": 5},
                ],
                "Ягодный букет": [
                    {"item": "Роза красная", "quantity": 10},
                    {"item": "Пион розовый", "quantity": 5},
                    {"item": "Зелень декоративная", "quantity": 7},
                ],
            }

            for product in products:
                if product.name in recipes:
                    for component in recipes[product.name]:
                        if component["item"] in warehouse_items:
                            recipe = ProductRecipe(
                                product_id=product.id,
                                warehouse_item_id=warehouse_items[component["item"]],
                                quantity=component["quantity"],
                                is_optional=False
                            )
                            session.add(recipe)

            await session.commit()
            print("✅ Product recipes seeded successfully")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding product recipes: {e}")
            raise


async def seed_product_addons():
    """Seed product addons (additional options)"""

    async with async_session() as session:
        try:
            from sqlmodel import select

            # Get all products
            result = await session.execute(select(Product))
            products = result.scalars().all()

            # Common addons for all products
            addon_templates = [
                {"name": "Добавить упаковочную ленту и бумагу", "description": "Красивая подарочная упаковка", "price": 50000, "is_default": False},
                {"name": "Добавить открытку (бесплатно)", "description": "Поздравительная открытка с вашим текстом", "price": 0, "is_default": False},
                {"name": "Срочная доставка (2 часа)", "description": "Доставка в течение 2 часов", "price": 100000, "is_default": False},
            ]

            for product in products:
                for addon_data in addon_templates:
                    addon = ProductAddon(
                        product_id=product.id,
                        **addon_data
                    )
                    session.add(addon)

            await session.commit()
            print("✅ Product addons seeded successfully")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding product addons: {e}")
            raise


async def seed_product_bundles():
    """Seed product bundles (frequently bought together)"""

    async with async_session() as session:
        try:
            from sqlmodel import select

            # Get products
            result = await session.execute(select(Product))
            products = list(result.scalars().all())

            if len(products) < 4:
                print("⚠️ Not enough products to create bundles")
                return

            # Create bundles: flower products paired with sweets/gifts
            flower_products = [p for p in products if p.type == ProductType.FLOWERS]
            other_products = [p for p in products if p.type != ProductType.FLOWERS]

            bundle_order = 0
            for flower in flower_products[:2]:  # First 2 flower products
                for other in other_products[:3]:  # Up to 3 other products
                    bundle = ProductBundle(
                        main_product_id=flower.id,
                        bundled_product_id=other.id,
                        display_order=bundle_order,
                        enabled=True
                    )
                    session.add(bundle)
                    bundle_order += 1

            await session.commit()
            print("✅ Product bundles seeded successfully")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding product bundles: {e}")
            raise


async def seed_pickup_locations():
    """Seed pickup locations"""

    async with async_session() as session:
        try:
            locations = [
                {"city": City.ALMATY, "address": "ул. Достык, 123", "landmark": "ТЦ Dostyk Plaza", "display_order": 0},
                {"city": City.ALMATY, "address": "пр. Абая, 45", "landmark": "рядом с метро Абай", "display_order": 1},
                {"city": City.ALMATY, "address": "ул. Байзакова, 67", "landmark": "ТРЦ Mega Silk Way", "display_order": 2},
                {"city": City.ASTANA, "address": "пр. Кабанбай батыра, 15", "landmark": "ТЦ Khan Shatyr", "display_order": 3},
            ]

            for location_data in locations:
                location = PickupLocation(**location_data, enabled=True)
                session.add(location)

            await session.commit()
            print("✅ Pickup locations seeded successfully")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding pickup locations: {e}")
            raise


async def seed_product_reviews():
    """Seed product reviews"""

    async with async_session() as session:
        try:
            from sqlmodel import select

            # Get flower products
            result = await session.execute(
                select(Product).where(Product.type == ProductType.FLOWERS).limit(3)
            )
            products = result.scalars().all()

            # Review templates
            review_templates = [
                {"author_name": "Айгерим Смагулова", "rating": 5, "text": "Заказывала этот букет на день рождения мамы. Цветы пришли свежие, красивые, ровно как на фотографии! Мама была в восторге. Спасибо большое за качество и сервис!", "likes": 24, "dislikes": 1},
                {"author_name": "Дмитрий Петров", "rating": 5, "text": "Отличный букет! Доставили вовремя, цветы свежие и ароматные. Жена очень довольна. Обязательно буду заказывать ещё.", "likes": 18, "dislikes": 0},
                {"author_name": "Светлана Ким", "rating": 4, "text": "Букет красивый, но немного меньше, чем ожидала по размеру M. В остальном всё отлично - цветы свежие, доставка быстрая.", "likes": 12, "dislikes": 2},
                {"author_name": "Алия Нурбекова", "rating": 5, "text": "Очень красивый букет, цветы свежие и ароматные. Доставка быстрая, курьер вежливый. Рекомендую!", "likes": 15, "dislikes": 0},
                {"author_name": "Марат Тулеев", "rating": 4, "text": "Хороший букет, но цена немного завышена. В целом доволен покупкой.", "likes": 8, "dislikes": 3},
            ]

            # Image URL for review photos
            review_image_url = "https://s3-alpha-sig.figma.com/img/a763/c5f3/3269c2bbd4306454e16d47682fec708c"

            for product in products:
                # Add 3-5 reviews per product
                for i, review_data in enumerate(review_templates[:5]):
                    review = ProductReview(
                        product_id=product.id,
                        **review_data
                    )
                    session.add(review)
                    await session.flush()  # Get review ID

                    # Add photo to first review only
                    if i == 0:
                        photo = ReviewPhoto(
                            review_id=review.id,
                            url=review_image_url,
                            order=0
                        )
                        session.add(photo)

            await session.commit()
            print("✅ Product reviews seeded successfully")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding product reviews: {e}")
            raise


async def seed_company_reviews():
    """Seed company reviews"""

    async with async_session() as session:
        try:
            reviews = [
                {"author_name": "Алия Нурбекова", "rating": 5, "text": "Заказываю цветы в этой компании уже третий раз. Всегда свежие цветы, вежливые курьеры, быстрая доставка. Очень рекомендую!", "likes": 45, "dislikes": 1},
                {"author_name": "Марат Тулеев", "rating": 5, "text": "Лучший сервис доставки цветов в Астане! Всегда выручают, даже когда заказываешь в последний момент.", "likes": 38, "dislikes": 0},
                {"author_name": "Елена Смирнова", "rating": 4, "text": "Хорошая компания, качественные цветы. Единственный минус - иногда долго отвечают в WhatsApp.", "likes": 22, "dislikes": 3},
                {"author_name": "Асель Жумабаева", "rating": 5, "text": "Заказывала букет на свадьбу подруги - получилось шикарно! Флористы настоящие профессионалы.", "likes": 31, "dislikes": 0},
                {"author_name": "Дамир Абаев", "rating": 5, "text": "Отличный магазин! Приятные цены, быстрая доставка, свежие цветы. Буду заказывать ещё.", "likes": 19, "dislikes": 1},
            ]

            for review_data in reviews:
                review = CompanyReview(**review_data)
                session.add(review)

            await session.commit()
            print("✅ Company reviews seeded successfully")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding company reviews: {e}")
            raise


async def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")

    # Create tables first
    await create_db_and_tables()
    print("📊 Database tables created")

    # Seed data in order
    await seed_users()
    await seed_shop_settings()
    await seed_products()
    await seed_product_images()
    await seed_warehouse_items()        # NEW: Warehouse items for recipes
    await seed_product_variants()       # NEW: S/M/L/XL sizes
    await seed_product_recipes()        # NEW: Composition/ingredients
    await seed_product_addons()         # NEW: Additional options
    await seed_product_bundles()        # NEW: Frequently bought together
    await seed_pickup_locations()       # NEW: Pickup addresses
    await seed_product_reviews()        # NEW: Product reviews
    await seed_company_reviews()        # NEW: Company reviews
    await seed_orders()

    print("🎉 Database seeding completed!")


if __name__ == "__main__":
    asyncio.run(main())