"""
Delivery logistics API endpoints for Phase 3.
Handles delivery slot calculation, validation, and feasibility checks.
"""
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from .delivery_parser import DeliveryParser, ParsedDelivery as ParsedDeliveryResult


router = APIRouter(prefix="/delivery", tags=["delivery"])


# ============================================================================
# Models
# ============================================================================

class DeliverySlot(BaseModel):
    """Delivery time slot"""
    start_time: str  # ISO format datetime
    end_time: str
    available: bool
    reason: Optional[str] = None  # Why unavailable


class DeliveryValidation(BaseModel):
    """Delivery time validation result"""
    is_valid: bool
    delivery_time: str
    reason: Optional[str] = None
    alternative_slots: Optional[List[DeliverySlot]] = None


class DeliveryFeasibility(BaseModel):
    """Delivery feasibility check result"""
    is_feasible: bool
    earliest_delivery: Optional[str] = None
    reason: Optional[str] = None


class DeliveryParseRequest(BaseModel):
    """Request body for parsing natural language delivery date/time"""
    date_str: str
    time_str: str


class ParsedDelivery(BaseModel):
    """Parsed delivery date/time result"""
    date: str  # YYYY-MM-DD format
    time: str  # HH:MM format
    iso_datetime: str  # ISO 8601 format
    original_date: str
    original_time: str


# ============================================================================
# Helper functions
# ============================================================================

def parse_time(time_str: str) -> time:
    """Parse time string in HH:MM format"""
    try:
        hour, minute = map(int, time_str.split(':'))
        return time(hour, minute)
    except:
        raise ValueError(f"Invalid time format: {time_str}")


def calculate_prep_time(product_ids: List[int]) -> int:
    """Calculate bouquet preparation time in minutes"""
    # Simple logic: 30 min base + 10 min per product
    base_time = 30
    per_product = 10
    return base_time + (len(product_ids) * per_product)


def calculate_delivery_time() -> int:
    """Calculate delivery time in minutes"""
    # Simple logic: 60 minutes for delivery
    return 60


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/slots", response_model=List[DeliverySlot])
async def get_delivery_slots(
    shop_id: int = Query(..., description="Shop ID"),
    date: str = Query(..., description="Delivery date (YYYY-MM-DD)"),
    product_ids: Optional[str] = Query(None, description="Comma-separated product IDs")
):
    """
    Get available delivery time slots for a specific date.

    Takes into account:
    - Shop working hours
    - Bouquet preparation time
    - Delivery time
    - Current time (can't deliver in the past)
    """
    # Parse input
    try:
        delivery_date = datetime.fromisoformat(date).date()
    except:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Parse product IDs
    products = []
    if product_ids:
        try:
            products = [int(pid) for pid in product_ids.split(',')]
        except:
            raise HTTPException(status_code=400, detail="Invalid product_ids format")

    # Calculate preparation and delivery time
    prep_minutes = calculate_prep_time(products)
    delivery_minutes = calculate_delivery_time()
    total_lead_time = prep_minutes + delivery_minutes

    # Shop working hours (hardcoded for now, should come from DB)
    shop_open = time(9, 0)
    shop_close = time(21, 0)

    # Generate slots (2-hour windows)
    slots = []
    current_time = datetime.now()
    slot_duration = timedelta(hours=2)

    # Start from shop opening or current time + lead time (whichever is later)
    if delivery_date == current_time.date():
        # Same day delivery - start from current time + lead time
        earliest_start = current_time + timedelta(minutes=total_lead_time)
        start_hour = max(earliest_start.hour, shop_open.hour)
    else:
        # Future date - start from shop opening
        start_hour = shop_open.hour

    # Generate slots from start hour to closing
    current_slot_start = datetime.combine(delivery_date, time(start_hour, 0))
    shop_closing_datetime = datetime.combine(delivery_date, shop_close)

    while current_slot_start < shop_closing_datetime:
        slot_end = current_slot_start + slot_duration

        # Check if slot is in the past
        is_available = current_slot_start >= current_time + timedelta(minutes=total_lead_time)

        # Check if slot ends before shop closes
        if slot_end > shop_closing_datetime:
            is_available = False
            reason = "Slot extends past shop closing time"
        elif not is_available:
            reason = f"Not enough time for preparation ({prep_minutes}m) and delivery ({delivery_minutes}m)"
        else:
            reason = None

        slots.append(DeliverySlot(
            start_time=current_slot_start.isoformat(),
            end_time=slot_end.isoformat(),
            available=is_available,
            reason=reason
        ))

        # Next slot (2-hour intervals)
        current_slot_start += slot_duration

    return slots


