from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PriceSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    price: Decimal
    is_available: bool
    captured_at: datetime


class PriceHistoryPage(BaseModel):
    items: list[PriceSnapshotResponse]
    total: int
    limit: int
    offset: int


class PriceStatistics(BaseModel):
    latest_price: Decimal | None
    min_price: Decimal | None
    max_price: Decimal | None
