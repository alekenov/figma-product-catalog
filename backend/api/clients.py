from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func, col
from database import get_session
from models import Order, OrderStatus, Client, ClientUpdate, ClientCreate
from services.client_service import client_service
from auth_utils import get_current_user_shop_id

router = APIRouter()


@router.get("/")
async def get_clients(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    skip: int = Query(0, ge=0, description="Number of clients to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of clients to return"),
    search: Optional[str] = Query(None, description="Search in customer name or phone"),
):
    """Get list of all clients including those without orders"""

    # First, get all clients from the Client table - filter by shop_id for multi-tenancy
    clients_query = select(Client).where(Client.shop_id == shop_id)

    # Apply search filter if provided
    if search:
        # Normalize search term for phone number matching
        normalized_search = client_service.normalize_phone(search) if search.replace('+', '').replace('-', '').replace(' ', '').isdigit() else search
        clients_query = clients_query.where(
            or_(
                Client.phone.ilike(f"%{search}%"),
                Client.phone.ilike(f"%{normalized_search}%") if normalized_search != search else False,
                Client.customerName.ilike(f"%{search}%")
            )
        )

    # Get all clients
    clients_result = await session.execute(clients_query)
    all_clients = clients_result.scalars().all()

    # Now get order statistics for clients who have orders - filter by shop_id for multi-tenancy
    order_stats_query = (
        select(
            Order.phone,
            func.coalesce(func.max(Order.customerName), "Клиент без имени").label("customerName"),
            func.min(Order.created_at).label("first_order_date"),
            func.max(Order.created_at).label("last_order_date"),
            func.count(Order.id).label("total_orders"),
            func.sum(Order.total).label("total_spent"),
            func.avg(Order.total).label("average_order"),
            func.max(Order.orderNumber).label("last_order_number"),
            func.max(Order.status).label("last_order_status")
        )
        .where(Order.shop_id == shop_id)
        .group_by(Order.phone)
    )

    order_stats_result = await session.execute(order_stats_query)
    order_stats = {row.phone: row for row in order_stats_result.all()}

    # Combine client data with order statistics
    clients = []

    # First add clients that have orders
    added_phones = set()
    for phone, stats in order_stats.items():
        # Find the client record
        client_record = next((c for c in all_clients if c.phone == phone), None)

        # Apply search filter on customer name from orders
        if search and stats.customerName:
            if search.lower() not in stats.customerName.lower() and search not in phone:
                continue

        client = {
            "id": client_record.id if client_record else None,
            "phone": phone,
            "customerName": stats.customerName or "Клиент без имени",
            "first_order_date": stats.first_order_date,
            "last_order_date": stats.last_order_date,
            "total_orders": stats.total_orders,
            "total_spent": int(stats.total_spent or 0),
            "average_order": int(stats.average_order or 0),
            "last_order_number": stats.last_order_number,
            "last_order_status": stats.last_order_status,
            "customer_since": stats.first_order_date.strftime("%d.%m.%Y") if stats.first_order_date else None
        }
        clients.append(client)
        added_phones.add(phone)

    # Then add clients without orders (new clients created via POST)
    for client_record in all_clients:
        if client_record.phone not in added_phones:
            # Use the customerName from the client record
            client = {
                "id": client_record.id,
                "phone": client_record.phone,
                "customerName": client_record.customerName or f"Клиент {client_record.phone}",
                "first_order_date": None,
                "last_order_date": None,
                "total_orders": 0,
                "total_spent": 0,
                "average_order": 0,
                "last_order_number": None,
                "last_order_status": None,
                "customer_since": client_record.created_at.strftime("%d.%m.%Y") if client_record.created_at else None
            }

            # Apply search filter
            if search:
                if search not in client_record.phone and search.lower() not in client["customerName"].lower():
                    continue

            clients.append(client)

    # Sort by total spent (clients with orders first, then new clients)
    clients.sort(key=lambda x: x["total_spent"], reverse=True)

    # Apply pagination
    paginated_clients = clients[skip:skip + limit]

    return paginated_clients


