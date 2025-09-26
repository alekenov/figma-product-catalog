"""
Authentication service for Kazakhstan flower shop backend.

Handles user authentication, password management, and authentication-related
business logic with support for Kazakhstan phone number formats.
"""

import re
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlmodel import Session, select

from database import get_session
from models import User, UserCreate, UserRead, UserRole, LoginRequest, LoginResponse, TokenData
from auth.jwt import create_access_token, create_refresh_token, verify_token


# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


class AuthService:
    """Authentication service for managing user authentication and authorization."""

    def __init__(self, session: Session):
        """Initialize AuthService with database session."""
        self.session = session

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain text password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string

        Example:
            hashed = AuthService.hash_password("secure_password")
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored hashed password

        Returns:
            True if password matches, False otherwise

        Example:
            is_valid = AuthService.verify_password("password", user.password_hash)
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def validate_kazakhstan_phone(phone: str) -> bool:
        """
        Validate Kazakhstan phone number format.

        Accepts formats:
        - +7 7XX XXX XX XX
        - +77XXXXXXXXX
        - 87XXXXXXXXX
        - 77XXXXXXXXX

        Args:
            phone: Phone number string

        Returns:
            True if valid Kazakhstan number, False otherwise

        Example:
            is_valid = AuthService.validate_kazakhstan_phone("+7 705 123 45 67")
        """
        # Remove all non-digit characters for validation
        digits_only = re.sub(r'\D', '', phone)

        # Kazakhstan mobile patterns
        patterns = [
            r'^7(70[0-9]|71[0-9]|72[0-9]|73[0-9]|74[0-9]|75[0-9]|76[0-9]|77[0-9]|78[0-9])\d{7}$',  # +7 7XX XXXXXXX
            r'^87(70[0-9]|71[0-9]|72[0-9]|73[0-9]|74[0-9]|75[0-9]|76[0-9]|77[0-9]|78[0-9])\d{7}$'   # 8 7XX XXXXXXX
        ]

        for pattern in patterns:
            if re.match(pattern, digits_only):
                return True

        return False

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """
        Normalize Kazakhstan phone number to standard format (+7XXXXXXXXXX).

        Args:
            phone: Phone number in any accepted format

        Returns:
            Normalized phone number string

        Example:
            normalized = AuthService.normalize_phone("8 705 123 45 67")
            # Returns: "+77051234567"
        """
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)

        # Convert 87XXXXXXXXX to 77XXXXXXXXX
        if digits_only.startswith('87'):
            digits_only = '7' + digits_only[2:]

        # Add + prefix if not present
        if not digits_only.startswith('7'):
            digits_only = '7' + digits_only

        return '+' + digits_only

    async def get_user_by_phone(self, phone: str) -> Optional[User]:
        """
        Get user by phone number.

        Args:
            phone: Phone number (will be normalized)

        Returns:
            User object if found, None otherwise

        Example:
            user = await auth_service.get_user_by_phone("+77051234567")
        """
        normalized_phone = self.normalize_phone(phone)
        statement = select(User).where(User.phone == normalized_phone, User.is_active == True)
        result = await self.session.exec(statement)
        return result.first()

    async def authenticate_user(self, login_request: LoginRequest) -> Optional[User]:
        """
        Authenticate user with phone and password.

        Args:
            login_request: Login credentials

        Returns:
            User object if authentication successful, None otherwise

        Example:
            user = await auth_service.authenticate_user(LoginRequest(
                phone="+77051234567",
                password="password"
            ))
        """
        # Validate phone format
        if not self.validate_kazakhstan_phone(login_request.phone):
            return None

        user = await self.get_user_by_phone(login_request.phone)
        if not user:
            return None

        if not self.verify_password(login_request.password, user.password_hash):
            return None

        return user

    async def create_user(self, user_create: UserCreate) -> User:
        """
        Create new user with hashed password.

        Args:
            user_create: User creation data

        Returns:
            Created user object

        Raises:
            HTTPException: If phone format invalid or user exists

        Example:
            user = await auth_service.create_user(UserCreate(
                name="John Doe",
                phone="+77051234567",
                password="secure_password",
                role=UserRole.FLORIST
            ))
        """
        # Validate phone format
        if not self.validate_kazakhstan_phone(user_create.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Kazakhstan phone number format"
            )

        # Normalize phone number
        normalized_phone = self.normalize_phone(user_create.phone)

        # Check if user already exists
        existing_user = await self.get_user_by_phone(normalized_phone)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this phone number already exists"
            )

        # Create user with hashed password
        user_data = user_create.dict(exclude={'password'})
        user_data['phone'] = normalized_phone
        user_data['password_hash'] = self.hash_password(user_create.password)

        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def login_user(self, login_request: LoginRequest) -> LoginResponse:
        """
        Login user and generate tokens.

        Args:
            login_request: Login credentials

        Returns:
            Login response with access token and user info

        Raises:
            HTTPException: If authentication fails

        Example:
            response = await auth_service.login_user(LoginRequest(
                phone="+77051234567",
                password="password"
            ))
        """
        user = await self.authenticate_user(login_request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone number or password"
            )

        # Create tokens
        token_data = {
            "user_id": user.id,
            "phone": user.phone,
            "role": user.role.value
        }

        access_token = create_access_token(token_data)

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserRead.from_orm(user)
        )

    async def get_current_user(self, token: str) -> User:
        """
        Get current user from JWT token.

        Args:
            token: JWT access token

        Returns:
            Current user object

        Raises:
            HTTPException: If token invalid or user not found

        Example:
            user = await auth_service.get_current_user(token)
        """
        # Verify token
        payload = verify_token(token)
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Get user from database
        statement = select(User).where(User.id == user_id, User.is_active == True)
        result = await self.session.exec(statement)
        user = result.first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        return user

    async def update_user_password(self, user_id: int, new_password: str) -> User:
        """
        Update user password.

        Args:
            user_id: User ID
            new_password: New plain text password

        Returns:
            Updated user object

        Raises:
            HTTPException: If user not found

        Example:
            user = await auth_service.update_user_password(1, "new_password")
        """
        statement = select(User).where(User.id == user_id)
        result = await self.session.exec(statement)
        user = result.first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.password_hash = self.hash_password(new_password)
        user.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def deactivate_user(self, user_id: int) -> User:
        """
        Deactivate user account.

        Args:
            user_id: User ID to deactivate

        Returns:
            Deactivated user object

        Raises:
            HTTPException: If user not found

        Example:
            user = await auth_service.deactivate_user(1)
        """
        statement = select(User).where(User.id == user_id)
        result = await self.session.exec(statement)
        user = result.first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.is_active = False
        user.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(user)

        return user


# Dependency injection functions
async def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    """
    Dependency to get AuthService instance.

    Returns:
        Configured AuthService instance

    Usage:
        @app.post("/login")
        async def login(
            request: LoginRequest,
            auth_service: AuthService = Depends(get_auth_service)
        ):
    """
    return AuthService(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Dependency to get current authenticated user.

    Args:
        credentials: HTTP Bearer credentials
        auth_service: Auth service instance

    Returns:
        Current user object

    Raises:
        HTTPException: If authentication fails

    Usage:
        @app.get("/protected")
        async def protected_route(
            current_user: User = Depends(get_current_user)
        ):
    """
    return await auth_service.get_current_user(credentials.credentials)


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user.

    Args:
        current_user: Current user from token

    Returns:
        Active user object

    Raises:
        HTTPException: If user is inactive

    Usage:
        @app.get("/user-info")
        async def get_user_info(
            user: User = Depends(get_current_active_user)
        ):
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user