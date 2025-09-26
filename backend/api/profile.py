"""
User Profile and Team Management API endpoints
Handles user profile operations and team member management
"""
import secrets
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col

from database import get_session
from models import (
    User, UserRead, UserUpdate, UserRole,
    TeamInvitation, TeamInvitationCreate, TeamInvitationRead,
    InvitationStatus
)
from auth_utils import (
    get_current_active_user, require_manager_or_director,
    get_password_hash
)

router = APIRouter()


@router.get("/", response_model=UserRead)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's profile information
    """
    return UserRead.model_validate(current_user)


@router.put("/", response_model=UserRead)
async def update_user_profile(
    *,
    session: AsyncSession = Depends(get_session),
    profile_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user's profile information
    Note: Role changes require manager/director permissions
    """
    update_data = profile_update.model_dump(exclude_unset=True)

    # Only managers/directors can change roles (including their own)
    if "role" in update_data:
        if current_user.role not in [UserRole.MANAGER, UserRole.DIRECTOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only managers and directors can change user roles"
            )

    # Hash password if provided
    if "password" in update_data:
        password = update_data.pop("password")
        update_data["password_hash"] = get_password_hash(password)

    # Check phone uniqueness if being updated
    if "phone" in update_data and update_data["phone"] != current_user.phone:
        phone_check_query = select(User).where(User.phone == update_data["phone"])
        phone_check_result = await session.execute(phone_check_query)
        existing_user = phone_check_result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use"
            )

    # Apply updates
    for field, value in update_data.items():
        setattr(current_user, field, value)

    await session.commit()
    await session.refresh(current_user)

    return UserRead.model_validate(current_user)


