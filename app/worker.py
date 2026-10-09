from typing import Any

from celery import Celery
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product
from app.models.watch import PriceWatch
from app.services.price_source import PriceSource, TemporaryPriceSourceError, UnsupportedPriceSource

settings = get_settings()

celery_app = Celery("stockwatch", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_default_queue="stockwatch",
    task_track_started=True,
    timezone="UTC",
)


@celery_app.task(  # type: ignore[untyped-decorator]
    bind=True, autoretry_for=(TemporaryPriceSourceError,), retry_backoff=True, max_retries=3
)
def check_watch_price(self: Any, watch_id: str) -> None:
    """Fetch one approved source and persist an immutable price snapshot."""
    with SessionLocal() as session:
        process_watch_price(watch_id, session, UnsupportedPriceSource())


def process_watch_price(watch_id: str, session: Session, source: PriceSource) -> None:
    """Persist one source result; callers choose retry policy."""
    row = session.execute(
        select(PriceWatch, Product)
        .join(Product, Product.id == PriceWatch.product_id)
        .where(PriceWatch.id == watch_id, PriceWatch.is_active.is_(True))
    ).one_or_none()
    if row is None:
        return
    watch, product = row
    result = source.fetch_price(product.url)
    session.add(
        PriceSnapshot(watch_id=watch.id, price=result.price, is_available=result.is_available)
    )
    session.commit()