@router.post("/", status_code=201)
async def create_client(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    client_create: ClientCreate
):
    """Create a new client"""

    try:
        # Use the client service to create client with normalized phone and shop_id
        new_client, client_created = await client_service.get_or_create_client(
            session,
            client_create.phone,
            shop_id,
            client_create.customerName,
            client_create.notes or ""
        )

        if not client_created:
            raise HTTPException(
                status_code=400,
                detail=f"Client with phone {client_create.phone} already exists"
            )

        # Return client with additional info
        return {
            "id": new_client.id,
            "phone": new_client.phone,
            "customerName": new_client.customerName,
            "notes": new_client.notes,
            "created_at": new_client.created_at,
            "updated_at": new_client.updated_at,
            "customer_since": new_client.created_at.strftime("%d.%m.%Y") if new_client.created_at else None,
            "total_orders": 0,
            "total_spent": 0,
            "average_order": 0
        }

    except Exception as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=400,
                detail=f"Client with phone {client_create.phone} already exists"
            )
        raise HTTPException(status_code=500, detail=f"Failed to create client: {str(e)}")


@router.post("/sync")
async def sync_clients(
    *,
    session: AsyncSession = Depends(get_session)
):
    """Synchronize client records from orders - creates Client records for all unique phone numbers in orders"""

    # Use the client service for batch sync
    result = await client_service.batch_sync_clients_from_orders(session)
    return result


@router.get("/{client_id}")
async def get_client_detail(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    client_id: int
):
    """Get detailed information about a specific client including order history"""

    # Get client record by ID - filter by shop_id for multi-tenancy
    client_query = select(Client).where(Client.id == client_id).where(Client.shop_id == shop_id)
    client_result = await session.execute(client_query)
    client_record = client_result.scalar_one_or_none()

    if not client_record:
        raise HTTPException(status_code=404, detail="Client not found")

    phone = client_record.phone

    # Get client statistics - filter by shop_id for multi-tenancy
    stats_query = select(
        Order.phone,
        func.coalesce(func.max(Order.customerName), "Клиент без имени").label("customerName"),
        func.min(Order.created_at).label("first_order_date"),
        func.max(Order.created_at).label("last_order_date"),
        func.count(Order.id).label("total_orders"),
        func.sum(Order.total).label("total_spent"),
        func.avg(Order.total).label("average_order")
    ).where(Order.phone == phone).where(Order.shop_id == shop_id).group_by(Order.phone)

    stats_result = await session.execute(stats_query)
    client_stats = stats_result.first()

    # If client has no orders, create default statistics
    if not client_stats:
        # Client has no orders yet - use default values
        client_detail = {
            "id": client_record.id,
            "phone": client_record.phone,
            "customerName": client_record.customerName or f"Клиент {client_record.phone}",
            "first_order_date": None,
            "last_order_date": None,
            "total_orders": 0,
            "total_spent": 0,
            "average_order": 0,
            "customer_since": client_record.created_at.strftime("%d.%m.%Y") if client_record.created_at else None,
            "orders": [],
            "notes": client_record.notes or ""
        }
    else:
        # Get all orders for this client - filter by shop_id for multi-tenancy
        orders_query = select(Order).where(
            Order.phone == phone
        ).where(Order.shop_id == shop_id).order_by(Order.created_at.desc())

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

        # Create client detail response for client with orders
        # Use client_record.customerName if set, otherwise fall back to orders
        client_detail = {
            "id": client_record.id,
            "phone": client_stats.phone,
            "customerName": client_record.customerName or client_stats.customerName or "Клиент без имени",
            "first_order_date": client_stats.first_order_date,
            "last_order_date": client_stats.last_order_date,
            "total_orders": client_stats.total_orders,
            "total_spent": int(client_stats.total_spent or 0),
            "average_order": int(client_stats.average_order or 0),
            "customer_since": client_stats.first_order_date.strftime("%d.%m.%Y") if client_stats.first_order_date else None,
            "orders": formatted_orders,
            "notes": client_record.notes or ""
        }

    return client_detail


