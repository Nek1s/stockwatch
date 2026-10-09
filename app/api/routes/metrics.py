from fastapi import APIRouter, Response

from app.observability.metrics import metrics_response

router = APIRouter(tags=["observability"])


@router.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    """Expose Prometheus metrics without requiring application authentication."""
    payload, content_type = metrics_response()
    return Response(content=payload, media_type=content_type)
