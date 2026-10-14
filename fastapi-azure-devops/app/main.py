from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings


def create_application() -> FastAPI:
    """Application factory building configured FastAPI instance."""
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Register API routers
    app.include_router(router)

    return app


app = create_application()
