from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base import Base
from app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
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
        yield test_client
    app.dependency_overrides.clear()


def token(client: TestClient, email: str) -> str:
    password = "correct-horse-battery-staple"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def test_user_manages_only_own_watches(client: TestClient) -> None:
    first_token = token(client, "first@example.com")
    second_token = token(client, "second@example.com")
    headers = {"Authorization": f"Bearer {first_token}"}
    create_response = client.post(
        "/api/v1/watches",
        headers=headers,
        json={
            "product_name": "Keyboard",
            "product_url": "https://shop.example.com/keyboard",
            "target_price": "99.99",
            "currency": "USD",
        },
    )
    assert create_response.status_code == 201
    watch_id = create_response.json()["id"]

    list_response = client.get("/api/v1/watches", headers=headers)
    assert list_response.json()["total"] == 1
    assert list_response.json()["items"][0]["product"]["name"] == "Keyboard"

    foreign_response = client.get(
        f"/api/v1/watches/{watch_id}", headers={"Authorization": f"Bearer {second_token}"}
    )
    assert foreign_response.status_code == 404

    update_response = client.patch(
        f"/api/v1/watches/{watch_id}",
        headers=headers,
        json={"target_price": "89.99", "is_active": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["target_price"] == "89.99"
    assert update_response.json()["is_active"] is False

    delete_response = client.delete(f"/api/v1/watches/{watch_id}", headers=headers)
    assert delete_response.status_code == 204
    assert client.get("/api/v1/watches", headers=headers).json()["total"] == 0


def test_watch_rejects_invalid_currency(client: TestClient) -> None:
    headers = {"Authorization": f"Bearer {token(client, 'user@example.com')}"}

    response = client.post(
        "/api/v1/watches",
        headers=headers,
        json={
            "product_name": "Keyboard",
            "product_url": "https://shop.example.com/keyboard",
            "target_price": "99.99",
            "currency": "usd",
        },
    )

    assert response.status_code == 422
