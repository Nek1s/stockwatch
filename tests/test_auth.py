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
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
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
    Base.metadata.drop_all(engine)


def register(client: TestClient, email: str = "user@example.com") -> dict[str, object]:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correct-horse-battery-staple"},
    )
    assert response.status_code == 201
    return response.json()


def test_register_creates_user_without_password_hash(client: TestClient) -> None:
    payload = register(client)

    assert payload["email"] == "user@example.com"
    assert payload["is_active"] is True
    assert "password_hash" not in payload


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    register(client)

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "correct-horse-battery-staple"},
    )

    assert response.status_code == 409


def test_login_refresh_and_current_user(client: TestClient) -> None:
    register(client)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "correct-horse-battery-staple"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.com"

    refresh_response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["access_token"] != tokens["access_token"]


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    register(client)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "incorrect-password"},
    )

    assert response.status_code == 401


def test_me_rejects_refresh_token(client: TestClient) -> None:
    register(client)
    tokens = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "correct-horse-battery-staple"},
    ).json()

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )

    assert response.status_code == 401


def test_user_can_configure_telegram_chat(client: TestClient) -> None:
    register(client)
    tokens = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "correct-horse-battery-staple"},
    ).json()

    response = client.put(
        "/api/v1/notifications/telegram",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"telegram_chat_id": "123456789"},
    )

    assert response.status_code == 200
    assert response.json()["telegram_chat_id"] == "123456789"