@router.put("/{client_id}/notes")
async def update_client_notes(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    client_id: int,
    client_update: ClientUpdate
):
    """Update notes for a specific client"""

    # Get client record by ID - filter by shop_id for multi-tenancy
    client_query = select(Client).where(Client.id == client_id).where(Client.shop_id == shop_id)
    client_result = await session.execute(client_query)
    client = client_result.scalar_one_or_none()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Update client notes
    client.notes = client_update.notes
    client.updated_at = datetime.now()

    await session.commit()
    await session.refresh(client)

    return {"id": client.id, "phone": client.phone, "notes": client.notes, "updated_at": client.updated_at}


@router.put("/{client_id}")
async def update_client(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    client_id: int,
    client_update: ClientUpdate
):
    """Update client information (name, phone, notes)"""

    # Get client record by ID - filter by shop_id for multi-tenancy
    client_query = select(Client).where(Client.id == client_id).where(Client.shop_id == shop_id)
    client_result = await session.execute(client_query)
    client = client_result.scalar_one_or_none()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Track if we need to update anything
    updated = False

    # Update customer name if provided
    if client_update.customerName is not None:
        client.customerName = client_update.customerName
        updated = True

    # Update phone if provided
    if client_update.phone is not None:
        # Normalize the phone number
        normalized_phone = client_service.normalize_phone(client_update.phone)

        # Check if phone is being changed to a different number
        if normalized_phone != client.phone:
            # Check if new phone already exists for another client in this shop
            existing_client_query = select(Client).where(
                Client.phone == normalized_phone,
                Client.shop_id == shop_id,
                Client.id != client_id  # Exclude current client
            )
            existing_result = await session.execute(existing_client_query)
            existing_client = existing_result.scalar_one_or_none()

            if existing_client:
                raise HTTPException(
                    status_code=400,
                    detail=f"Phone number {normalized_phone} is already registered for another client"
                )

            # CASCADE UPDATE: Update phone in all orders for this client
            # This prevents orphaned records and duplicate client entries in the list
            old_phone = client.phone
            orders_update_stmt = (
                update(Order)
                .where(Order.phone == old_phone)
                .where(Order.shop_id == shop_id)
                .values(phone=normalized_phone)
            )
            await session.execute(orders_update_stmt)

            client.phone = normalized_phone
            updated = True

    # Update notes if provided
    if client_update.notes is not None:
        client.notes = client_update.notes
        updated = True

    # Update timestamp if anything changed
    if updated:
        client.updated_at = datetime.now()
        await session.commit()
        await session.refresh(client)

    return {
        "id": client.id,
        "phone": client.phone,
        "customerName": client.customerName,
        "notes": client.notes,
        "updated_at": client.updated_at
    }


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
    # Create subquery to get first order date for each client
    first_order_subquery = select(
        Order.phone,
        func.min(Order.created_at).label("first_order")
    ).group_by(Order.phone).subquery()

    # Count clients whose first order was today
    new_clients_today_query = select(func.count()).select_from(
        first_order_subquery
    ).where(func.date(first_order_subquery.c.first_order) == today)

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


@router.post("/normalize-phone")
async def normalize_phone_endpoint(
    phone: str
):
    """Normalize phone number for consistent storage"""
    try:
        normalized = client_service.normalize_phone(phone)
        return {
            "original": phone,
            "normalized": normalized,
            "valid": len(normalized) >= 10
        }
    except Exception as e:
        return {
            "original": phone,
            "normalized": phone,
            "valid": False,
            "error": str(e)
        }


@router.post("/cache/clear")
async def clear_client_cache():
    """Clear client cache - useful for development/testing"""
    await client_service.clear_cache()
    return {"message": "Client cache cleared successfully"}