from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product
from app.models.user import User
from app.models.watch import PriceWatch
from app.services.price_source import PriceResult, TemporaryPriceSourceError
from app.worker import enqueue_active_watch_checks, process_watch_price


class FixedPriceSource:
    def fetch_price(self, url: str) -> PriceResult:
        assert url == "https://example.com/product"
        return PriceResult(price=Decimal("123.45"))


class FailingPriceSource:
    def fetch_price(self, url: str) -> PriceResult:
        raise TemporaryPriceSourceError("temporary failure")


def test_worker_persists_price_snapshot() -> None:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    user = User(id=uuid4(), email="worker@example.com", password_hash="hash")
    product = Product(
        id=uuid4(), user_id=user.id, name="Product", url="https://example.com/product"
    )
    watch = PriceWatch(
        id=uuid4(),
        user_id=user.id,
        product_id=product.id,
        target_price=Decimal("100"),
        currency="RUB",
    )
    session.add_all([user, product, watch])
    session.commit()

    process_watch_price(watch.id, session, FixedPriceSource())

    snapshot = session.scalar(select(PriceSnapshot).where(PriceSnapshot.watch_id == watch.id))
    assert snapshot is not None
    assert snapshot.price == Decimal("123.45")


def test_worker_skips_missing_watch() -> None:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session: Session = sessionmaker(bind=engine)()

    process_watch_price(uuid4(), session, FailingPriceSource())


def test_worker_propagates_temporary_source_error() -> None:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session: Session = sessionmaker(bind=engine)()
    user = User(id=uuid4(), email="retry@example.com", password_hash="hash")
    product = Product(
        id=uuid4(), user_id=user.id, name="Product", url="https://example.com/product"
    )
    watch = PriceWatch(
        id=uuid4(),
        user_id=user.id,
        product_id=product.id,
        target_price=Decimal("100"),
        currency="RUB",
    )
    session.add_all([user, product, watch])
    session.commit()

    with pytest.raises(TemporaryPriceSourceError):
        process_watch_price(watch.id, session, FailingPriceSource())


def test_scheduler_enqueues_only_active_watches(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session: Session = sessionmaker(bind=engine)()
    user = User(id=uuid4(), email="beat@example.com", password_hash="hash")
    product = Product(id=uuid4(), user_id=user.id, name="Active", url="https://example.com/active")
    active_watch = PriceWatch(
        id=uuid4(),
        user_id=user.id,
        product_id=product.id,
        target_price=Decimal("100"),
        currency="RUB",
    )
    session.add_all([user, product, active_watch])
    session.commit()
    active_watch_id = str(active_watch.id)
    queued: list[str] = []

    monkeypatch.setattr("app.worker.SessionLocal", lambda: session)
    monkeypatch.setattr("app.worker.check_watch_price.delay", queued.append)

    assert enqueue_active_watch_checks.run() == 1
    assert queued == [active_watch_id]
