"""
Team management service for Kazakhstan flower shop backend.

Handles team member invitations, invitation code generation/validation,
and team management operations with proper role-based access control.
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from sqlmodel import Session, select, and_

from database import get_session
from models import (
    User, UserCreate, UserRead, UserRole,
    TeamInvitation, TeamInvitationCreate, TeamInvitationRead,
    InvitationStatus
)
from services.auth_service import AuthService, get_auth_service


class TeamService:
    """Service for managing team members and invitations."""

    def __init__(self, session: Session, auth_service: AuthService):
        """Initialize TeamService with database session and auth service."""
        self.session = session
        self.auth_service = auth_service

    @staticmethod
    def generate_invitation_code() -> str:
        """
        Generate a 6-digit invitation code.

        Returns:
            Random 6-digit alphanumeric code

        Example:
            code = TeamService.generate_invitation_code()
            # Returns something like: "A1B2C3"
        """
        # Generate 6-digit alphanumeric code (avoiding confusing characters)
        characters = string.ascii_uppercase + string.digits
        # Remove confusing characters: 0, O, I, 1
        characters = characters.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
        return ''.join(secrets.choice(characters) for _ in range(6))

    async def invite_colleague(
        self,
        invitation_data: TeamInvitationCreate,
        inviting_user: User
    ) -> TeamInvitation:
        """
        Send invitation to a new team member.

        Args:
            invitation_data: Invitation details
            inviting_user: User sending the invitation

        Returns:
            Created invitation object

        Raises:
            HTTPException: If user lacks permission or phone already exists

        Example:
            invitation = await team_service.invite_colleague(
                TeamInvitationCreate(
                    phone="+77051234567",
                    name="John Doe",
                    role=UserRole.FLORIST
                ),
                current_user
            )
        """
        # Validate Kazakhstan phone format
        if not AuthService.validate_kazakhstan_phone(invitation_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Kazakhstan phone number format"
            )

        # Normalize phone number
        normalized_phone = AuthService.normalize_phone(invitation_data.phone)

        # Check if user already exists with this phone
        existing_user = await self.auth_service.get_user_by_phone(normalized_phone)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this phone number already exists"
            )

        # Check if there's already a pending invitation for this phone
        statement = select(TeamInvitation).where(
            and_(
                TeamInvitation.phone == normalized_phone,
                TeamInvitation.status == InvitationStatus.PENDING,
                TeamInvitation.expires_at > datetime.utcnow()
            )
        )
        result = await self.session.exec(statement)
        existing_invitation = result.first()

        if existing_invitation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pending invitation already exists for this phone number"
            )

        # Generate unique invitation code
        invitation_code = self.generate_invitation_code()

        # Ensure code is unique (very unlikely collision, but good to check)
        while True:
            statement = select(TeamInvitation).where(
                and_(
                    TeamInvitation.invitation_code == invitation_code,
                    TeamInvitation.status == InvitationStatus.PENDING,
                    TeamInvitation.expires_at > datetime.utcnow()
                )
            )
            result = await self.session.exec(statement)
            if not result.first():
                break
            invitation_code = self.generate_invitation_code()

        # Create invitation (expires in 48 hours)
        invitation = TeamInvitation(
            phone=normalized_phone,
            name=invitation_data.name,
            role=invitation_data.role,
            invited_by=inviting_user.id,
            invitation_code=invitation_code,
            expires_at=datetime.utcnow() + timedelta(hours=48),
            status=InvitationStatus.PENDING
        )

        self.session.add(invitation)
        await self.session.commit()
        await self.session.refresh(invitation)

        return invitation

    async def get_invitation_by_code(self, invitation_code: str) -> Optional[TeamInvitation]:
        """
        Get invitation by invitation code.

        Args:
            invitation_code: 6-digit invitation code

        Returns:
            TeamInvitation object if found and valid, None otherwise

        Example:
            invitation = await team_service.get_invitation_by_code("A1B2C3")
        """
        statement = select(TeamInvitation).where(
            and_(
                TeamInvitation.invitation_code == invitation_code.upper(),
                TeamInvitation.status == InvitationStatus.PENDING,
                TeamInvitation.expires_at > datetime.utcnow()
            )
        )
        result = await self.session.exec(statement)
        return result.first()

    async def accept_invitation(
        self,
        invitation_code: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Accept team invitation and create user account.

        Args:
            invitation_code: 6-digit invitation code
            password: Password for new account

        Returns:
            Dictionary with created user and login tokens

        Raises:
            HTTPException: If invitation invalid or expired

        Example:
            result = await team_service.accept_invitation("A1B2C3", "password123")
            user = result["user"]
            access_token = result["access_token"]
        """
        # Find valid invitation
        invitation = await self.get_invitation_by_code(invitation_code)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid or expired invitation code"
            )

        # Create user account
        user_create = UserCreate(
            name=invitation.name,
            phone=invitation.phone,
            role=invitation.role,
            password=password,
            invited_by=invitation.invited_by
        )

        try:
            user = await self.auth_service.create_user(user_create)
        except HTTPException:
            # Mark invitation as expired if user creation fails
            invitation.status = InvitationStatus.EXPIRED
            await self.session.commit()
            raise

        # Mark invitation as accepted
        invitation.status = InvitationStatus.ACCEPTED
        invitation.updated_at = datetime.utcnow()

        await self.session.commit()

        # Generate login tokens for new user
        from models import LoginRequest
        login_request = LoginRequest(phone=user.phone, password=password)
        login_response = await self.auth_service.login_user(login_request)

        return {
            "user": UserRead.from_orm(user),
            "access_token": login_response.access_token,
            "token_type": login_response.token_type,
            "invitation": TeamInvitationRead.from_orm(invitation)
        }

    async def get_team_members(self, inviting_user_id: Optional[int] = None) -> List[UserRead]:
        """
        Get all team members.

        Args:
            inviting_user_id: Optional filter by who invited them

        Returns:
            List of team members

        Example:
            members = await team_service.get_team_members()
            director_invites = await team_service.get_team_members(director_user_id)
        """
        statement = select(User).where(User.is_active == True)

        if inviting_user_id is not None:
            statement = statement.where(User.invited_by == inviting_user_id)

        result = await self.session.exec(statement)
        users = result.all()

        return [UserRead.from_orm(user) for user in users]

    async def get_invitations_by_user(
        self,
        user_id: int,
        status_filter: Optional[InvitationStatus] = None
    ) -> List[TeamInvitationRead]:
        """
        Get invitations sent by a specific user.

        Args:
            user_id: ID of user who sent invitations
            status_filter: Optional filter by invitation status

        Returns:
            List of invitations

        Example:
            invitations = await team_service.get_invitations_by_user(1)
            pending = await team_service.get_invitations_by_user(1, InvitationStatus.PENDING)
        """
        statement = select(TeamInvitation).where(TeamInvitation.invited_by == user_id)

        if status_filter:
            statement = statement.where(TeamInvitation.status == status_filter)

        statement = statement.order_by(TeamInvitation.created_at.desc())

        result = await self.session.exec(statement)
        invitations = result.all()

        return [TeamInvitationRead.from_orm(invitation) for invitation in invitations]

    async def get_all_invitations(
        self,
        status_filter: Optional[InvitationStatus] = None
    ) -> List[TeamInvitationRead]:
        """
        Get all invitations (admin function).

        Args:
            status_filter: Optional filter by invitation status

        Returns:
            List of all invitations

        Example:
            all_invitations = await team_service.get_all_invitations()
            pending_invitations = await team_service.get_all_invitations(InvitationStatus.PENDING)
        """
        statement = select(TeamInvitation)

        if status_filter:
            statement = statement.where(TeamInvitation.status == status_filter)

        statement = statement.order_by(TeamInvitation.created_at.desc())

        result = await self.session.exec(statement)
        invitations = result.all()

        return [TeamInvitationRead.from_orm(invitation) for invitation in invitations]

    async def cancel_invitation(
        self,
        invitation_id: int,
        canceling_user: User
    ) -> TeamInvitation:
        """
        Cancel a pending invitation.

        Args:
            invitation_id: ID of invitation to cancel
            canceling_user: User canceling the invitation

        Returns:
            Canceled invitation

        Raises:
            HTTPException: If invitation not found or cannot be canceled

        Example:
            canceled = await team_service.cancel_invitation(1, current_user)
        """
        statement = select(TeamInvitation).where(TeamInvitation.id == invitation_id)
        result = await self.session.exec(statement)
        invitation = result.first()

        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )

        # Check if user can cancel this invitation
        if invitation.invited_by != canceling_user.id and canceling_user.role != UserRole.DIRECTOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot cancel invitation sent by another user"
            )

        if invitation.status != InvitationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only cancel pending invitations"
            )

        invitation.status = InvitationStatus.EXPIRED
        invitation.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(invitation)

        return invitation

    async def remove_team_member(
        self,
        user_id: int,
        removing_user: User
    ) -> User:
        """
        Remove (deactivate) a team member.

        Args:
            user_id: ID of user to remove
            removing_user: User performing the removal

        Returns:
            Deactivated user

        Raises:
            HTTPException: If user not found or insufficient permissions

        Example:
            removed_user = await team_service.remove_team_member(2, director)
        """
        statement = select(User).where(User.id == user_id)
        result = await self.session.exec(statement)
        user = result.first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )

        # Prevent self-removal
        if user.id == removing_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove yourself from the team"
            )

        # Only directors can remove other directors
        if user.role == UserRole.DIRECTOR and removing_user.role != UserRole.DIRECTOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only directors can remove other directors"
            )

        return await self.auth_service.deactivate_user(user_id)

    async def update_team_member_role(
        self,
        user_id: int,
        new_role: UserRole,
        updating_user: User
    ) -> User:
        """
        Update team member's role.

        Args:
            user_id: ID of user to update
            new_role: New role to assign
            updating_user: User performing the update

        Returns:
            Updated user

        Raises:
            HTTPException: If user not found or insufficient permissions

        Example:
            updated_user = await team_service.update_team_member_role(
                2, UserRole.MANAGER, director
            )
        """
        statement = select(User).where(User.id == user_id)
        result = await self.session.exec(statement)
        user = result.first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )

        # Prevent self-role change
        if user.id == updating_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role"
            )

        # Only directors can assign director role or modify other directors
        if (new_role == UserRole.DIRECTOR or user.role == UserRole.DIRECTOR) and updating_user.role != UserRole.DIRECTOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only directors can assign or modify director roles"
            )

        user.role = new_role
        user.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def cleanup_expired_invitations(self) -> int:
        """
        Clean up expired invitations (background task).

        Returns:
            Number of cleaned up invitations

        Example:
            cleaned = await team_service.cleanup_expired_invitations()
        """
        statement = select(TeamInvitation).where(
            and_(
                TeamInvitation.status == InvitationStatus.PENDING,
                TeamInvitation.expires_at <= datetime.utcnow()
            )
        )
        result = await self.session.exec(statement)
        expired_invitations = result.all()

        count = 0
        for invitation in expired_invitations:
            invitation.status = InvitationStatus.EXPIRED
            invitation.updated_at = datetime.utcnow()
            count += 1

        if count > 0:
            await self.session.commit()

        return count


# Dependency injection
async def get_team_service(
    session: Session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service)
) -> TeamService:
    """
    Dependency to get TeamService instance.

    Returns:
        Configured TeamService instance

    Usage:
        @app.post("/invite-colleague")
        async def invite_colleague(
            invitation: TeamInvitationCreate,
            team_service: TeamService = Depends(get_team_service),
            current_user: User = Depends(get_current_user)
        ):
    """
    return TeamService(session, auth_service)