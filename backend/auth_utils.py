"""
Authentication utilities for JWT token handling and password hashing
"""
from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import os

# Structured logging
from core.logging import get_logger
logger = get_logger(__name__)

# Use Render config if DATABASE_URL is set, otherwise use SQLite for local dev
if os.getenv("DATABASE_URL"):
    from config_render import settings
else:
    from config_sqlite import settings
from database import get_session
from models import User, UserRole, TokenData
from utils import normalize_phone_number

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Security scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Verify JWT token and extract user data."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])

        # JWT payload values are always strings - sub claim is now string
        user_id_str = payload.get("sub")
        phone: str = payload.get("phone")
        role: str = payload.get("role")
        shop_id: Optional[int] = payload.get("shop_id")  # Extract shop_id for multi-tenancy

        if user_id_str is None:
            logger.error("jwt_missing_sub_claim", payload_keys=list(payload.keys()))
            raise JWTError("Invalid token: missing user ID")

        # Convert string user_id to integer for database lookup
        try:
            user_id: int = int(user_id_str)
        except (ValueError, TypeError) as e:
            logger.error("jwt_invalid_user_id_format", user_id_str=user_id_str, error=str(e))
            raise JWTError("Invalid token: user ID must be numeric")

        logger.info("jwt_verified", user_id=user_id, phone=phone, role=role, shop_id=shop_id)
        token_data = TokenData(user_id=user_id, phone=phone, role=role, shop_id=shop_id)
        return token_data
    except JWTError as jwt_err:
        logger.error("jwt_verification_failed", jwt_error=str(jwt_err))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error("jwt_verification_unexpected_error", error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def authenticate_user(session: AsyncSession, phone: str, password: str) -> Optional[User]:
    """Authenticate user by phone and password with phone normalization."""
    # Normalize phone number to +7XXXXXXXXXX format
    normalized_phone = normalize_phone_number(phone)

    query = select(User).where(User.phone == normalized_phone).where(User.is_active == True)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


async def get_current_user(
    token: str = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extract token from bearer
        token_str = token.credentials
        logger.debug("token_extraction_started", token_length=len(token_str))

        # Verify and decode token
        token_data = verify_token(token_str)
        logger.debug("token_decoded", user_id=token_data.user_id)

        # Get user from database - ensure user_id is int
        user_id = int(token_data.user_id)  # Extra safety cast
        user = await session.get(User, user_id)

        if user is None:
            logger.warning("user_not_found_in_database", user_id=user_id)
            raise credentials_exception

        if not user.is_active:
            logger.warning("user_inactive", user_id=user_id, user_name=user.name, user_phone=user.phone)
            raise credentials_exception

        logger.info("user_authenticated", user_id=user.id, user_name=user.name, user_phone=user.phone, user_role=user.role)
        return user

    except JWTError as jwt_err:
        logger.error("jwt_error_in_get_current_user", jwt_error=str(jwt_err))
        raise credentials_exception
    except AttributeError as attr_err:
        logger.error("token_format_error", error=str(attr_err))
        raise credentials_exception
    except ValueError as val_err:
        logger.error("value_error_in_get_current_user", error=str(val_err))
        raise credentials_exception
    except Exception as e:
        logger.error("unexpected_error_in_get_current_user", error=str(e), error_type=type(e).__name__)
        raise credentials_exception


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(required_role: UserRole):
    """Dependency factory to require specific user role."""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {required_role.value} role"
            )
        return current_user
    return role_checker


def require_roles(allowed_roles: list[UserRole]):
    """Dependency factory to require one of multiple user roles."""
    async def roles_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            roles_str = ", ".join([role.value for role in allowed_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of these roles: {roles_str}"
            )
        return current_user
    return roles_checker


def require_superadmin(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to require superadmin access."""
    if not current_user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires superadmin access"
        )
    return current_user


# Commonly used role dependencies
require_director = require_role(UserRole.DIRECTOR)
require_manager_or_director = require_roles([UserRole.MANAGER, UserRole.DIRECTOR])
require_staff = require_roles([UserRole.FLORIST, UserRole.MANAGER, UserRole.DIRECTOR])


async def get_current_user_shop_id(current_user: User = Depends(get_current_active_user)) -> int:
    """
    Dependency to get current user's shop_id for multi-tenancy filtering.
    Raises HTTPException if user has no shop assigned.
    """
    if current_user.shop_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not assigned to any shop"
        )
    return current_user.shop_id