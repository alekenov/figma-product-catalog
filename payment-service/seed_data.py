"""
Seed script for payment_config table

Populates payment configurations for all 8 БИН.
Run this after deploying payment-service to Railway.
"""
from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import PaymentConfig


# 8 БИН configurations mapped to shop_ids
PAYMENT_CONFIGS = [
    {
        "shop_id": 8,
        "organization_bin": "891027350515",
        "is_active": True,
        "provider": "kaspi",
        "description": "Cvety.kz (Астана, Достык, 5) - Default"
    },
    {
        "shop_id": 9,
        "organization_bin": "991011000048",
        "is_active": True,
        "provider": "kaspi",
        "description": "Flowers Almaty (Алматы, Баишева, 28/1)"
    },
    {
        "shop_id": 10,
        "organization_bin": "210440028324",
        "is_active": True,
        "provider": "kaspi",
        "description": "VLVT FLOWERS (Алматы, Аль-Фараби, 53Б)"
    },
    {
        "shop_id": 11,
        "organization_bin": "590915402028",
        "is_active": True,
        "provider": "kaspi",
        "description": "Royal Flowers (5 locations across Kazakhstan)"
    },
    {
        "shop_id": 12,
        "organization_bin": "960514451575",
        "is_active": True,
        "provider": "kaspi",
        "description": "Gerim Flowers (Астана, Омарова, 21)"
    },
    {
        "shop_id": 13,
        "organization_bin": "860214400107",
        "is_active": True,
        "provider": "kaspi",
        "description": "Santini (Алматы, Суюнбая 251)"
    },
    {
        "shop_id": 14,
        "organization_bin": "920317450731",
        "is_active": True,
        "provider": "kaspi",
        "description": "Eileen Flovers (Костанай, Лермонтова, 28/1)"
    },
    {
        "shop_id": 15,
        "organization_bin": "930201350766",
        "is_active": True,
        "provider": "kaspi",
        "description": "Rosalie (Алматы, Каирбекова, 35А)"
    },
]


def seed_payment_configs():
    """Seed payment configurations"""
    print("🌱 Seeding payment configurations...")

    # Create tables first
    create_db_and_tables()

    with Session(engine) as session:
        # Check if data already exists
        existing_count = len(session.exec(select(PaymentConfig)).all())

        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing configs. Skipping seed.")
            print("   Delete existing data first if you want to re-seed.")
            return

        # Insert all configs
        for config_data in PAYMENT_CONFIGS:
            config = PaymentConfig(**config_data)
            session.add(config)
            print(f"✅ Added: shop_id={config.shop_id}, БИН={config.organization_bin}")

        session.commit()
        print(f"✅ Successfully seeded {len(PAYMENT_CONFIGS)} payment configs!")


def list_payment_configs():
    """List all payment configurations"""
    print("\n📋 Current payment configurations:\n")

    with Session(engine) as session:
        configs = session.exec(select(PaymentConfig)).all()

        if not configs:
            print("   No configurations found. Run seed_payment_configs() first.")
            return

        for config in configs:
            status = "✅ Active" if config.is_active else "❌ Inactive"
            print(f"   Shop ID: {config.shop_id:2d} | БИН: {config.organization_bin} | {status}")
            if config.description:
                print(f"               {config.description}")
            print()


def delete_all_configs():
    """Delete all payment configurations (use with caution!)"""
    print("⚠️  Deleting all payment configurations...")

    with Session(engine) as session:
        configs = session.exec(select(PaymentConfig)).all()
        count = len(configs)

        for config in configs:
            session.delete(config)

        session.commit()
        print(f"🗑️  Deleted {count} configurations")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "seed":
            seed_payment_configs()
        elif command == "list":
            list_payment_configs()
        elif command == "delete":
            confirm = input("Are you sure you want to delete all configs? (yes/no): ")
            if confirm.lower() == "yes":
                delete_all_configs()
            else:
                print("Cancelled.")
        else:
            print("Unknown command. Use: seed, list, or delete")
    else:
        print("Usage:")
        print("  python seed_data.py seed    # Seed payment configs")
        print("  python seed_data.py list    # List all configs")
        print("  python seed_data.py delete  # Delete all configs")
