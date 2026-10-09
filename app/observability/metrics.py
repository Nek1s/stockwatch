import os

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    Counter,
    Histogram,
    multiprocess,
)
from prometheus_client import generate_latest as generate_prometheus_metrics

HTTP_REQUESTS = Counter(
    "stockwatch_http_requests_total",
    "Total HTTP requests handled by StockWatch.",
    ("method", "path", "status"),
)
HTTP_REQUEST_DURATION = Histogram(
    "stockwatch_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ("method", "path"),
)
PRICE_CHECKS = Counter(
    "stockwatch_price_checks_total",
    "Total price-check task executions.",
    ("outcome",),
)
PRICE_CHECK_DURATION = Histogram(
    "stockwatch_price_check_duration_seconds",
    "Price-check task duration in seconds.",
)
PRICE_SNAPSHOTS = Counter(
    "stockwatch_price_snapshots_total",
    "Total persisted price snapshots.",
)


def metrics_response() -> tuple[bytes, str]:
    """Render metrics, aggregating processes when Docker multiprocess mode is enabled."""
    if os.getenv("PROMETHEUS_MULTIPROC_DIR"):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)  # type: ignore[no-untyped-call]
        return generate_prometheus_metrics(registry), CONTENT_TYPE_LATEST
    return generate_prometheus_metrics(REGISTRY), CONTENT_TYPE_LATEST
