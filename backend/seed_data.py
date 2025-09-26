"""
Script to seed the database with test data that matches the frontend requirements
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database import create_db_and_tables, async_session
from models import Product, Order, OrderItem, ProductType, OrderStatus


async def seed_products():
    """Seed products that match the frontend ProductCatalogFixed.jsx data"""

    async with async_session() as session:
        # Products from frontend (matching the mock data)
        products_data = [
            {
                "name": "Красный букет",
                "price": 12000 * 100,  # Convert to kopecks
                "type": ProductType.FLOWERS,
                "image_url": "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa",
                "enabled": True,
                "colors": ["red"],
                "occasions": ["birthday", "valentine"],
                "cities": ["almaty", "astana"],
                "manufacturing_time": 30,
                "shelf_life_days": 5
            },
            {
                "name": "Сердечное признание в любви",
                "price": 12000 * 100,
                "type": ProductType.FLOWERS,
                "image_url": "https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5",
                "enabled": True,
                "colors": ["pink", "red"],
                "occasions": ["valentine", "anniversary"],
                "cities": ["almaty"],
                "manufacturing_time": 25,
                "shelf_life_days": 7
            },
            {
                "name": "Шоколадный набор",
                "price": 8000 * 100,
                "type": ProductType.SWEETS,
                "image_url": "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa",
                "enabled": False,
                "colors": ["brown"],
                "occasions": ["birthday"],
                "cities": ["almaty", "astana", "shymkent"],
                "manufacturing_time": 10,
                "shelf_life_days": 30
            },
            {
                "name": "Макаронс",
                "price": 6000 * 100,
                "type": ProductType.SWEETS,
                "image_url": "https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5",
                "enabled": False,
                "colors": ["mixed"],
                "occasions": ["birthday", "celebration"],
                "cities": ["almaty"],
                "manufacturing_time": 15,
                "shelf_life_days": 7
            },
            {
                "name": "Фруктовая корзина",
                "price": 15000 * 100,
                "type": ProductType.FRUITS,
                "image_url": "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa",
                "enabled": False,
                "colors": ["green", "red", "yellow"],
                "occasions": ["get_well", "healthy"],
                "cities": ["almaty", "astana"],
                "manufacturing_time": 20,
                "shelf_life_days": 3
            },
            {
                "name": "Ягодный букет",
                "price": 10000 * 100,
                "type": ProductType.FRUITS,
                "image_url": "https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5",
                "enabled": False,
                "colors": ["red", "purple"],
                "occasions": ["healthy", "birthday"],
                "cities": ["almaty"],
                "manufacturing_time": 35,
                "shelf_life_days": 2
            }
        ]

        # Create products
        for product_data in products_data:
            product = Product(**product_data)
            session.add(product)

        await session.commit()
        print("✅ Products seeded successfully")


async def seed_orders():
    """Seed orders that match the frontend Orders.jsx data"""

    async with async_session() as session:
        # Sample orders from frontend
        orders_data = [
            {
                "order_number": "#12345",
                "customer_name": "Анна Петрова",
                "customer_phone": "+7 701 234 5678",
                "customer_email": "anna@example.com",
                "delivery_address": "ул. Абая 150, кв. 25",
                "status": OrderStatus.NEW,
                "subtotal": 20000 * 100,  # Convert to kopecks
                "delivery_cost": 1000 * 100,
                "total_amount": 21000 * 100,
                "notes": "Поздравление с днем рождения",
                "created_at": datetime.now() - timedelta(hours=2)
            },
            {
                "order_number": "#12346",
                "customer_name": "Марат Абаев",
                "customer_phone": "+7 777 987 6543",
                "delivery_address": "пр. Достык 123",
                "status": OrderStatus.PAID,
                "subtotal": 12000 * 100,
                "delivery_cost": 0,
                "total_amount": 12000 * 100,
                "created_at": datetime.now() - timedelta(hours=4)
            },
            {
                "order_number": "#12347",
                "customer_name": "Елена Смирнова",
                "customer_phone": "+7 708 111 2233",
                "delivery_address": "ул. Сатпаева 90/1",
                "status": OrderStatus.DELIVERED,
                "subtotal": 15000 * 100,
                "delivery_cost": 1500 * 100,
                "total_amount": 16500 * 100,
                "created_at": datetime.now() - timedelta(days=1)
            }
        ]

        # Create orders
        for order_data in orders_data:
            order = Order(**order_data)
            session.add(order)

        await session.flush()  # Flush to get IDs

        # Add sample order items
        orders = await session.exec("SELECT * FROM orders")
        orders_list = list(orders.all())

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


async def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")

    # Create tables first
    await create_db_and_tables()
    print("📊 Database tables created")

    # Seed data
    await seed_products()
    await seed_orders()

    print("🎉 Database seeding completed!")


if __name__ == "__main__":
    asyncio.run(main())