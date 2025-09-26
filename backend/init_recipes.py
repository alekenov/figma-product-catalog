#!/usr/bin/env python3
"""Initialize product recipes with warehouse components"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from sqlmodel import select
from database import get_session
from models import Product, WarehouseItem, ProductRecipe


async def init_recipes():
    """Initialize recipes for existing products"""

    async for session in get_session():
        # Get all products and warehouse items
        products_result = await session.execute(select(Product))
        products = products_result.scalars().all()

        warehouse_result = await session.execute(select(WarehouseItem))
        warehouse_items = warehouse_result.scalars().all()

        # Create warehouse items lookup by name
        warehouse_lookup = {item.name.lower(): item for item in warehouse_items}

        print("📋 Initializing product recipes...")

        # Define recipes for each product
        recipes_config = [
            {
                "product_name": "Красные розы",
                "components": [
                    ("красная роза", 25, False),
                    ("эвкалипт (ветка)", 3, False),
                ]
            },
            {
                "product_name": "Букет белых лилий",
                "components": [
                    ("розовая лилия", 7, False),  # Using розовая лилия as substitute
                    ("белая хризантема", 3, False),
                    ("эвкалипт (ветка)", 2, False),
                ]
            },
            {
                "product_name": "Микс цветов",
                "components": [
                    ("красная роза", 5, False),
                    ("белая роза", 5, False),
                    ("розовая роза", 5, False),
                    ("эвкалипт (ветка)", 3, False),
                ]
            },
            {
                "product_name": "Орхидеи",
                "components": [
                    ("белая орхидея", 3, False),
                    ("эвкалипт (ветка)", 1, True),  # Optional decoration
                ]
            },
            {
                "product_name": "Тюльпаны",
                "components": [
                    ("розовая роза", 15, False),  # Using розовая роза as substitute for tulips
                    ("эвкалипт (ветка)", 2, True),
                ]
            },
            {
                "product_name": "Букет №1",
                "components": [
                    ("красная роза", 15, False),
                    ("белая роза", 10, False),
                    ("эвкалипт (ветка)", 5, False),
                ]
            },
            {
                "product_name": "Букет №2",
                "components": [
                    ("розовая роза", 20, False),
                    ("белая хризантема", 5, False),
                    ("эвкалипт (ветка)", 3, False),
                ]
            },
            {
                "product_name": "Букет №3",
                "components": [
                    ("белая роза", 30, False),
                    ("эвкалипт (ветка)", 5, False),
                ]
            },
            {
                "product_name": "Розовый букет",
                "components": [
                    ("розовая роза", 25, False),
                    ("белая роза", 5, False),
                    ("эвкалипт (ветка)", 3, False),
                ]
            },
            {
                "product_name": "Белый букет",
                "components": [
                    ("белая роза", 20, False),
                    ("белая хризантема", 10, False),
                    ("эвкалипт (ветка)", 4, False),
                ]
            },
            {
                "product_name": "Желтый букет",
                "components": [
                    ("желтая роза", 25, False),
                    ("эвкалипт (ветка)", 3, False),
                ]
            },
            {
                "product_name": "Букет с лилиями",
                "components": [
                    ("розовая лилия", 5, False),
                    ("белая роза", 10, False),
                    ("эвкалипт (ветка)", 3, False),
                ]
            },
        ]

        # Process each product
        for product in products:
            # Find matching recipe config
            recipe_config = None
            for config in recipes_config:
                if config["product_name"].lower() in product.name.lower():
                    recipe_config = config
                    break

            if not recipe_config:
                # Default recipe for products without specific config
                print(f"  ⚠️  No recipe config for: {product.name}, using default")
                recipe_config = {
                    "product_name": product.name,
                    "components": [
                        ("красная роза", 15, False),
                        ("эвкалипт (ветка)", 2, False),
                    ]
                }

            # Check if product already has recipes
            existing_result = await session.execute(
                select(ProductRecipe).where(ProductRecipe.product_id == product.id)
            )
            if existing_result.scalars().first():
                print(f"  ✓ {product.name} - already has recipe")
                continue

            # Create recipes
            created_count = 0
            for component_name, quantity, is_optional in recipe_config["components"]:
                warehouse_item = warehouse_lookup.get(component_name.lower())

                if not warehouse_item:
                    print(f"    ⚠️  Component not found: {component_name}")
                    continue

                recipe = ProductRecipe(
                    product_id=product.id,
                    warehouse_item_id=warehouse_item.id,
                    quantity=quantity,
                    is_optional=is_optional
                )
                session.add(recipe)
                created_count += 1

            if created_count > 0:
                print(f"  ✅ {product.name} - added {created_count} components")
            else:
                print(f"  ❌ {product.name} - no components added")

        await session.commit()
        print("\n🎉 Product recipes initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_recipes())