from typing import Any
from uuid import UUID

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
    beat_schedule={
        "enqueue-active-price-checks": {
            "task": "app.worker.enqueue_active_watch_checks",
            "schedule": 300.0,
        }
    },
)


@celery_app.task(  # type: ignore[untyped-decorator]
    bind=True, autoretry_for=(TemporaryPriceSourceError,), retry_backoff=True, max_retries=3
)
def check_watch_price(self: Any, watch_id: str) -> None:
    """Fetch one approved source and persist an immutable price snapshot."""
    with SessionLocal() as session:
        process_watch_price(UUID(watch_id), session, UnsupportedPriceSource())


@celery_app.task  # type: ignore[untyped-decorator]
def enqueue_active_watch_checks() -> int:
    """Queue one price-check task per active watch for Celery Beat."""
    with SessionLocal() as session:
        watch_ids = session.scalars(
            select(PriceWatch.id).where(PriceWatch.is_active.is_(True))
        ).all()

    for watch_id in watch_ids:
        check_watch_price.delay(str(watch_id))
    return len(watch_ids)


def process_watch_price(watch_id: UUID, session: Session, source: PriceSource) -> None:
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
