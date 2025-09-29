"""
JWT token utilities for authentication.

Handles creation and validation of JWT tokens with proper expiration times
and security measures for Kazakhstan flower shop backend.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from config import settings


# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token with user data.

    Args:
        data: Dictionary containing user information (user_id, phone, role)
        expires_delta: Custom expiration time (default: 15 minutes)

    Returns:
        Encoded JWT token string

    Example:
        token = create_access_token({"user_id": 1, "phone": "+77051234567", "role": "manager"})
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT refresh token with user data.

    Args:
        data: Dictionary containing user information (user_id, phone)
        expires_delta: Custom expiration time (default: 7 days)

    Returns:
        Encoded JWT refresh token string

    Example:
        refresh_token = create_refresh_token({"user_id": 1, "phone": "+77051234567"})
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string to verify
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded token payload as dictionary

    Raises:
        HTTPException: If token is invalid, expired, or wrong type

    Example:
        payload = verify_token(token, "access")
        user_id = payload["user_id"]
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])

        # Check if token has expired
        exp = payload.get("exp")
        if exp is None or datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Ensure required fields exist
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception

        return payload

    except JWTError:
        raise credentials_exception


def get_token_expiry(token: str) -> Optional[datetime]:
    """
    Get expiration time from JWT token without full validation.

    Args:
        token: JWT token string

    Returns:
        Expiration datetime or None if invalid

    Example:
        expiry = get_token_expiry(token)
        if expiry and expiry > datetime.utcnow():
            print("Token is still valid")
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM], options={"verify_exp": False})
        exp = payload.get("exp")
        return datetime.fromtimestamp(exp) if exp else None
    except JWTError:
        return None


def is_token_expired(token: str) -> bool:
    """
    Check if JWT token is expired.

    Args:
        token: JWT token string

    Returns:
        True if token is expired, False otherwise

    Example:
        if is_token_expired(token):
            # Request new token
            pass
    """
    expiry = get_token_expiry(token)
    if expiry is None:
        return True
    return expiry < datetime.utcnow()


def refresh_access_token(refresh_token: str) -> Dict[str, str]:
    """
    Generate new access token from valid refresh token.

    Args:
        refresh_token: Valid refresh token

    Returns:
        Dictionary with new access_token and token_type

    Raises:
        HTTPException: If refresh token is invalid or expired

    Example:
        new_tokens = refresh_access_token(refresh_token)
        access_token = new_tokens["access_token"]
    """
    payload = verify_token(refresh_token, "refresh")

    # Create new access token with user data from refresh token
    access_token_data = {
        "user_id": payload["user_id"],
        "phone": payload.get("phone"),
        "role": payload.get("role")
    }

    access_token = create_access_token(access_token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }