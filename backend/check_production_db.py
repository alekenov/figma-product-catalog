"""
Quick script to check production database state
Run with: railway run python check_production_db.py
"""
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_db():
    # Get DATABASE_URL from environment (Railway will inject it)
    db_url = os.getenv('DATABASE_URL', '')
    if not db_url:
        print("❌ DATABASE_URL not set")
        return

    # Convert to async URL
    db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')
    print(f"🔗 Connecting to database...")

    engine = create_async_engine(db_url, echo=False)

    try:
        async with engine.begin() as conn:
            # Check tables
            print("\n📋 Tables in database:")
            result = await conn.execute(text(
                """SELECT table_name FROM information_schema.tables
                   WHERE table_schema='public'
                   ORDER BY table_name"""
            ))
            tables = [row[0] for row in result]
            for table in tables:
                print(f"  - {table}")

            print("\n📊 Data counts:")

            # Check shops
            result = await conn.execute(text('SELECT COUNT(*) FROM shop'))
            shop_count = result.scalar()
            print(f"  - Shops: {shop_count}")

            if shop_count > 0:
                result = await conn.execute(text('SELECT id, name FROM shop LIMIT 5'))
                for row in result:
                    print(f"    • Shop #{row[0]}: {row[1]}")

            # Check users
            result = await conn.execute(text('SELECT COUNT(*) FROM "user"'))
            user_count = result.scalar()
            print(f"  - Users: {user_count}")

            # Check products
            result = await conn.execute(text('SELECT COUNT(*) FROM product'))
            product_count = result.scalar()
            print(f"  - Products: {product_count}")

            # Check orders
            result = await conn.execute(text('SELECT COUNT(*) FROM "order"'))
            order_count = result.scalar()
            print(f"  - Orders: {order_count}")

            if order_count > 0:
                result = await conn.execute(text(
                    'SELECT tracking_id, "orderNumber", status FROM "order" LIMIT 5'
                ))
                print("\n  Recent orders:")
                for row in result:
                    print(f"    • {row[1]} (tracking: {row[0]}) - {row[2]}")

            print("\n✅ Database check complete")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_db())
