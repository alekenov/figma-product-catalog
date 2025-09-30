"""
Content Management API endpoints
Handles FAQs and Static Pages
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import get_session
from models import (
    FAQ, FAQCreate, FAQUpdate, FAQRead,
    StaticPage, StaticPageCreate, StaticPageUpdate, StaticPageRead,
    User, UserRole
)
from auth_utils import get_current_active_user, require_director

router = APIRouter()


# ===============================
# FAQ Endpoints
# ===============================

@router.get("/faqs")
async def get_faqs(
    *,
    session: AsyncSession = Depends(get_session),
    category: Optional[str] = None,
    include_disabled: bool = Query(default=False, description="Include disabled FAQs (admin only)")
):
    """
    Get list of FAQs (public endpoint).
    Returns only enabled FAQs by default, ordered by display_order.
    """
    query = select(FAQ).order_by(FAQ.display_order, FAQ.created_at)

    # Filter by category if provided
    if category:
        query = query.where(FAQ.category == category)

    # Filter by enabled status
    if not include_disabled:
        query = query.where(FAQ.enabled == True)

    result = await session.execute(query)
    faqs = list(result.scalars().all())

    return [FAQRead.model_validate(faq) for faq in faqs]


@router.post("/faqs", response_model=FAQRead)
async def create_faq(
    *,
    session: AsyncSession = Depends(get_session),
    faq_in: FAQCreate,
    current_user: User = Depends(require_director)
):
    """
    Create a new FAQ (admin only).
    Requires director role.
    """
    faq = FAQ.model_validate(faq_in)
    session.add(faq)
    await session.commit()
    await session.refresh(faq)

    return faq


@router.put("/faqs/{faq_id}", response_model=FAQRead)
async def update_faq(
    *,
    session: AsyncSession = Depends(get_session),
    faq_id: int,
    faq_update: FAQUpdate,
    current_user: User = Depends(require_director)
):
    """
    Update an existing FAQ (admin only).
    Requires director role.
    """
    faq = await session.get(FAQ, faq_id)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    # Update fields
    update_data = faq_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(faq, field, value)

    await session.commit()
    await session.refresh(faq)

    return faq


@router.delete("/faqs/{faq_id}")
async def delete_faq(
    *,
    session: AsyncSession = Depends(get_session),
    faq_id: int,
    current_user: User = Depends(require_director)
):
    """
    Delete an FAQ (admin only).
    Requires director role.
    """
    faq = await session.get(FAQ, faq_id)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    await session.delete(faq)
    await session.commit()

    return {"message": f"FAQ {faq_id} deleted successfully"}


# ===============================
# Static Page Endpoints
# ===============================

@router.get("/pages/{slug}", response_model=StaticPageRead)
async def get_page_by_slug(
    *,
    session: AsyncSession = Depends(get_session),
    slug: str
):
    """
    Get static page by slug (public endpoint).
    Returns only if page is enabled.
    """
    query = select(StaticPage).where(StaticPage.slug == slug, StaticPage.enabled == True)
    result = await session.execute(query)
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    return page


@router.get("/pages")
async def get_all_pages(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_director)
):
    """
    Get all static pages (admin only).
    Includes disabled pages.
    Requires director role.
    """
    query = select(StaticPage).order_by(StaticPage.created_at.desc())
    result = await session.execute(query)
    pages = list(result.scalars().all())

    return [StaticPageRead.model_validate(page) for page in pages]


@router.post("/pages", response_model=StaticPageRead)
async def create_page(
    *,
    session: AsyncSession = Depends(get_session),
    page_in: StaticPageCreate,
    current_user: User = Depends(require_director)
):
    """
    Create a new static page (admin only).
    Requires director role.
    """
    # Check if slug already exists
    existing_query = select(StaticPage).where(StaticPage.slug == page_in.slug)
    existing_result = await session.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Page with this slug already exists")

    page = StaticPage.model_validate(page_in)
    session.add(page)
    await session.commit()
    await session.refresh(page)

    return page


@router.put("/pages/{page_id}", response_model=StaticPageRead)
async def update_page(
    *,
    session: AsyncSession = Depends(get_session),
    page_id: int,
    page_update: StaticPageUpdate,
    current_user: User = Depends(require_director)
):
    """
    Update an existing static page (admin only).
    Requires director role.
    """
    page = await session.get(StaticPage, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    # If slug is being changed, check for conflicts
    if page_update.slug and page_update.slug != page.slug:
        existing_query = select(StaticPage).where(StaticPage.slug == page_update.slug)
        existing_result = await session.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Page with this slug already exists")

    # Update fields
    update_data = page_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(page, field, value)

    await session.commit()
    await session.refresh(page)

    return page


@router.delete("/pages/{page_id}")
async def delete_page(
    *,
    session: AsyncSession = Depends(get_session),
    page_id: int,
    current_user: User = Depends(require_director)
):
    """
    Delete a static page (admin only).
    Requires director role.
    """
    page = await session.get(StaticPage, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    await session.delete(page)
    await session.commit()

    return {"message": f"Page {page_id} deleted successfully"}