"""
Authentication API endpoints
Handles user login, logout, token refresh, and current user info
"""
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import get_session
from models import (
    User, UserCreate, UserRead, UserRole, UserResponse,
    LoginRequest, LoginResponse, TokenData
)
from auth_utils import (
    authenticate_user, create_access_token, get_current_active_user,
    get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login_for_access_token(
    login_data: LoginRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Authenticate user with phone and password, return JWT token with shop_id
    """
    user = await authenticate_user(session, login_data.phone, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),  # Convert user.id to string for JWT
            "phone": user.phone,
            "role": user.role.name,  # Use enum name (DIRECTOR) instead of value (director)
            "shop_id": user.shop_id  # Add shop_id for multi-tenancy filtering
        },
        expires_delta=access_token_expires
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_user(user)
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    Refresh JWT token for current user with shop_id
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(current_user.id),  # Convert user.id to string for JWT
            "phone": current_user.phone,
            "role": current_user.role.name,  # Use enum name (DIRECTOR) instead of value (director)
            "shop_id": current_user.shop_id  # Add shop_id for multi-tenancy filtering
        },
        expires_delta=access_token_expires
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_user(current_user)
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout current user (client-side token removal required)
    """
    return {
        "message": "Successfully logged out",
        "detail": "Please remove token from client storage"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information
    """
    return UserResponse.from_user(current_user)


@router.post("/register", response_model=UserResponse)
async def register_user(
    *,
    session: AsyncSession = Depends(get_session),
    user_data: UserCreate
):
    """
    Register new user and create their shop
    First registered user becomes shop owner (Director)
    """
    from models import Shop

    # Check if phone number already exists
    existing_user_query = select(User).where(User.phone == user_data.phone)
    existing_user_result = await session.execute(existing_user_query)
    existing_user = existing_user_result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    # Hash password
    password_hash = get_password_hash(user_data.password)

    # Create user
    user_dict = user_data.model_dump(exclude={"password"})
    user_dict["password_hash"] = password_hash

    # Public registration always creates a new shop with DIRECTOR role
    user_dict["role"] = UserRole.DIRECTOR

    user = User(**user_dict)
    session.add(user)
    await session.flush()  # Get user.id without committing

    # Always create shop for public registration
    shop = Shop(
        owner_id=user.id,
        name="Мой магазин",  # Default name, can be changed later
        phone=user.phone
    )
    session.add(shop)
    await session.flush()  # Get shop.id

    # Assign user to their shop
    user.shop_id = shop.id

    await session.commit()
    await session.refresh(user)

    # Send Telegram notification about new registration
    try:
        from services.telegram_notifications import notify_new_registration
        await notify_new_registration(
            shop_id=shop.id,
            shop_name=shop.name,
            owner_name=user.name,
            owner_phone=user.phone,
            city=shop.city.value if shop.city else None,
            address=shop.address
        )
    except Exception as e:
        # Don't fail registration if notification fails
        from core.logging import get_logger
        logger = get_logger(__name__)
        logger.error("registration_notification_failed", error=str(e))

    return UserResponse.from_user(user)


@router.put("/change-password")
async def change_password(
    *,
    session: AsyncSession = Depends(get_session),
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Change current user's password
    """
    from auth_utils import verify_password

    # Verify current password
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password length
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long"
        )

    # Update password
    current_user.password_hash = get_password_hash(new_password)
    await session.commit()

    return {"message": "Password updated successfully"}


@router.get("/verify-token")
async def verify_token_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    """
    Verify if current token is valid and get user info
    """
    return {
        "valid": True,
        "user": UserResponse.from_user(current_user),
        "message": "Token is valid"
    }


@router.get("/users")
async def get_shop_users(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of all users in the current user's shop
    Used for assignment dropdowns
    """
    # Get all active users from the same shop
    query = select(User).where(
        User.shop_id == current_user.shop_id,
        User.is_active == True
    ).order_by(User.name)

    result = await session.execute(query)
    users = result.scalars().all()

    return [UserResponse.from_user(user) for user in users]