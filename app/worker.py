from decimal import Decimal
from time import perf_counter
from typing import Any
from uuid import UUID

from celery import Celery
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.notification import NotificationEvent
from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product
from app.models.user import User
from app.models.watch import PriceWatch
from app.observability.metrics import PRICE_CHECK_DURATION, PRICE_CHECKS, PRICE_SNAPSHOTS
from app.services.notifier import Notifier, TelegramNotifier, TemporaryNotificationError
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
    bind=True,
    autoretry_for=(TemporaryPriceSourceError, TemporaryNotificationError),
    retry_backoff=True,
    max_retries=3,
)
def check_watch_price(self: Any, watch_id: str) -> None:
    """Fetch one approved source and persist an immutable price snapshot."""
    started_at = perf_counter()
    outcome = "success"
    try:
        with SessionLocal() as session:
            notifier = (
                TelegramNotifier(settings.telegram_bot_token)
                if settings.telegram_bot_token
                else None
            )
            process_watch_price(UUID(watch_id), session, UnsupportedPriceSource(), notifier)
    except Exception:
        outcome = "error"
        raise
    finally:
        PRICE_CHECKS.labels(outcome=outcome).inc()
        PRICE_CHECK_DURATION.observe(perf_counter() - started_at)


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


def process_watch_price(
    watch_id: UUID, session: Session, source: PriceSource, notifier: Notifier | None = None
) -> None:
    """Persist one source result; callers choose retry policy."""
    row = session.execute(
        select(PriceWatch, Product, User)
        .join(Product, Product.id == PriceWatch.product_id)
        .join(User, User.id == PriceWatch.user_id)
        .where(PriceWatch.id == watch_id, PriceWatch.is_active.is_(True))
    ).one_or_none()
    if row is None:
        return
    watch, product, user = row
    result = source.fetch_price(product.url)
    previous_snapshot = session.scalar(
        select(PriceSnapshot)
        .where(PriceSnapshot.watch_id == watch.id)
        .order_by(PriceSnapshot.captured_at.desc())
        .limit(1)
    )
    snapshot = PriceSnapshot(
        watch_id=watch.id, price=result.price, is_available=result.is_available
    )
    session.add(snapshot)
    session.flush()
    if _should_notify(watch, user, result.price, result.is_available, previous_snapshot, notifier):
        assert notifier is not None
        assert user.telegram_chat_id is not None
        notifier.send_price_alert(
            user.telegram_chat_id, product.name, str(result.price), watch.currency
        )
        session.add(NotificationEvent(watch_id=watch.id, price_snapshot_id=snapshot.id))
    session.commit()
    PRICE_SNAPSHOTS.inc()


def _should_notify(
    watch: PriceWatch,
    user: User,
    price: Decimal,
    is_available: bool,
    previous_snapshot: PriceSnapshot | None,
    notifier: Notifier | None,
) -> bool:
    """Send one alert when a price crosses the user's target from above."""
    if notifier is None or user.telegram_chat_id is None or not is_available:
        return False
    if price > watch.target_price:
        return False
    return previous_snapshot is None or (
        not previous_snapshot.is_available or previous_snapshot.price > watch.target_price
    )
