from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.price_history import router as price_history_router
from app.api.routes.watches import router as watches_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Build the ASGI application without performing external I/O."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="API-сервис мониторинга цен товаров.",
        debug=settings.debug,
    )
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(watches_router)
    app.include_router(price_history_router)
    app.include_router(notifications_router)
    return app


app = create_app()
