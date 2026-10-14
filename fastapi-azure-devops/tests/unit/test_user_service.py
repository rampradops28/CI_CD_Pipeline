from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status

from app.models.user import User, UserCreate
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


@pytest.mark.unit
class TestUserService:
    """Isolated unit tests for UserService business logic using mocked UserRepository."""

    def test_create_user_success(self) -> None:
        """Test successful user creation when email is available."""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.get_by_email.return_value = None  # Email not taken

        expected_user = User(
            id=10,
            email="alice@example.com",
            full_name="Alice Wonderland",
            is_active=True,
        )
        mock_repo.create.return_value = expected_user

        service = UserService(repository=mock_repo)
        user_in = UserCreate(email="alice@example.com", full_name="Alice Wonderland")

        # Act
        created_user = service.create_user(user_in)

        # Assert
        assert created_user.id == 10
        assert created_user.email == "alice@example.com"
        assert created_user.full_name == "Alice Wonderland"
        mock_repo.get_by_email.assert_called_once_with("alice@example.com")
        mock_repo.create.assert_called_once_with(
            email="alice@example.com", full_name="Alice Wonderland"
        )

    def test_create_user_duplicate_email_raises_400(self, sample_user: User) -> None:
        """Test creating a user with already registered email raises HTTPException 400."""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.get_by_email.return_value = sample_user  # Email already exists!

        service = UserService(repository=mock_repo)
        user_in = UserCreate(email=sample_user.email, full_name="Another Name")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_user(user_in)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in exc_info.value.detail
        mock_repo.create.assert_not_called()

    def test_get_user_by_id_success(self, sample_user: User) -> None:
        """Test retrieving an existing user by primary ID."""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.get_by_id.return_value = sample_user

        service = UserService(repository=mock_repo)

        # Act
        user = service.get_user_by_id(user_id=1)

        # Assert
        assert user.id == 1
        assert user.email == sample_user.email
        mock_repo.get_by_id.assert_called_once_with(1)

    def test_get_user_by_id_not_found_raises_404(self) -> None:
        """Test retrieving a non-existent user ID raises HTTPException 404."""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.get_by_id.return_value = None  # User does not exist

        service = UserService(repository=mock_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_user_by_id(user_id=999)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc_info.value.detail
        mock_repo.get_by_id.assert_called_once_with(999)
