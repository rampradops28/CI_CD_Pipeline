from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connection import get_db
from app.models.user import UserCreate, UserResponse
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Factory dependency constructing UserService with UserRepository."""
    repository = UserRepository(db)
    return UserService(repository)


@router.get("/health", status_code=status.HTTP_200_OK, tags=["Monitoring"])
def health_check() -> dict[str, str]:
    """Health check probe endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.app_env,
    }


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
def create_user(
    user_in: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Create a new user with validation."""
    user = service.create_user(user_in)
    return UserResponse.model_validate(user)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    tags=["Users"],
)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Retrieve an existing user by primary ID."""
    user = service.get_user_by_id(user_id)
    return UserResponse.model_validate(user)
