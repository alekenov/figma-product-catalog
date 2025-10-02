"""
Product Service - Business logic for product management

Provides clean interfaces for product CRUD operations with proper
transaction discipline (no commits without explicit flag).
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from models import (
    Product, ProductCreate, ProductUpdate, ProductImage, ProductImageCreate
)


class ProductService:
    """
    Product management service with business logic.

    All write operations accept a `commit` parameter to control transactions.
    Router layer is responsible for calling with commit=True.
    """

    @staticmethod
    async def create_product(
        session: AsyncSession,
        product_in: ProductCreate,
        shop_id: int,
        commit: bool = False
    ) -> Product:
        """
        Create a new product with shop_id.

        Args:
            session: Database session
            product_in: Product creation data
            shop_id: Shop ID to assign to the product (for multi-tenancy)
            commit: Whether to commit the transaction

        Returns:
            Created Product instance

        Raises:
            HTTPException: If validation fails
        """
        # Create product instance
        product_data = product_in.model_dump()
        product_data['shop_id'] = shop_id  # Inject shop_id for multi-tenancy

        product = Product(**product_data)

        # Add to session
        session.add(product)

        if commit:
            await session.commit()
            await session.refresh(product)
        else:
            await session.flush()

        return product

    @staticmethod
    async def update_product(
        session: AsyncSession,
        product_id: int,
        product_in: ProductUpdate,
        shop_id: int,
        commit: bool = False
    ) -> Product:
        """
        Update an existing product.

        Args:
            session: Database session
            product_id: Product ID
            product_in: Product update data
            shop_id: Shop ID for multi-tenancy verification
            commit: Whether to commit the transaction

        Returns:
            Updated Product instance

        Raises:
            HTTPException: If product not found or doesn't belong to shop
        """
        # Get existing product
        product = await session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Verify product belongs to user's shop
        if product.shop_id != shop_id:
            raise HTTPException(status_code=403, detail="Product does not belong to your shop")

        # Update fields that were provided
        product_data = product_in.model_dump(exclude_unset=True)
        for field, value in product_data.items():
            setattr(product, field, value)

        if commit:
            await session.commit()
            await session.refresh(product)
        else:
            await session.flush()

        return product

    @staticmethod
    async def toggle_product_status(
        session: AsyncSession,
        product_id: int,
        enabled: bool,
        shop_id: int,
        commit: bool = False
    ) -> Product:
        """
        Toggle product enabled/disabled status.

        Args:
            session: Database session
            product_id: Product ID
            enabled: New enabled status
            shop_id: Shop ID for multi-tenancy verification
            commit: Whether to commit the transaction

        Returns:
            Updated Product instance

        Raises:
            HTTPException: If product not found or doesn't belong to shop
        """
        # Get existing product
        product = await session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Verify product belongs to user's shop
        if product.shop_id != shop_id:
            raise HTTPException(status_code=403, detail="Product does not belong to your shop")

        # Update enabled status
        product.enabled = enabled

        if commit:
            await session.commit()
            await session.refresh(product)
        else:
            await session.flush()

        return product

    @staticmethod
    async def bulk_update_status(
        session: AsyncSession,
        product_ids: List[int],
        enabled: bool,
        shop_id: int,
        commit: bool = False
    ) -> int:
        """
        Bulk update product status for multiple products.

        Args:
            session: Database session
            product_ids: List of product IDs
            enabled: New enabled status
            shop_id: Shop ID for multi-tenancy verification
            commit: Whether to commit the transaction

        Returns:
            Number of products updated
        """
        updated_count = 0

        for product_id in product_ids:
            product = await session.get(Product, product_id)
            if product and product.shop_id == shop_id:
                product.enabled = enabled
                updated_count += 1

        if commit:
            await session.commit()

        return updated_count

    @staticmethod
    async def delete_product(
        session: AsyncSession,
        product_id: int,
        shop_id: int,
        commit: bool = False
    ) -> None:
        """
        Delete a product.

        Args:
            session: Database session
            product_id: Product ID
            shop_id: Shop ID for multi-tenancy verification
            commit: Whether to commit the transaction

        Raises:
            HTTPException: If product not found or doesn't belong to shop
        """
        # Get existing product
        product = await session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Verify product belongs to user's shop
        if product.shop_id != shop_id:
            raise HTTPException(status_code=403, detail="Product does not belong to your shop")

        # Delete product
        await session.delete(product)

        if commit:
            await session.commit()

    # ===== Image Management =====

    @staticmethod
    async def create_product_image(
        session: AsyncSession,
        product_id: int,
        image_in: ProductImageCreate,
        shop_id: int,
        commit: bool = False
    ) -> ProductImage:
        """
        Create a new product image.

        Args:
            session: Database session
            product_id: Product ID
            image_in: Image creation data
            shop_id: Shop ID for multi-tenancy verification
            commit: Whether to commit the transaction

        Returns:
            Created ProductImage instance

        Raises:
            HTTPException: If product not found or doesn't belong to shop
        """
        # Verify product exists and belongs to shop
        product = await session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.shop_id != shop_id:
            raise HTTPException(status_code=403, detail="Product does not belong to your shop")

        # Create image record
        image = ProductImage.model_validate(image_in)
        session.add(image)

        if commit:
            await session.commit()
            await session.refresh(image)
        else:
            await session.flush()

        return image

    @staticmethod
    async def delete_product_image(
        session: AsyncSession,
        product_id: int,
        image_id: int,
        shop_id: int,
        commit: bool = False
    ) -> None:
        """
        Delete a product image.

        Args:
            session: Database session
            product_id: Product ID (for validation)
            image_id: Image ID
            shop_id: Shop ID for multi-tenancy verification
            commit: Whether to commit the transaction

        Raises:
            HTTPException: If image not found or doesn't belong to product/shop
        """
        image = await session.get(ProductImage, image_id)
        if not image or image.product_id != product_id:
            raise HTTPException(status_code=404, detail="Image not found")

        # Verify product belongs to shop
        product = await session.get(Product, product_id)
        if not product or product.shop_id != shop_id:
            raise HTTPException(status_code=403, detail="Image does not belong to your shop")

        await session.delete(image)

        if commit:
            await session.commit()

    # ===== Business Validation =====

    @staticmethod
    async def validate_slug_uniqueness(
        session: AsyncSession,
        slug: str,
        exclude_product_id: Optional[int] = None
    ) -> bool:
        """
        Validate that product slug is unique.

        Args:
            session: Database session
            slug: Slug to check
            exclude_product_id: Product ID to exclude from check (for updates)

        Returns:
            True if slug is unique, False otherwise
        """
        from sqlmodel import select

        query = select(Product).where(Product.slug == slug)
        if exclude_product_id:
            query = query.where(Product.id != exclude_product_id)

        result = await session.execute(query)
        existing = result.scalar_one_or_none()

        return existing is None

    @staticmethod
    def validate_base_price(product: Product) -> List[str]:
        """
        Validate that product has a valid base price.

        Args:
            product: Product instance

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if product.price is None:
            errors.append("Product must have a price")
        elif product.price <= 0:
            errors.append("Product price must be positive")

        return errors

    @staticmethod
    def validate_product_recipe(recipes: List[dict]) -> List[str]:
        """
        Validate product recipe/composition data.

        Args:
            recipes: List of recipe dictionaries

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        for idx, recipe in enumerate(recipes):
            if 'warehouse_item_id' not in recipe:
                errors.append(f"Recipe {idx + 1}: missing warehouse_item_id")

            if 'quantity' not in recipe:
                errors.append(f"Recipe {idx + 1}: missing quantity")
            elif recipe['quantity'] <= 0:
                errors.append(f"Recipe {idx + 1}: quantity must be positive")

        return errors
