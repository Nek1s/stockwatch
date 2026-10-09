from decimal import Decimal
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product
from app.models.user import User
from app.models.watch import PriceWatch
from app.services.price_source import PriceResult, TemporaryPriceSourceError
from app.worker import process_watch_price


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

    process_watch_price(str(watch.id), session, FixedPriceSource())

    snapshot = session.scalar(select(PriceSnapshot).where(PriceSnapshot.watch_id == watch.id))
    assert snapshot is not None
    assert snapshot.price == Decimal("123.45")


def test_worker_propagates_temporary_source_error() -> None:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session: Session = sessionmaker(bind=engine)()

    try:
        process_watch_price(str(uuid4()), session, FailingPriceSource())
    except TemporaryPriceSourceError:
        raise AssertionError("Inactive or missing watch must not call source")
