#!/usr/bin/env python3
"""
🚀 Phase 2 Migration: Update Railway paymentconfig with production shop_ids

This script:
1. Deletes old test shop_ids (8-15)
2. Inserts production shop_ids (121038, 576631, 75509, 69292, 49237, 56195, 71691)
3. Verifies the update was successful

Usage:
  python migrate_production_shop_ids.py
"""
from sqlalchemy import text
from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import PaymentConfig
from datetime import datetime


# Production shop_ids and БINs (from Bitrix research 2025-11-03)
PRODUCTION_CONFIGS = [
    {
        "shop_id": 121038,
        "organization_bin": "920317450731",
        "provider": "kaspi",
        "seller_name": "Eileen flowers",
        "city": "Костанай",
    },
    {
        "shop_id": 576631,
        "organization_bin": "210440028324",
        "provider": "kaspi",
        "seller_name": "VLVT Flowers Almaty",
        "city": "Алматы",
    },
    {
        "shop_id": 75509,
        "organization_bin": "860214400107",
        "provider": "kaspi",
        "seller_name": "Santini",
        "city": "Алматы",
    },
    {
        "shop_id": 69292,
        "organization_bin": "960514451575",
        "provider": "kaspi",
        "seller_name": "Gerim Flowers",
        "city": "Астана",
    },
    {
        "shop_id": 49237,
        "organization_bin": "930201350766",
        "provider": "kaspi",
        "seller_name": "Rosalie",
        "city": "Алматы",
    },
    {
        "shop_id": 56195,
        "organization_bin": "590915402028",
        "provider": "kaspi",
        "seller_name": "Royal Flowers Almaty",
        "city": "Алматы",
    },
    {
        "shop_id": 71691,
        "organization_bin": "991011000048",
        "provider": "kaspi",
        "seller_name": "Flowers.Almaty",
        "city": "Алматы",
    },
]


def migrate():
    """Execute Phase 2 migration"""
    print("\n" + "="*70)
    print("🚀 PHASE 2 MIGRATION: Production shop_ids Update")
    print("="*70)

    # Ensure tables exist
    create_db_and_tables()

    with Session(engine) as session:
        try:
            print("\n📋 Step 1: Current paymentconfig state")
            print("-" * 70)

            current_configs = session.exec(select(PaymentConfig)).all()
            print(f"Total configurations: {len(current_configs)}")

            for config in current_configs:
                print(f"  • shop_id={config.shop_id}, БИН={config.organization_bin}, active={config.is_active}")

            # Delete old test shop_ids (8-15)
            print("\n🗑️  Step 2: Delete test shop_ids (8-15)")
            print("-" * 70)

            test_shop_ids = [8, 9, 10, 11, 12, 13, 14, 15]
            deleted_count = 0

            for shop_id in test_shop_ids:
                config = session.exec(
                    select(PaymentConfig).where(PaymentConfig.shop_id == shop_id)
                ).first()

                if config:
                    session.delete(config)
                    deleted_count += 1
                    print(f"  🗑️  Deleted shop_id={shop_id}")

            session.commit()
            print(f"✅ Deleted {deleted_count} test configurations")

            # Insert production shop_ids
            print("\n✨ Step 3: Insert production shop_ids")
            print("-" * 70)

            for config_data in PRODUCTION_CONFIGS:
                # Check if already exists
                existing = session.exec(
                    select(PaymentConfig).where(PaymentConfig.shop_id == config_data["shop_id"])
                ).first()

                if existing:
                    print(f"  ⚠️  shop_id={config_data['shop_id']} already exists, updating...")
                    existing.organization_bin = config_data["organization_bin"]
                    existing.is_active = True
                    session.add(existing)
                else:
                    new_config = PaymentConfig(
                        shop_id=config_data["shop_id"],
                        organization_bin=config_data["organization_bin"],
                        is_active=True,
                        provider=config_data["provider"],
                        device_token=None,  # Will be added later
                    )
                    session.add(new_config)
                    print(f"  ✅ Added: {config_data['seller_name']} (shop_id={config_data['shop_id']})")

            session.commit()
            print(f"✅ Successfully inserted/updated {len(PRODUCTION_CONFIGS)} production configurations")

            # Verify the update
            print("\n✔️  Step 4: Verify configuration")
            print("-" * 70)

            final_configs = session.exec(
                select(PaymentConfig).order_by(PaymentConfig.shop_id)
            ).all()

            print(f"\nFinal paymentconfig state ({len(final_configs)} total):\n")

            almaty_count = 0
            astana_count = 0
            kostanai_count = 0

            for i, config in enumerate(final_configs, 1):
                # Find the corresponding seller info
                seller_info = next(
                    (c for c in PRODUCTION_CONFIGS if c["shop_id"] == config.shop_id),
                    None
                )

                if seller_info:
                    seller = seller_info["seller_name"]
                    city = seller_info["city"]

                    if city == "Алматы":
                        almaty_count += 1
                    elif city == "Астана":
                        astana_count += 1
                    elif city == "Костанай":
                        kostanai_count += 1

                    print(f"  {i}. {seller:25} (shop_id={config.shop_id}, БИН={config.organization_bin}) ✅")
                else:
                    print(f"  {i}. Unknown shop_id={config.shop_id}, БИН={config.organization_bin} ⚠️")

            print(f"\n📊 Distribution by city:")
            print(f"  • Алматы: {almaty_count} sellers")
            print(f"  • Астана: {astana_count} sellers")
            print(f"  • Костанай: {kostanai_count} sellers")

            print("\n" + "="*70)
            print("✅ Phase 2 Migration COMPLETED Successfully!")
            print("="*70)
            print("\n📌 Next Steps:")
            print("  1. Verify this database update in Railway Dashboard")
            print("  2. Deploy payment-service to Railway (git push)")
            print("  3. Update ApiClient.php in production (Phase 3)")
            print("  4. Test payment routing for all 7 sellers (Phase 6)")
            print()

            return True

        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            session.rollback()
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = migrate()
    exit(0 if success else 1)
