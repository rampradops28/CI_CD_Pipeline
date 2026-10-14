from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


# ==============================================================================
# SQLAlchemy ORM Model
# ==============================================================================
class User(Base):
    """User entity mapped to users table."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )


# ==============================================================================
# Pydantic Schemas (DTOs)
# ==============================================================================
class UserBase(BaseModel):
    """Shared user attributes."""

    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """Payload required to create a new user."""

    pass


class UserResponse(UserBase):
    """Response schema representing a persisted user."""

    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
