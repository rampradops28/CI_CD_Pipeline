from fastapi import HTTPException, status

from app.models.user import User, UserCreate
from app.repositories.user_repository import UserRepository


class UserService:
    """Business logic service for managing users."""

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def create_user(self, user_in: UserCreate) -> User:
        """Create user with business validation: email uniqueness."""
        existing_user = self.repository.get_by_email(user_in.email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{user_in.email}' is already registered.",
            )

        return self.repository.create(
            email=user_in.email,
            full_name=user_in.full_name,
        )

    def get_user_by_id(self, user_id: int) -> User:
        """Retrieve user by ID or raise 404 NOT FOUND."""
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found.",
            )
        return user
