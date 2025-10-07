"""
Superadmin API endpoints
Provides superadmin-only access to manage all shops, users, and view cross-shop statistics.
Only accessible by users with is_superadmin=True (phone 77015211545).
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from datetime import datetime

from database import get_session
from models import (
    User, UserRead, UserResponse, UserRole,
    Shop, ShopRead,
    Order, Product, WarehouseItem
)
from auth_utils import require_superadmin, get_password_hash

router = APIRouter()


# ===============================
# Shop Management Endpoints
# ===============================

@router.get("/shops", response_model=List[ShopRead])
async def list_all_shops(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000)
):
    """
    Get list of all shops across the platform.
    Superadmin only endpoint.
    """
    query = select(Shop)

    if is_active is not None:
        query = query.where(Shop.is_active == is_active)

    query = query.offset(skip).limit(limit).order_by(Shop.created_at.desc())

    result = await session.execute(query)
    shops = result.scalars().all()

    return shops


@router.get("/shops/{shop_id}", response_model=dict)
async def get_shop_detail(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    shop_id: int
):
    """
    Get detailed information about a specific shop including its users.
    Superadmin only endpoint.
    """
    # Get shop
    shop_result = await session.execute(
        select(Shop).where(Shop.id == shop_id)
    )
    shop = shop_result.scalar_one_or_none()

    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shop with id {shop_id} not found"
        )

    # Get shop users
    users_result = await session.execute(
        select(User).where(User.shop_id == shop_id)
    )
    users = users_result.scalars().all()

    # Get shop owner
    owner_result = await session.execute(
        select(User).where(User.id == shop.owner_id)
    )
    owner = owner_result.scalar_one_or_none()

    # Get shop statistics
    products_count_result = await session.execute(
        select(func.count(Product.id)).where(Product.shop_id == shop_id)
    )
    products_count = products_count_result.scalar() or 0

    orders_count_result = await session.execute(
        select(func.count(Order.id)).where(Order.shop_id == shop_id)
    )
    orders_count = orders_count_result.scalar() or 0

    return {
        "shop": ShopRead.model_validate(shop),
        "owner": UserResponse.from_user(owner) if owner else None,
        "users": [UserResponse.from_user(u) for u in users],
        "stats": {
            "products_count": products_count,
            "orders_count": orders_count,
            "users_count": len(users)
        }
    }


@router.put("/shops/{shop_id}/block")
async def block_shop(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    shop_id: int
):
    """
    Block a shop (set is_active=False).
    Superadmin only endpoint.
    """
    result = await session.execute(
        select(Shop).where(Shop.id == shop_id)
    )
    shop = result.scalar_one_or_none()

    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shop with id {shop_id} not found"
        )

    shop.is_active = False
    await session.commit()
    await session.refresh(shop)

    return {
        "message": f"Shop '{shop.name}' has been blocked",
        "shop": ShopRead.model_validate(shop)
    }


@router.put("/shops/{shop_id}/unblock")
async def unblock_shop(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    shop_id: int
):
    """
    Unblock a shop (set is_active=True).
    Superadmin only endpoint.
    """
    result = await session.execute(
        select(Shop).where(Shop.id == shop_id)
    )
    shop = result.scalar_one_or_none()

    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shop with id {shop_id} not found"
        )

    shop.is_active = True
    await session.commit()
    await session.refresh(shop)

    return {
        "message": f"Shop '{shop.name}' has been unblocked",
        "shop": ShopRead.model_validate(shop)
    }


# ===============================
# User Management Endpoints
# ===============================

@router.get("/users", response_model=List[UserResponse])
async def list_all_users(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    shop_id: Optional[int] = Query(None, description="Filter by shop ID"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name or phone"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000)
):
    """
    Get list of all users across all shops.
    Supports filtering by shop_id, role, is_active, and search.
    Superadmin only endpoint.
    """
    query = select(User)

    if shop_id is not None:
        query = query.where(User.shop_id == shop_id)

    if role is not None:
        query = query.where(User.role == role)

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (User.name.ilike(search_pattern)) | (User.phone.ilike(search_pattern))
        )

    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())

    result = await session.execute(query)
    users = result.scalars().all()

    return [UserResponse.from_user(u) for u in users]


@router.put("/users/{user_id}/block")
async def block_user(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    user_id: int
):
    """
    Block a user (set is_active=False).
    Superadmin only endpoint.
    """
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Prevent blocking superadmins
    if user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot block a superadmin user"
        )

    user.is_active = False
    await session.commit()
    await session.refresh(user)

    return {
        "message": f"User '{user.name}' has been blocked",
        "user": UserResponse.from_user(user)
    }


@router.put("/users/{user_id}/unblock")
async def unblock_user(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    user_id: int
):
    """
    Unblock a user (set is_active=True).
    Superadmin only endpoint.
    """
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    user.is_active = True
    await session.commit()
    await session.refresh(user)

    return {
        "message": f"User '{user.name}' has been unblocked",
        "user": UserResponse.from_user(user)
    }


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    user_id: int,
    new_password: str = Query(..., min_length=6, description="New password (min 6 characters)")
):
    """
    Reset user's password to a new value.
    Superadmin only endpoint.
    """
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Hash new password
    user.password_hash = get_password_hash(new_password)
    await session.commit()

    return {
        "message": f"Password reset successful for user '{user.name}'",
        "user": UserResponse.from_user(user)
    }


# ===============================
# Product Management Endpoints
# ===============================

@router.get("/products")
async def list_all_products(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    shop_id: Optional[int] = Query(None, description="Filter by shop ID"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    search: Optional[str] = Query(None, description="Search by product name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000)
):
    """
    Get list of all products across all shops.
    Supports filtering by shop_id, enabled status, and search.
    Superadmin only endpoint.
    """
    query = select(Product, Shop.name.label("shop_name")).join(Shop, Product.shop_id == Shop.id)

    if shop_id is not None:
        query = query.where(Product.shop_id == shop_id)

    if enabled is not None:
        query = query.where(Product.enabled == enabled)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(Product.name.ilike(search_pattern))

    query = query.offset(skip).limit(limit).order_by(Product.created_at.desc())

    result = await session.execute(query)
    rows = result.all()

    # Format response with shop names
    products = []
    for product, shop_name in rows:
        product_dict = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "type": product.type,
            "description": product.description,
            "enabled": product.enabled,
            "shop_id": product.shop_id,
            "shop_name": shop_name,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "image": product.image
        }
        products.append(product_dict)

    return products


@router.put("/products/{product_id}")
async def update_product(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    product_id: int,
    name: Optional[str] = None,
    price: Optional[int] = None,
    description: Optional[str] = None,
    enabled: Optional[bool] = None
):
    """
    Update product details.
    Superadmin only endpoint.
    """
    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    # Update fields if provided
    if name is not None:
        product.name = name
    if price is not None:
        product.price = price
    if description is not None:
        product.description = description
    if enabled is not None:
        product.enabled = enabled

    await session.commit()
    await session.refresh(product)

    return {
        "message": f"Product '{product.name}' has been updated",
        "product": {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "enabled": product.enabled,
            "shop_id": product.shop_id
        }
    }


@router.delete("/products/{product_id}")
async def delete_product(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    product_id: int
):
    """
    Delete a product.
    Superadmin only endpoint.
    """
    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    product_name = product.name
    await session.delete(product)
    await session.commit()

    return {
        "message": f"Product '{product_name}' has been deleted"
    }


@router.put("/products/{product_id}/toggle")
async def toggle_product(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    product_id: int
):
    """
    Toggle product enabled status.
    Superadmin only endpoint.
    """
    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    # Toggle enabled status
    product.enabled = not product.enabled
    await session.commit()
    await session.refresh(product)

    status_text = "включен" if product.enabled else "выключен"
    return {
        "message": f"Товар '{product.name}' {status_text}",
        "product": {
            "id": product.id,
            "name": product.name,
            "enabled": product.enabled
        }
    }


# ===============================
# Order Management Endpoints
# ===============================

@router.get("/orders")
async def list_all_orders(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    shop_id: Optional[int] = Query(None, description="Filter by shop ID"),
    status: Optional[str] = Query(None, description="Filter by order status"),
    date_from: Optional[str] = Query(None, description="Filter by date from (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter by date to (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000)
):
    """
    Get list of all orders across all shops.
    Supports filtering by shop_id, status, and date range.
    Superadmin only endpoint.
    """
    from models.enums import OrderStatus as OrderStatusEnum

    query = select(Order, Shop.name.label("shop_name")).join(Shop, Order.shop_id == Shop.id)

    if shop_id is not None:
        query = query.where(Order.shop_id == shop_id)

    if status:
        try:
            # Look up enum by name (uppercase) to get the enum member
            status_enum = OrderStatusEnum[status.upper()]
            query = query.where(Order.status == status_enum)
        except (ValueError, KeyError):
            pass  # Invalid status, ignore filter

    if date_from:
        try:
            date_from_dt = datetime.fromisoformat(date_from)
            query = query.where(Order.created_at >= date_from_dt)
        except ValueError:
            pass  # Invalid date format, ignore

    if date_to:
        try:
            date_to_dt = datetime.fromisoformat(date_to)
            query = query.where(Order.created_at <= date_to_dt)
        except ValueError:
            pass  # Invalid date format, ignore

    query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())

    result = await session.execute(query)
    rows = result.all()

    # Format response with shop names
    orders = []
    for order, shop_name in rows:
        order_dict = {
            "id": order.id,
            "tracking_id": order.tracking_id,
            "orderNumber": order.orderNumber,
            "customerName": order.customerName,
            "phone": order.phone,
            "total": order.total,
            "status": order.status.value,
            "shop_id": order.shop_id,
            "shop_name": shop_name,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None
        }
        orders.append(order_dict)

    return orders


@router.get("/orders/{order_id}")
async def get_order_detail(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    order_id: int
):
    """
    Get detailed information about a specific order including items.
    Superadmin only endpoint.
    """
    from models.orders import OrderItem

    # Get order
    order_result = await session.execute(
        select(Order).where(Order.id == order_id)
    )
    order = order_result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )

    # Get shop
    shop_result = await session.execute(
        select(Shop).where(Shop.id == order.shop_id)
    )
    shop = shop_result.scalar_one_or_none()

    # Get order items
    items_result = await session.execute(
        select(OrderItem).where(OrderItem.order_id == order_id)
    )
    items = items_result.scalars().all()

    return {
        "order": {
            "id": order.id,
            "tracking_id": order.tracking_id,
            "orderNumber": order.orderNumber,
            "customerName": order.customerName,
            "phone": order.phone,
            "delivery_address": order.delivery_address,
            "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None,
            "scheduled_time": order.scheduled_time,
            "subtotal": order.subtotal,
            "delivery_cost": order.delivery_cost,
            "total": order.total,
            "status": order.status.value,
            "notes": order.notes,
            "created_at": order.created_at.isoformat() if order.created_at else None
        },
        "shop": {
            "id": shop.id,
            "name": shop.name
        } if shop else None,
        "items": [
            {
                "id": item.id,
                "product_name": item.product_name,
                "product_price": item.product_price,
                "quantity": item.quantity,
                "item_total": item.item_total
            }
            for item in items
        ]
    }


@router.put("/orders/{order_id}/status")
async def update_order_status(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    order_id: int,
    new_status: str = Query(..., description="New order status (NEW, PAID, ACCEPTED, ASSEMBLED, IN_DELIVERY, DELIVERED, CANCELLED)")
):
    """
    Update order status.
    Superadmin only endpoint.
    """
    from models.enums import OrderStatus as OrderStatusEnum

    result = await session.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )

    # Validate and set new status
    try:
        status_enum = OrderStatusEnum(new_status.lower())
        order.status = status_enum
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {new_status}. Must be one of: NEW, PAID, ACCEPTED, ASSEMBLED, IN_DELIVERY, DELIVERED, CANCELLED"
        )

    await session.commit()
    await session.refresh(order)

    return {
        "message": f"Статус заказа {order.orderNumber} изменен на {status_enum.value}",
        "order": {
            "id": order.id,
            "orderNumber": order.orderNumber,
            "status": order.status.value
        }
    }


@router.put("/orders/{order_id}/cancel")
async def cancel_order(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin),
    order_id: int,
    reason: Optional[str] = Query(None, description="Cancellation reason")
):
    """
    Cancel an order.
    Superadmin only endpoint.
    """
    from models.enums import OrderStatus as OrderStatusEnum

    result = await session.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )

    # Check if order can be cancelled
    if order.status == OrderStatusEnum.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заказ уже отменен"
        )

    if order.status == OrderStatusEnum.DELIVERED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно отменить доставленный заказ"
        )

    # Cancel order
    order.status = OrderStatusEnum.CANCELLED
    if reason:
        order.cancellation_reason = reason

    await session.commit()
    await session.refresh(order)

    return {
        "message": f"Заказ {order.orderNumber} отменен",
        "order": {
            "id": order.id,
            "orderNumber": order.orderNumber,
            "status": order.status.value,
            "cancellation_reason": order.cancellation_reason
        }
    }


# ===============================
# Statistics Endpoint
# ===============================

@router.get("/stats")
async def get_platform_stats(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_superadmin)
):
    """
    Get platform-wide statistics.
    Superadmin only endpoint.
    """
    # Total shops
    total_shops_result = await session.execute(select(func.count(Shop.id)))
    total_shops = total_shops_result.scalar() or 0

    # Active shops
    active_shops_result = await session.execute(
        select(func.count(Shop.id)).where(Shop.is_active == True)
    )
    active_shops = active_shops_result.scalar() or 0

    # Total users
    total_users_result = await session.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0

    # Active users
    active_users_result = await session.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_users_result.scalar() or 0

    # Users by role
    users_by_role = {}
    for role in UserRole:
        role_count_result = await session.execute(
            select(func.count(User.id)).where(User.role == role)
        )
        users_by_role[role.value] = role_count_result.scalar() or 0

    # Total orders
    total_orders_result = await session.execute(select(func.count(Order.id)))
    total_orders = total_orders_result.scalar() or 0

    # Total products
    total_products_result = await session.execute(select(func.count(Product.id)))
    total_products = total_products_result.scalar() or 0

    return {
        "shops": {
            "total": total_shops,
            "active": active_shops,
            "blocked": total_shops - active_shops
        },
        "users": {
            "total": total_users,
            "active": active_users,
            "blocked": total_users - active_users,
            "by_role": users_by_role
        },
        "orders": {
            "total": total_orders
        },
        "products": {
            "total": total_products
        },
        "timestamp": datetime.utcnow().isoformat()
    }
