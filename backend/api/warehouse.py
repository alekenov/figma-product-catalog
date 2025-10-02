from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col, desc
from database import get_session
from models import (
    WarehouseItem, WarehouseItemCreate, WarehouseItemRead, WarehouseItemUpdate, WarehouseItemDetail,
    WarehouseOperation, WarehouseOperationCreate, WarehouseOperationRead, WarehouseOperationType
)
from utils import kopecks_to_tenge, tenge_to_kopecks, format_price_tenge
from auth_utils import get_current_user_shop_id

router = APIRouter()


@router.get("/", response_model=List[WarehouseItemRead])
async def get_warehouse_items(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of items to return"),
    search: Optional[str] = Query(None, description="Search in item names"),
    low_stock: bool = Query(False, description="Show only low stock items"),
):
    """Get list of warehouse items with filtering and search"""

    # Build query - filter by shop_id for multi-tenancy
    query = select(WarehouseItem).where(WarehouseItem.shop_id == shop_id)

    # Apply filters
    if search:
        query = query.where(col(WarehouseItem.name).ilike(f"%{search}%"))

    if low_stock:
        query = query.where(WarehouseItem.quantity <= WarehouseItem.min_quantity)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await session.execute(query)
    items = result.scalars().all()
    return items


@router.post("/", response_model=WarehouseItemRead)
async def create_warehouse_item(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    item: WarehouseItemCreate
):
    """Create a new warehouse item"""

    # Convert tenge prices to kopecks for storage
    db_item = WarehouseItem(
        name=item.name,
        quantity=item.quantity,
        cost_price=item.cost_price,  # Already converted by property
        retail_price=item.retail_price,  # Already converted by property
        image=item.image,
        min_quantity=item.min_quantity,
        last_delivery_date=datetime.now(),
        shop_id=shop_id  # Inject shop_id from JWT
    )

    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)

    # Create initial delivery operation if quantity > 0
    if db_item.quantity > 0:
        operation = WarehouseOperation(
            warehouse_item_id=db_item.id,
            operation_type=WarehouseOperationType.DELIVERY,
            quantity_change=db_item.quantity,
            balance_after=db_item.quantity,
            description="Начальная поставка"
        )
        session.add(operation)
        await session.commit()

    return db_item


