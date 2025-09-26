from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func, col
from database import get_session
from models import Order, OrderStatus, Client, ClientUpdate

router = APIRouter()


@router.get("/")
async def get_clients(
    *,
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0, description="Number of clients to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of clients to return"),
    search: Optional[str] = Query(None, description="Search in customer name or phone"),
):
    """Get list of clients grouped by phone number with aggregated statistics"""

    # Base query to get client statistics grouped by phone
    query = select(
        Order.phone,
        func.coalesce(func.max(Order.customerName), "Клиент без имени").label("customerName"),
        func.min(Order.created_at).label("first_order_date"),
        func.max(Order.created_at).label("last_order_date"),
        func.count(Order.id).label("total_orders"),
        func.sum(Order.total).label("total_spent"),
        func.avg(Order.total).label("average_order")
    ).group_by(Order.phone)

    # Apply search filter
    if search:
        query = query.having(
            col(Order.customerName).ilike(f"%{search}%") |
            col(Order.phone).ilike(f"%{search}%")
        )

    # Order by total spent descending (most valuable clients first)
    query = query.order_by(func.sum(Order.total).desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await session.execute(query)
    clients_data = result.all()

    # Format response
    clients = []
    for client_data in clients_data:
        # Get last order details
        last_order_query = select(Order).where(
            Order.phone == client_data.phone
        ).order_by(Order.created_at.desc()).limit(1)
        last_order_result = await session.execute(last_order_query)
        last_order = last_order_result.scalar_one_or_none()

        client = {
            "phone": client_data.phone,
            "customerName": client_data.customerName or "Клиент без имени",
            "first_order_date": client_data.first_order_date,
            "last_order_date": client_data.last_order_date,
            "total_orders": client_data.total_orders,
            "total_spent": int(client_data.total_spent or 0),
            "average_order": int(client_data.average_order or 0),
            "last_order_number": last_order.orderNumber if last_order else None,
            "last_order_status": last_order.status if last_order else None,
            "customer_since": client_data.first_order_date.strftime("%d.%m.%Y") if client_data.first_order_date else None
        }
        clients.append(client)

    return clients


@router.get("/{phone}")
async def get_client_detail(
    *,
    session: AsyncSession = Depends(get_session),
    phone: str
):
    """Get detailed information about a specific client including order history"""

    # Get client statistics
    stats_query = select(
        Order.phone,
        func.coalesce(func.max(Order.customerName), "Клиент без имени").label("customerName"),
        func.min(Order.created_at).label("first_order_date"),
        func.max(Order.created_at).label("last_order_date"),
        func.count(Order.id).label("total_orders"),
        func.sum(Order.total).label("total_spent"),
        func.avg(Order.total).label("average_order")
    ).where(Order.phone == phone).group_by(Order.phone)

    stats_result = await session.execute(stats_query)
    client_stats = stats_result.first()

    if not client_stats:
        raise HTTPException(status_code=404, detail="Client not found")

    # Get all orders for this client
    orders_query = select(Order).where(
        Order.phone == phone
    ).order_by(Order.created_at.desc())

    orders_result = await session.execute(orders_query)
    orders = orders_result.scalars().all()

    # Format orders
    formatted_orders = []
    for order in orders:
        formatted_orders.append({
            "id": order.id,
            "orderNumber": order.orderNumber,
            "customerName": order.customerName,
            "phone": order.phone,
            "total": order.total,
            "status": order.status,
            "created_at": order.created_at,
            "delivery_date": order.delivery_date,
            "delivery_address": order.delivery_address,
            "notes": order.notes
        })

    # Get client notes
    client_query = select(Client).where(Client.phone == phone)
    client_result = await session.execute(client_query)
    client = client_result.scalar_one_or_none()

    # Create client detail response
    client_detail = {
        "phone": client_stats.phone,
        "customerName": client_stats.customerName or "Клиент без имени",
        "first_order_date": client_stats.first_order_date,
        "last_order_date": client_stats.last_order_date,
        "total_orders": client_stats.total_orders,
        "total_spent": int(client_stats.total_spent or 0),
        "average_order": int(client_stats.average_order or 0),
        "customer_since": client_stats.first_order_date.strftime("%d.%m.%Y") if client_stats.first_order_date else None,
        "orders": formatted_orders,
        "notes": client.notes if client else ""
    }

    return client_detail


@router.put("/{phone}/notes")
async def update_client_notes(
    *,
    session: AsyncSession = Depends(get_session),
    phone: str,
    client_update: ClientUpdate
):
    """Update notes for a specific client"""

    # Check if client exists (has orders)
    orders_check = select(Order).where(Order.phone == phone).limit(1)
    orders_result = await session.execute(orders_check)
    if not orders_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Client not found")

    # Get or create client record
    client_query = select(Client).where(Client.phone == phone)
    client_result = await session.execute(client_query)
    client = client_result.scalar_one_or_none()

    if client:
        # Update existing client
        client.notes = client_update.notes
        client.updated_at = datetime.now()
    else:
        # Create new client record
        client = Client(phone=phone, notes=client_update.notes)
        session.add(client)

    await session.commit()
    await session.refresh(client)

    return {"phone": phone, "notes": client.notes, "updated_at": client.updated_at}


@router.get("/stats/dashboard")
async def get_clients_dashboard_stats(
    *,
    session: AsyncSession = Depends(get_session)
):
    """Get client statistics for dashboard"""

    # Total unique clients
    total_clients_query = select(func.count(func.distinct(Order.phone)))
    total_clients_result = await session.execute(total_clients_query)
    total_clients = total_clients_result.scalar()

    # New clients today
    today = datetime.now().date()
    new_clients_today_query = select(func.count(func.distinct(Order.phone))).where(
        func.date(func.min(Order.created_at).over(partition_by=Order.phone)) == today
    )
    new_clients_today_result = await session.execute(new_clients_today_query)
    new_clients_today = new_clients_today_result.scalar() or 0

    # Repeat customers (clients with more than 1 order)
    repeat_customers_query = select(func.count()).select_from(
        select(Order.phone).group_by(Order.phone).having(func.count(Order.id) > 1)
    )
    repeat_customers_result = await session.execute(repeat_customers_query)
    repeat_customers = repeat_customers_result.scalar() or 0

    # Top spending client this month
    current_month = datetime.now().replace(day=1).date()
    top_client_query = select(
        Order.phone,
        func.coalesce(func.max(Order.customerName), "Клиент без имени").label("customerName"),
        func.sum(Order.total).label("monthly_spent")
    ).where(
        func.date(Order.created_at) >= current_month
    ).group_by(Order.phone).order_by(func.sum(Order.total).desc()).limit(1)

    top_client_result = await session.execute(top_client_query)
    top_client = top_client_result.first()

    return {
        "total_clients": total_clients,
        "new_clients_today": new_clients_today,
        "repeat_customers": repeat_customers,
        "repeat_rate": round((repeat_customers / total_clients * 100) if total_clients > 0 else 0, 1),
        "top_client_this_month": {
            "phone": top_client.phone if top_client else None,
            "name": top_client.customerName if top_client else None,
            "spent": int(top_client.monthly_spent) if top_client else 0
        } if top_client else None
    }