from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col
from database import get_session
from models import (
    Product, ProductRecipe, ProductRecipeCreate, ProductRecipeRead, ProductRecipeUpdate,
    ProductWithRecipe, WarehouseItem, WarehouseItemRead
)

router = APIRouter()


@router.get("/products/{product_id}/recipe", response_model=ProductWithRecipe)
async def get_product_recipe(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int
):
    """Get product with its recipe and availability info"""

    # Get product
    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get recipes with warehouse items
    recipes_result = await session.execute(
        select(ProductRecipe, WarehouseItem)
        .join(WarehouseItem, ProductRecipe.warehouse_item_id == WarehouseItem.id)
        .where(ProductRecipe.product_id == product_id)
    )

    recipes_with_items = recipes_result.all()

    # Calculate total cost and availability
    total_cost = 0
    can_produce = True
    max_quantity = float('inf')

    recipes = []
    for recipe, warehouse_item in recipes_with_items:
        # Calculate how many products we can make with this component
        if recipe.quantity > 0:
            possible_quantity = warehouse_item.quantity // recipe.quantity
            max_quantity = min(max_quantity, possible_quantity)

        # Check if we have enough for at least one product
        if warehouse_item.quantity < recipe.quantity and not recipe.is_optional:
            can_produce = False

        # Add to total cost
        total_cost += warehouse_item.cost_price * recipe.quantity

        # Create recipe response with warehouse item details
        recipe_read = ProductRecipeRead(
            **recipe.model_dump(),
            warehouse_item=WarehouseItemRead(**warehouse_item.model_dump())
        )
        recipes.append(recipe_read)

    # If no recipes, we can't produce
    if not recipes:
        max_quantity = 0
    elif max_quantity == float('inf'):
        max_quantity = 0

    return ProductWithRecipe(
        **product.model_dump(),
        recipes=recipes,
        total_cost=total_cost,
        can_produce=can_produce,
        max_quantity=int(max_quantity)
    )


@router.post("/products/{product_id}/recipe", response_model=ProductRecipeRead)
async def add_recipe_component(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    recipe: ProductRecipeCreate
):
    """Add a component to product recipe"""

    # Verify product exists
    product_result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    if not product_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found")

    # Verify warehouse item exists
    warehouse_result = await session.execute(
        select(WarehouseItem).where(WarehouseItem.id == recipe.warehouse_item_id)
    )
    warehouse_item = warehouse_result.scalar_one_or_none()
    if not warehouse_item:
        raise HTTPException(status_code=404, detail="Warehouse item not found")

    # Check if recipe already exists for this combination
    existing_result = await session.execute(
        select(ProductRecipe)
        .where(ProductRecipe.product_id == product_id)
        .where(ProductRecipe.warehouse_item_id == recipe.warehouse_item_id)
    )

    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Recipe component already exists for this product"
        )

    # Create new recipe
    db_recipe = ProductRecipe(
        product_id=product_id,
        warehouse_item_id=recipe.warehouse_item_id,
        quantity=recipe.quantity,
        is_optional=recipe.is_optional
    )
    session.add(db_recipe)
    await session.commit()
    await session.refresh(db_recipe)

    # Return with warehouse item details
    return ProductRecipeRead(
        **db_recipe.model_dump(),
        warehouse_item=WarehouseItemRead(**warehouse_item.model_dump())
    )


@router.patch("/products/{product_id}/recipe/{recipe_id}", response_model=ProductRecipeRead)
async def update_recipe_component(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    recipe_id: int,
    recipe_update: ProductRecipeUpdate
):
    """Update a recipe component"""

    # Get existing recipe
    result = await session.execute(
        select(ProductRecipe)
        .where(ProductRecipe.id == recipe_id)
        .where(ProductRecipe.product_id == product_id)
    )
    db_recipe = result.scalar_one_or_none()

    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe component not found")

    # Update fields
    update_data = recipe_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_recipe, key, value)

    await session.commit()
    await session.refresh(db_recipe)

    # Get warehouse item for response
    warehouse_result = await session.execute(
        select(WarehouseItem).where(WarehouseItem.id == db_recipe.warehouse_item_id)
    )
    warehouse_item = warehouse_result.scalar_one()

    return ProductRecipeRead(
        **db_recipe.model_dump(),
        warehouse_item=WarehouseItemRead(**warehouse_item.model_dump())
    )


