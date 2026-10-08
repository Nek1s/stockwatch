from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base import Base
from app.main import app
from app.models.price_snapshot import PriceSnapshot


@pytest.fixture
def client_and_session() -> Generator[tuple[TestClient, sessionmaker[Session]], None, None]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_db() -> Generator[Session, None, None]:
        with test_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client, test_session
    app.dependency_overrides.clear()


def create_watch(client: TestClient, access_token: str) -> str:
    response = client.post(
        "/api/v1/watches",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "product_name": "Coffee",
            "product_url": "https://shop.example.com/coffee",
            "target_price": "500.00",
            "currency": "RUB",
        },
    )
    return response.json()["id"]


def test_price_history_and_statistics(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, test_session = client_and_session
    password = "correct-horse-battery-staple"
    client.post(
        "/api/v1/auth/register", json={"email": "history@example.com", "password": password}
    )
    access_token = client.post(
        "/api/v1/auth/login", json={"email": "history@example.com", "password": password}
    ).json()["access_token"]
    watch_id = create_watch(client, access_token)

    with test_session() as session:
        session.add_all(
            [
                PriceSnapshot(
                    watch_id=UUID(watch_id),
                    price=Decimal("450.00"),
                    captured_at=datetime.now(UTC) - timedelta(hours=1),
                ),
                PriceSnapshot(
                    watch_id=UUID(watch_id), price=Decimal("400.00"), captured_at=datetime.now(UTC)
                ),
            ]
        )
        session.commit()

    history = client.get(
        f"/api/v1/watches/{watch_id}/prices", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert history.status_code == 200
    assert history.json()["total"] == 2
    assert history.json()["items"][0]["price"] == "400.00"
    statistics = client.get(
        f"/api/v1/watches/{watch_id}/prices/statistics",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert statistics.json() == {
        "latest_price": "400.00",
        "min_price": "400.00",
        "max_price": "450.00",
    }
