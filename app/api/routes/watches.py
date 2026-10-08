from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.models.product import Product
from app.models.watch import PriceWatch
from app.schemas.watch import ProductResponse, WatchCreate, WatchPage, WatchResponse, WatchUpdate

router = APIRouter(prefix="/api/v1/watches", tags=["price watches"])


def to_response(watch: PriceWatch, product: Product) -> WatchResponse:
    return WatchResponse(
        id=watch.id,
        product=ProductResponse.model_validate(product),
        target_price=watch.target_price,
        currency=watch.currency,
        is_active=watch.is_active,
    )


def get_owned_watch(watch_id: UUID, user_id: UUID, db: DbSession) -> tuple[PriceWatch, Product]:
    row = db.execute(
        select(PriceWatch, Product)
        .join(Product, Product.id == PriceWatch.product_id)
        .where(PriceWatch.id == watch_id, PriceWatch.user_id == user_id)
    ).one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watch not found")
    return row


@router.post("", response_model=WatchResponse, status_code=status.HTTP_201_CREATED)
def create_watch(payload: WatchCreate, current_user: CurrentUser, db: DbSession) -> WatchResponse:
    product = Product(
        user_id=current_user.id,
        name=payload.product_name,
        url=str(payload.product_url),
    )
    db.add(product)
    db.flush()
    watch = PriceWatch(
        user_id=current_user.id,
        product_id=product.id,
        target_price=payload.target_price,
        currency=payload.currency,
    )
    db.add(watch)
    db.commit()
    db.refresh(watch)
    return to_response(watch, product)


@router.get("", response_model=WatchPage)
def list_watches(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    is_active: bool | None = None,
) -> WatchPage:
    filters = [PriceWatch.user_id == current_user.id]
    if is_active is not None:
        filters.append(PriceWatch.is_active == is_active)
    rows = db.execute(
        select(PriceWatch, Product)
        .join(Product, Product.id == PriceWatch.product_id)
        .where(*filters)
        .order_by(PriceWatch.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    total = db.scalar(select(func.count()).select_from(PriceWatch).where(*filters)) or 0
    return WatchPage(
        items=[to_response(watch, product) for watch, product in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{watch_id}", response_model=WatchResponse)
def get_watch(watch_id: UUID, current_user: CurrentUser, db: DbSession) -> WatchResponse:
    watch, product = get_owned_watch(watch_id, current_user.id, db)
    return to_response(watch, product)


@router.patch("/{watch_id}", response_model=WatchResponse)
def update_watch(
    watch_id: UUID, payload: WatchUpdate, current_user: CurrentUser, db: DbSession
) -> WatchResponse:
    watch, product = get_owned_watch(watch_id, current_user.id, db)
    changes = payload.model_dump(exclude_unset=True)
    if "product_name" in changes:
        product.name = changes.pop("product_name")
    if "product_url" in changes:
        product.url = str(changes.pop("product_url"))
    for field, value in changes.items():
        setattr(watch, field, value)
    db.commit()
    db.refresh(watch)
    return to_response(watch, product)


@router.delete("/{watch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watch(watch_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    watch, product = get_owned_watch(watch_id, current_user.id, db)
    db.delete(watch)
    db.delete(product)
    db.commit()