@router.post("/validate", response_model=DeliveryValidation)
async def validate_delivery_time(
    shop_id: int = Query(..., description="Shop ID"),
    delivery_time: str = Query(..., description="Requested delivery time (ISO format)"),
    product_ids: Optional[str] = Query(None, description="Comma-separated product IDs")
):
    """
    Validate if a specific delivery time is feasible.

    Returns validation result with reason if invalid,
    and suggests alternative slots.
    """
    # Parse delivery time
    try:
        requested_time = datetime.fromisoformat(delivery_time)
    except:
        raise HTTPException(status_code=400, detail="Invalid delivery_time format. Use ISO format")

    # Parse product IDs
    products = []
    if product_ids:
        try:
            products = [int(pid) for pid in product_ids.split(',')]
        except:
            raise HTTPException(status_code=400, detail="Invalid product_ids format")

    # Calculate lead time
    prep_minutes = calculate_prep_time(products)
    delivery_minutes = calculate_delivery_time()
    total_lead_time = prep_minutes + delivery_minutes

    current_time = datetime.now()
    earliest_possible = current_time + timedelta(minutes=total_lead_time)

    # Shop working hours
    shop_open = time(9, 0)
    shop_close = time(21, 0)

    # Validation checks
    is_valid = True
    reason = None

    # Check 1: Not in the past
    if requested_time < earliest_possible:
        is_valid = False
        reason = f"Requested time is too soon. Need at least {total_lead_time} minutes for prep and delivery. Earliest: {earliest_possible.isoformat()}"

    # Check 2: Within shop hours
    elif requested_time.time() < shop_open or requested_time.time() > shop_close:
        is_valid = False
        reason = f"Delivery time outside shop hours ({shop_open.strftime('%H:%M')} - {shop_close.strftime('%H:%M')})"

    # If invalid, suggest alternatives
    alternative_slots = None
    if not is_valid:
        # Get available slots for that date
        date_str = requested_time.date().isoformat()
        alternative_slots = await get_delivery_slots(
            shop_id=shop_id,
            date=date_str,
            product_ids=product_ids
        )
        # Filter to only available slots
        alternative_slots = [slot for slot in alternative_slots if slot.available][:3]  # Top 3

    return DeliveryValidation(
        is_valid=is_valid,
        delivery_time=delivery_time,
        reason=reason,
        alternative_slots=alternative_slots
    )


@router.get("/feasibility", response_model=DeliveryFeasibility)
async def check_delivery_feasibility(
    shop_id: int = Query(..., description="Shop ID"),
    delivery_date: str = Query(..., description="Desired delivery date (YYYY-MM-DD)"),
    product_ids: Optional[str] = Query(None, description="Comma-separated product IDs")
):
    """
    Check if delivery is feasible on a given date.

    Returns earliest possible delivery time if feasible.
    """
    # Parse date
    try:
        desired_date = datetime.fromisoformat(delivery_date).date()
    except:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Parse product IDs
    products = []
    if product_ids:
        try:
            products = [int(pid) for pid in product_ids.split(',')]
        except:
            raise HTTPException(status_code=400, detail="Invalid product_ids format")

    # Calculate lead time
    prep_minutes = calculate_prep_time(products)
    delivery_minutes = calculate_delivery_time()
    total_lead_time = prep_minutes + delivery_minutes

    current_time = datetime.now()
    earliest_possible_datetime = current_time + timedelta(minutes=total_lead_time)
    earliest_possible_date = earliest_possible_datetime.date()

    # Shop hours
    shop_open = time(9, 0)
    shop_close = time(21, 0)

    # Check if desired date is in the past
    if desired_date < current_time.date():
        return DeliveryFeasibility(
            is_feasible=False,
            reason="Cannot deliver in the past",
            earliest_delivery=earliest_possible_datetime.isoformat()
        )

    # Check if desired date is too soon
    if desired_date < earliest_possible_date:
        return DeliveryFeasibility(
            is_feasible=False,
            reason=f"Not enough time for preparation and delivery. Need {total_lead_time} minutes minimum",
            earliest_delivery=earliest_possible_datetime.isoformat()
        )

    # Check if it's same day and already past closing time
    if desired_date == current_time.date():
        if current_time.time() > shop_close:
            # Too late today, earliest is tomorrow at opening
            tomorrow = current_time + timedelta(days=1)
            earliest_tomorrow = datetime.combine(tomorrow.date(), shop_open)
            return DeliveryFeasibility(
                is_feasible=False,
                reason="Shop is closed for today",
                earliest_delivery=earliest_tomorrow.isoformat()
            )

    # If we get here, delivery is feasible
    # Calculate earliest delivery time on that date
    if desired_date == earliest_possible_date:
        earliest_delivery_time = earliest_possible_datetime
    else:
        # Future date - can deliver from shop opening
        earliest_delivery_time = datetime.combine(desired_date, shop_open)

    return DeliveryFeasibility(
        is_feasible=True,
        earliest_delivery=earliest_delivery_time.isoformat(),
        reason=None
    )


@router.post("/parse", response_model=ParsedDelivery)
async def parse_delivery_datetime(request: DeliveryParseRequest):
    """
    Parse natural language delivery date and time to ISO format.

    Centralizes parsing logic that was previously duplicated in MCP server.
    Supports Russian and English natural language expressions.

    Supported date formats:
    - "сегодня", "today" → today's date
    - "завтра", "tomorrow" → tomorrow's date
    - "послезавтра", "day after tomorrow" → day after tomorrow
    - "через N дней" → N days from today
    - "YYYY-MM-DD" → exact date

    Supported time formats:
    - "утром", "morning" → 10:00
    - "днем", "afternoon" → 14:00
    - "вечером", "evening" → 18:00
    - "как можно скорее", "asap" → nearest available slot
    - "HH:MM" → exact time

    Example request:
        POST /api/v1/delivery/parse
        {
            "date_str": "завтра",
            "time_str": "днем"
        }

    Example response:
        {
            "date": "2025-01-16",
            "time": "14:00",
            "iso_datetime": "2025-01-16T14:00:00",
            "original_date": "завтра",
            "original_time": "днем"
        }
    """
    try:
        parsed = DeliveryParser.parse(request.date_str, request.time_str)

        return ParsedDelivery(
            date=parsed.date.strftime('%Y-%m-%d'),
            time=parsed.time,
            iso_datetime=parsed.iso_datetime,
            original_date=parsed.original_date,
            original_time=parsed.original_time
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse delivery date/time: {str(e)}"
        )
