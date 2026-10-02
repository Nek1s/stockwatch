from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    service: str


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Проверить доступность сервиса",
)
async def healthcheck() -> HealthResponse:
    """Return a lightweight liveness probe without contacting dependencies."""
    return HealthResponse(status="ok", service="stockwatch")
