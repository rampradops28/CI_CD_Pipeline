import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository


@pytest.mark.integration
class TestUserRepository:
    """Integration tests for UserRepository verifying actual database interactions."""

    def test_create_user_persists_in_database(self, db_session: Session) -> None:
        """Test creating a user persists the entity and generates a valid primary key ID."""
        # Arrange
        repo = UserRepository(db_session)
        email = "bob.marley@example.com"
        full_name = "Bob Marley"

        # Act
        created_user = repo.create(email=email, full_name=full_name)

        # Assert
        assert created_user.id is not None
        assert created_user.id > 0
        assert created_user.email == email
        assert created_user.full_name == full_name
        assert created_user.is_active is True
        assert created_user.created_at is not None

        # Verify entity exists by direct query
        queried_user = db_session.get(User, created_user.id)
        assert queried_user is not None
        assert queried_user.email == email

    def test_get_by_id(self, db_session: Session) -> None:
        """Test retrieving a persisted user by ID."""
        repo = UserRepository(db_session)
        user = repo.create(email="carol@example.com", full_name="Carol Danvers")

        retrieved = repo.get_by_id(user.id)
        assert retrieved is not None
        assert retrieved.id == user.id
        assert retrieved.email == "carol@example.com"

    def test_get_by_id_returns_none_for_missing_id(self, db_session: Session) -> None:
        """Test get_by_id returns None when user does not exist in database."""
        repo = UserRepository(db_session)
        retrieved = repo.get_by_id(99999)
        assert retrieved is None

    def test_get_by_email(self, db_session: Session) -> None:
        """Test retrieving a persisted user by unique email address."""
        repo = UserRepository(db_session)
        repo.create(email="david@example.com", full_name="David Bowie")

        retrieved = repo.get_by_email("david@example.com")
        assert retrieved is not None
        assert retrieved.full_name == "David Bowie"

    def test_duplicate_email_violates_integrity_constraint(
        self, db_session: Session
    ) -> None:
        """Test database enforces unique email constraint, raising IntegrityError on duplicates."""
        repo = UserRepository(db_session)
        repo.create(email="unique.target@example.com", full_name="First User")

        with pytest.raises(IntegrityError):
            repo.create(email="unique.target@example.com", full_name="Duplicate User")
        db_session.rollback()

    def test_list_users_pagination(self, db_session: Session) -> None:
        """Test list_users retrieves records adhering to pagination bounds."""
        repo = UserRepository(db_session)
        for i in range(5):
            repo.create(email=f"user{i}@example.com", full_name=f"User {i}")

        page_1 = repo.list_users(skip=0, limit=2)
        assert len(page_1) == 2

        page_2 = repo.list_users(skip=2, limit=2)
        assert len(page_2) == 2
        assert page_1[0].id != page_2[0].id