@router.delete("/products/{product_id}/recipe/{recipe_id}")
async def delete_recipe_component(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    recipe_id: int
):
    """Delete a recipe component"""

    # Get existing recipe
    result = await session.execute(
        select(ProductRecipe)
        .where(ProductRecipe.id == recipe_id)
        .where(ProductRecipe.product_id == product_id)
    )
    db_recipe = result.scalar_one_or_none()

    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe component not found")

    await session.delete(db_recipe)
    await session.commit()

    return {"detail": "Recipe component deleted"}


@router.post("/products/{product_id}/recipe/batch", response_model=List[ProductRecipeRead])
async def set_product_recipe(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    recipes: List[ProductRecipeCreate]
):
    """Set complete recipe for a product (replaces existing)"""

    # Verify product exists
    product_result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    if not product_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete existing recipes
    existing_result = await session.execute(
        select(ProductRecipe).where(ProductRecipe.product_id == product_id)
    )
    existing_recipes = existing_result.scalars().all()
    for recipe in existing_recipes:
        await session.delete(recipe)

    # Add new recipes
    created_recipes = []
    for recipe_data in recipes:
        # Verify warehouse item exists
        warehouse_result = await session.execute(
            select(WarehouseItem).where(WarehouseItem.id == recipe_data.warehouse_item_id)
        )
        warehouse_item = warehouse_result.scalar_one_or_none()
        if not warehouse_item:
            raise HTTPException(
                status_code=404,
                detail=f"Warehouse item {recipe_data.warehouse_item_id} not found"
            )

        recipe_data.product_id = product_id
        db_recipe = ProductRecipe.model_validate(recipe_data)
        session.add(db_recipe)
        await session.flush()

        created_recipes.append(ProductRecipeRead(
            **db_recipe.model_dump(),
            warehouse_item=WarehouseItemRead(**warehouse_item.model_dump())
        ))

    await session.commit()
    return created_recipes


@router.get("/products/check-availability", response_model=List[ProductWithRecipe])
async def check_products_availability(
    *,
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Check availability of all products based on warehouse stock"""

    # Get all enabled products
    products_result = await session.execute(
        select(Product)
        .where(Product.enabled == True)
        .offset(skip)
        .limit(limit)
    )
    products = products_result.scalars().all()

    result = []
    for product in products:
        # Get recipes with warehouse items
        recipes_result = await session.execute(
            select(ProductRecipe, WarehouseItem)
            .join(WarehouseItem, ProductRecipe.warehouse_item_id == WarehouseItem.id)
            .where(ProductRecipe.product_id == product.id)
        )

        recipes_with_items = recipes_result.all()

        # Calculate availability
        total_cost = 0
        can_produce = True
        max_quantity = float('inf')

        recipes = []
        for recipe, warehouse_item in recipes_with_items:
            if recipe.quantity > 0:
                possible_quantity = warehouse_item.quantity // recipe.quantity
                max_quantity = min(max_quantity, possible_quantity)

            if warehouse_item.quantity < recipe.quantity and not recipe.is_optional:
                can_produce = False

            total_cost += warehouse_item.cost_price * recipe.quantity

            recipe_read = ProductRecipeRead(
                **recipe.model_dump(),
                warehouse_item=WarehouseItemRead(**warehouse_item.model_dump())
            )
            recipes.append(recipe_read)

        if not recipes:
            max_quantity = 0
        elif max_quantity == float('inf'):
            max_quantity = 0

        result.append(ProductWithRecipe(
            **product.model_dump(),
            recipes=recipes,
            total_cost=total_cost,
            can_produce=can_produce,
            max_quantity=int(max_quantity)
        ))

    return result