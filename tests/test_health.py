from fastapi.testclient import TestClient

from app.main import app


def test_healthcheck_returns_service_status() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "stockwatch"}


def test_metrics_exposes_stockwatch_counters() -> None:
    client = TestClient(app)
    client.get("/health")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "stockwatch_http_requests_total" in response.text
    assert "stockwatch_price_checks_total" in response.text
