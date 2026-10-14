from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Handles database operations for User entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        """Retrieve a single user by primary key ID."""
        stmt = select(User).where(User.id == user_id)
        return self.db.scalars(stmt).first()

    def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by unique email address."""
        stmt = select(User).where(User.email == email)
        return self.db.scalars(stmt).first()

    def list_users(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """List users with pagination support."""
        stmt = select(User).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def create(self, email: str, full_name: str) -> User:
        """Persist a new user into the database."""
        user = User(email=email, full_name=full_name, is_active=True)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
