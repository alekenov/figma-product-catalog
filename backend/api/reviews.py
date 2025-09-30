"""
Review API endpoints
Handles company reviews and product reviews with photo uploads
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlmodel import and_

from database import get_session
from models import (
    CompanyReview, CompanyReviewCreate, CompanyReviewRead,
    ProductReview, ProductReviewCreate, ProductReviewRead,
    ReviewPhoto, ReviewPhotoCreate, ReviewPhotoRead,
    Product
)

router = APIRouter()


@router.get("/company")
async def get_company_reviews(
    *,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get company reviews with statistics (public endpoint).
    Used by ReviewsSection.jsx on homepage.
    """
    # Get all company reviews for stats
    all_reviews_query = select(CompanyReview)
    all_reviews_result = await session.execute(all_reviews_query)
    all_reviews = list(all_reviews_result.scalars().all())

    # Calculate stats
    total_count = len(all_reviews)
    if total_count > 0:
        total_rating = sum(review.rating for review in all_reviews)
        average_rating = round(total_rating / total_count, 1)

        # Rating breakdown
        rating_breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for review in all_reviews:
            rating_breakdown[review.rating] += 1
    else:
        average_rating = 0
        rating_breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

    # Get paginated reviews
    reviews_query = (
        select(CompanyReview)
        .order_by(CompanyReview.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    reviews_result = await session.execute(reviews_query)
    reviews = list(reviews_result.scalars().all())

    return {
        "reviews": [CompanyReviewRead.model_validate(review) for review in reviews],
        "stats": {
            "total_count": total_count,
            "average_rating": average_rating,
            "rating_breakdown": rating_breakdown
        },
        "pagination": {
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }
    }


@router.post("/company", response_model=CompanyReviewRead)
async def create_company_review(
    *,
    session: AsyncSession = Depends(get_session),
    review_in: CompanyReviewCreate
):
    """
    Create a new company review (public endpoint, no auth required for MVP).
    """
    review = CompanyReview.model_validate(review_in)
    session.add(review)
    await session.commit()
    await session.refresh(review)

    return review


@router.get("/product/{product_id}")
async def get_product_reviews(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get product reviews with statistics (public endpoint).
    """
    # Verify product exists
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get all reviews for stats
    all_reviews_query = select(ProductReview).where(ProductReview.product_id == product_id)
    all_reviews_result = await session.execute(all_reviews_query)
    all_reviews = list(all_reviews_result.scalars().all())

    # Calculate stats
    total_count = len(all_reviews)
    if total_count > 0:
        total_rating = sum(review.rating for review in all_reviews)
        average_rating = round(total_rating / total_count, 1)

        # Rating breakdown
        rating_breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for review in all_reviews:
            rating_breakdown[review.rating] += 1
    else:
        average_rating = 0
        rating_breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

    # Get paginated reviews with photos
    reviews_query = (
        select(ProductReview)
        .where(ProductReview.product_id == product_id)
        .order_by(ProductReview.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    reviews_result = await session.execute(reviews_query)
    reviews = list(reviews_result.scalars().all())

    # Load photos for each review
    reviews_with_photos = []
    for review in reviews:
        photos_query = select(ReviewPhoto).where(ReviewPhoto.review_id == review.id)
        photos_result = await session.execute(photos_query)
        photos = list(photos_result.scalars().all())

        review_dict = ProductReviewRead.model_validate(review).model_dump()
        review_dict['photos'] = [ReviewPhotoRead.model_validate(photo) for photo in photos]
        reviews_with_photos.append(review_dict)

    return {
        "reviews": reviews_with_photos,
        "stats": {
            "total_count": total_count,
            "average_rating": average_rating,
            "rating_breakdown": rating_breakdown
        },
        "pagination": {
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }
    }


@router.post("/product/{product_id}", response_model=ProductReviewRead)
async def create_product_review(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    review_in: ProductReviewCreate
):
    """
    Create a new product review (public endpoint, no auth required for MVP).
    """
    # Verify product exists
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Ensure product_id matches
    review_data = review_in.model_dump()
    if review_data.get('product_id') != product_id:
        review_data['product_id'] = product_id

    review = ProductReview(**review_data)
    session.add(review)
    await session.commit()
    await session.refresh(review)

    return review


@router.post("/product/{product_id}/{review_id}/photos", response_model=ReviewPhotoRead)
async def add_review_photo(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    review_id: int,
    photo_in: ReviewPhotoCreate
):
    """
    Add a photo to a product review (public endpoint).
    """
    # Verify review exists and belongs to product
    review = await session.get(ProductReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.product_id != product_id:
        raise HTTPException(status_code=400, detail="Review does not belong to this product")

    # Ensure review_id matches
    photo_data = photo_in.model_dump()
    if photo_data.get('review_id') != review_id:
        photo_data['review_id'] = review_id

    photo = ReviewPhoto(**photo_data)
    session.add(photo)
    await session.commit()
    await session.refresh(photo)

    return photo