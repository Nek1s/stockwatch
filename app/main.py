from time import perf_counter

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import RequestResponseEndpoint

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.price_history import router as price_history_router
from app.api.routes.watches import router as watches_router
from app.core.config import get_settings
from app.observability.metrics import HTTP_REQUEST_DURATION, HTTP_REQUESTS


def create_app() -> FastAPI:
    """Build the ASGI application without performing external I/O."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="API-сервис мониторинга цен товаров.",
        debug=settings.debug,
    )

    @app.middleware("http")
    async def collect_http_metrics(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        started_at = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            path = _route_path(request)
            HTTP_REQUESTS.labels(method=request.method, path=path, status="500").inc()
            HTTP_REQUEST_DURATION.labels(method=request.method, path=path).observe(
                perf_counter() - started_at
            )
            raise
        path = _route_path(request)
        HTTP_REQUESTS.labels(
            method=request.method, path=path, status=str(response.status_code)
        ).inc()
        HTTP_REQUEST_DURATION.labels(method=request.method, path=path).observe(
            perf_counter() - started_at
        )
        return response

    app.include_router(health_router)
    app.include_router(metrics_router)
    app.include_router(auth_router)
    app.include_router(watches_router)
    app.include_router(price_history_router)
    app.include_router(notifications_router)
    return app


def _route_path(request: Request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", "unmatched")


app = create_app()