@router.get("/team", response_model=List[UserRead])
async def get_team_members(
    *,
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of users to return"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    active_only: bool = Query(True, description="Show only active users"),
    search: Optional[str] = Query(None, description="Search in user names or phone"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of team members
    All authenticated users can view team members
    """
    # Build query
    query = select(User)

    # Apply filters
    if active_only:
        query = query.where(User.is_active == True)

    if role:
        query = query.where(User.role == role)

    if search:
        query = query.where(
            col(User.name).ilike(f"%{search}%") |
            col(User.phone).ilike(f"%{search}%")
        )

    # Order by creation date (newest first)
    query = query.order_by(User.created_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await session.execute(query)
    users = result.scalars().all()

    return [UserRead.model_validate(user) for user in users]


@router.post("/team/invite", response_model=TeamInvitationRead)
async def invite_team_member(
    *,
    session: AsyncSession = Depends(get_session),
    invitation_data: TeamInvitationCreate,
    current_user: User = Depends(require_manager_or_director)
):
    """
    Invite a new team member
    Requires manager or director role
    """
    # Check if phone number already has an active user
    existing_user_query = select(User).where(User.phone == invitation_data.phone)
    existing_user_result = await session.execute(existing_user_query)
    existing_user = existing_user_result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone number already exists"
        )

    # Check if there's already a pending invitation for this phone
    pending_invitation_query = select(TeamInvitation).where(
        TeamInvitation.phone == invitation_data.phone
    ).where(TeamInvitation.status == InvitationStatus.PENDING)
    pending_invitation_result = await session.execute(pending_invitation_query)
    pending_invitation = pending_invitation_result.scalar_one_or_none()

    if pending_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There's already a pending invitation for this phone number"
        )

    # Generate invitation code (6 digits)
    invitation_code = secrets.randbelow(900000) + 100000  # Ensures 6 digits

    # Create invitation
    invitation = TeamInvitation(
        phone=invitation_data.phone,
        name=invitation_data.name,
        role=invitation_data.role,
        invited_by=current_user.id,
        invitation_code=str(invitation_code),
        expires_at=datetime.utcnow() + timedelta(days=7)  # 7 days expiry
    )

    session.add(invitation)
    await session.commit()
    await session.refresh(invitation)

    # Load the inviting user for response
    invitation_with_user = await session.get(TeamInvitation, invitation.id)
    inviter_query = select(User).where(User.id == current_user.id)
    inviter_result = await session.execute(inviter_query)
    inviter = inviter_result.scalar_one()

    # Create response manually to include inviter info
    return TeamInvitationRead(
        id=invitation.id,
        phone=invitation.phone,
        name=invitation.name,
        role=invitation.role,
        invited_by=invitation.invited_by,
        status=invitation.status,
        invitation_code=invitation.invitation_code,
        expires_at=invitation.expires_at,
        created_at=invitation.created_at,
        updated_at=invitation.updated_at,
        invited_by_user=UserRead.model_validate(inviter)
    )


@router.delete("/team/{user_id}")
async def remove_team_member(
    *,
    session: AsyncSession = Depends(get_session),
    user_id: int,
    current_user: User = Depends(require_manager_or_director)
):
    """
    Remove team member (deactivate user)
    Requires manager or director role
    """
    # Get user to remove
    user_to_remove = await session.get(User, user_id)
    if not user_to_remove:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent self-removal
    if user_to_remove.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself from the team"
        )

    # Directors can only be removed by other directors
    if user_to_remove.role == UserRole.DIRECTOR and current_user.role != UserRole.DIRECTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only directors can remove other directors"
        )

    # Deactivate user instead of deleting (preserves order history)
    user_to_remove.is_active = False
    await session.commit()

    return {"message": f"User {user_to_remove.name} has been removed from the team"}


@router.put("/team/{user_id}/role", response_model=UserRead)
async def change_team_member_role(
    *,
    session: AsyncSession = Depends(get_session),
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(require_manager_or_director)
):
    """
    Change team member's role
    Requires manager or director role
    """
    # Get user to update
    user_to_update = await session.get(User, user_id)
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Only directors can change director roles or promote to director
    if (user_to_update.role == UserRole.DIRECTOR or new_role == UserRole.DIRECTOR):
        if current_user.role != UserRole.DIRECTOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only directors can manage director roles"
            )

    # Prevent self-demotion from director role
    if (user_to_update.id == current_user.id and
        current_user.role == UserRole.DIRECTOR and
        new_role != UserRole.DIRECTOR):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote yourself from director role"
        )

    # Update role
    user_to_update.role = new_role
    await session.commit()
    await session.refresh(user_to_update)

    return UserRead.model_validate(user_to_update)


@router.get("/team/invitations", response_model=List[TeamInvitationRead])
async def get_team_invitations(
    *,
    session: AsyncSession = Depends(get_session),
    status_filter: Optional[InvitationStatus] = Query(None, description="Filter by invitation status"),
    current_user: User = Depends(require_manager_or_director)
):
    """
    Get list of team invitations
    Requires manager or director role
    """
    query = select(TeamInvitation)

    if status_filter:
        query = query.where(TeamInvitation.status == status_filter)

    # Order by creation date (newest first)
    query = query.order_by(TeamInvitation.created_at.desc())

    result = await session.execute(query)
    invitations = result.scalars().all()

    # Load inviter info for each invitation
    invitation_responses = []
    for invitation in invitations:
        inviter_query = select(User).where(User.id == invitation.invited_by)
        inviter_result = await session.execute(inviter_query)
        inviter = inviter_result.scalar_one_or_none()

        invitation_responses.append(TeamInvitationRead(
            id=invitation.id,
            phone=invitation.phone,
            name=invitation.name,
            role=invitation.role,
            invited_by=invitation.invited_by,
            status=invitation.status,
            invitation_code=invitation.invitation_code,
            expires_at=invitation.expires_at,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at,
            invited_by_user=UserRead.model_validate(inviter) if inviter else None
        ))

    return invitation_responses


@router.delete("/team/invitations/{invitation_id}")
async def cancel_invitation(
    *,
    session: AsyncSession = Depends(get_session),
    invitation_id: int,
    current_user: User = Depends(require_manager_or_director)
):
    """
    Cancel a pending invitation
    Requires manager or director role
    """
    invitation = await session.get(TeamInvitation, invitation_id)
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )

    if invitation.status != InvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only cancel pending invitations"
        )

    # Mark as expired instead of deleting
    invitation.status = InvitationStatus.EXPIRED
    await session.commit()

    return {"message": "Invitation cancelled successfully"}


@router.get("/stats", response_model=dict)
async def get_team_stats(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get team statistics
    Available to all authenticated users
    """
    # Count users by role
    role_stats = {}
    for role in UserRole:
        role_query = select(User.id).where(User.role == role).where(User.is_active == True)
        role_result = await session.execute(role_query)
        role_stats[role.value] = len(role_result.scalars().all())

    # Count pending invitations
    pending_invitations_query = select(TeamInvitation.id).where(
        TeamInvitation.status == InvitationStatus.PENDING
    )
    pending_invitations_result = await session.execute(pending_invitations_query)
    pending_invitations_count = len(pending_invitations_result.scalars().all())

    # Total active users
    total_active_query = select(User.id).where(User.is_active == True)
    total_active_result = await session.execute(total_active_query)
    total_active_count = len(total_active_result.scalars().all())

    return {
        "total_active_users": total_active_count,
        "users_by_role": role_stats,
        "pending_invitations": pending_invitations_count
    }