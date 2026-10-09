from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.api.routes.watches import get_owned_watch
from app.models.price_snapshot import PriceSnapshot
from app.schemas.price_history import PriceHistoryPage, PriceSnapshotResponse, PriceStatistics

router = APIRouter(prefix="/api/v1/watches/{watch_id}/prices", tags=["price history"])


@router.get("", response_model=PriceHistoryPage)
def list_price_history(
    watch_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PriceHistoryPage:
    watch, _ = get_owned_watch(watch_id, current_user.id, db)
    items = db.scalars(
        select(PriceSnapshot)
        .where(PriceSnapshot.watch_id == watch.id)
        .order_by(PriceSnapshot.captured_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    total = (
        db.scalar(
            select(func.count())
            .select_from(PriceSnapshot)
            .where(PriceSnapshot.watch_id == watch.id)
        )
        or 0
    )
    return PriceHistoryPage(
        items=[PriceSnapshotResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/statistics", response_model=PriceStatistics)
def get_price_statistics(
    watch_id: UUID, current_user: CurrentUser, db: DbSession
) -> PriceStatistics:
    watch, _ = get_owned_watch(watch_id, current_user.id, db)
    latest = db.scalar(
        select(PriceSnapshot.price)
        .where(PriceSnapshot.watch_id == watch.id)
        .order_by(PriceSnapshot.captured_at.desc())
        .limit(1)
    )
    min_price, max_price = db.execute(
        select(func.min(PriceSnapshot.price), func.max(PriceSnapshot.price)).where(
            PriceSnapshot.watch_id == watch.id
        )
    ).one()
    return PriceStatistics(latest_price=latest, min_price=min_price, max_price=max_price)