@router.get("/{item_id}", response_model=WarehouseItemDetail)
async def get_warehouse_item(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    item_id: int
):
    """Get a single warehouse item with its operations"""

    # Get item - filter by shop_id
    result = await session.execute(
        select(WarehouseItem).where(
            WarehouseItem.id == item_id,
            WarehouseItem.shop_id == shop_id
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Warehouse item not found")

    # Get operations
    operations_result = await session.execute(
        select(WarehouseOperation)
        .where(WarehouseOperation.warehouse_item_id == item_id)
        .order_by(desc(WarehouseOperation.created_at))
    )
    operations = operations_result.scalars().all()

    # Return item with operations
    return WarehouseItemDetail(
        **item.model_dump(),
        operations=operations
    )


@router.patch("/{item_id}", response_model=WarehouseItemRead)
async def update_warehouse_item(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    item_id: int,
    item_update: WarehouseItemUpdate
):
    """Update a warehouse item (except quantity - use operations for that)"""

    # Get existing item
    result = await session.execute(
        select(WarehouseItem).where(WarehouseItem.id == item_id)
    )
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(status_code=404, detail="Warehouse item not found")

    # Verify ownership
    if db_item.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Warehouse item does not belong to your shop")

    # Track price changes (in kopecks)
    old_cost_price = db_item.cost_price
    old_retail_price = db_item.retail_price

    # Update fields - convert tenge to kopecks where needed
    update_data = item_update.model_dump(exclude_unset=True, exclude={'cost_price_tenge', 'retail_price_tenge'})

    # Don't allow quantity updates through this endpoint
    if 'quantity' in update_data:
        del update_data['quantity']

    # Handle price updates with conversion
    if item_update.cost_price_tenge is not None:
        new_cost_price = item_update.cost_price
        db_item.cost_price = new_cost_price

    if item_update.retail_price_tenge is not None:
        new_retail_price = item_update.retail_price
        db_item.retail_price = new_retail_price

    # Update other fields
    for key, value in update_data.items():
        setattr(db_item, key, value)

    # Record price change operations (display in tenge)
    if item_update.cost_price_tenge is not None and item_update.cost_price != old_cost_price:
        old_cost_tenge = kopecks_to_tenge(old_cost_price)
        new_cost_tenge = item_update.cost_price_tenge
        operation = WarehouseOperation(
            warehouse_item_id=item_id,
            operation_type=WarehouseOperationType.PRICE_CHANGE,
            quantity_change=0,
            balance_after=db_item.quantity,
            description=f"Себестоимость: {old_cost_tenge}₸ → {new_cost_tenge}₸",
            old_value=old_cost_price,
            new_value=item_update.cost_price
        )
        session.add(operation)

    if item_update.retail_price_tenge is not None and item_update.retail_price != old_retail_price:
        old_retail_tenge = kopecks_to_tenge(old_retail_price)
        new_retail_tenge = item_update.retail_price_tenge
        operation = WarehouseOperation(
            warehouse_item_id=item_id,
            operation_type=WarehouseOperationType.PRICE_CHANGE,
            quantity_change=0,
            balance_after=db_item.quantity,
            description=f"Розничная цена: {old_retail_tenge}₸ → {new_retail_tenge}₸",
            old_value=old_retail_price,
            new_value=item_update.retail_price
        )
        session.add(operation)

    await session.commit()
    await session.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
async def delete_warehouse_item(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    item_id: int
):
    """Delete a warehouse item"""

    # Get existing item
    result = await session.execute(
        select(WarehouseItem).where(WarehouseItem.id == item_id)
    )
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(status_code=404, detail="Warehouse item not found")

    # Verify ownership
    if db_item.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Warehouse item does not belong to your shop")

    await session.delete(db_item)
    await session.commit()
    return {"detail": "Warehouse item deleted"}


# Operations endpoints

@router.post("/{item_id}/writeoff", response_model=WarehouseOperationRead)
async def writeoff_item(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    item_id: int,
    writeoff: WarehouseOperationCreate
):
    """Write off warehouse item quantity"""

    # Get existing item
    result = await session.execute(
        select(WarehouseItem).where(WarehouseItem.id == item_id)
    )
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(status_code=404, detail="Warehouse item not found")

    # Verify ownership
    if db_item.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Warehouse item does not belong to your shop")

    # Validate quantity
    if writeoff.quantity_change is None or writeoff.quantity_change >= 0:
        raise HTTPException(status_code=400, detail="Writeoff quantity must be negative")

    if abs(writeoff.quantity_change) > db_item.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot write off more than available quantity ({db_item.quantity})"
        )

    # Update item quantity
    db_item.quantity += writeoff.quantity_change  # quantity_change is negative

    # Create operation
    operation = WarehouseOperation(
        warehouse_item_id=item_id,
        operation_type=WarehouseOperationType.WRITEOFF,
        quantity_change=writeoff.quantity_change,
        balance_after=db_item.quantity,
        description=f"Списание: {writeoff.reason or writeoff.description}"
    )
    session.add(operation)

    await session.commit()
    await session.refresh(operation)
    return operation


@router.post("/{item_id}/delivery", response_model=WarehouseOperationRead)
async def add_delivery(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    item_id: int,
    delivery: WarehouseOperationCreate
):
    """Add delivery to warehouse item"""

    # Get existing item
    result = await session.execute(
        select(WarehouseItem).where(WarehouseItem.id == item_id)
    )
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(status_code=404, detail="Warehouse item not found")

    # Verify ownership
    if db_item.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Warehouse item does not belong to your shop")

    # Validate quantity
    if delivery.quantity_change is None or delivery.quantity_change <= 0:
        raise HTTPException(status_code=400, detail="Delivery quantity must be positive")

    # Update item quantity
    db_item.quantity += delivery.quantity_change
    db_item.last_delivery_date = datetime.now()

    # Create operation
    operation = WarehouseOperation(
        warehouse_item_id=item_id,
        operation_type=WarehouseOperationType.DELIVERY,
        quantity_change=delivery.quantity_change,
        balance_after=db_item.quantity,
        description=delivery.description or "Поставка"
    )
    session.add(operation)

    await session.commit()
    await session.refresh(operation)
    return operation


@router.post("/{item_id}/sale", response_model=WarehouseOperationRead)
async def record_sale(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    item_id: int,
    sale: WarehouseOperationCreate
):
    """Record a sale from warehouse"""

    # Get existing item
    result = await session.execute(
        select(WarehouseItem).where(WarehouseItem.id == item_id)
    )
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(status_code=404, detail="Warehouse item not found")

    # Verify ownership
    if db_item.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Warehouse item does not belong to your shop")

    # Validate quantity
    if sale.quantity_change is None or sale.quantity_change >= 0:
        raise HTTPException(status_code=400, detail="Sale quantity must be negative")

    if abs(sale.quantity_change) > db_item.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot sell more than available quantity ({db_item.quantity})"
        )

    # Update item quantity
    db_item.quantity += sale.quantity_change  # quantity_change is negative

    # Create operation
    operation = WarehouseOperation(
        warehouse_item_id=item_id,
        operation_type=WarehouseOperationType.SALE,
        quantity_change=sale.quantity_change,
        balance_after=db_item.quantity,
        description=sale.description or f"Продажа{' - Заказ #' + str(sale.order_id) if sale.order_id else ''}",
        order_id=sale.order_id
    )
    session.add(operation)

    await session.commit()
    await session.refresh(operation)
    return operation


@router.get("/{item_id}/operations", response_model=List[WarehouseOperationRead])
async def get_item_operations(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    item_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    operation_type: Optional[WarehouseOperationType] = Query(None)
):
    """Get operations history for a warehouse item"""

    # Verify item ownership first
    item_result = await session.execute(
        select(WarehouseItem).where(WarehouseItem.id == item_id)
    )
    item = item_result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Warehouse item not found")

    if item.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Warehouse item does not belong to your shop")

    # Build query
    query = select(WarehouseOperation).where(WarehouseOperation.warehouse_item_id == item_id)

    if operation_type:
        query = query.where(WarehouseOperation.operation_type == operation_type)

    query = query.order_by(desc(WarehouseOperation.created_at))
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await session.execute(query)
    operations = result.scalars().all()
    return operations