from decimal import Decimal
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class WatchCreate(BaseModel):
    product_name: str = Field(min_length=1, max_length=255)
    product_url: AnyHttpUrl
    target_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")


class WatchUpdate(BaseModel):
    product_name: str | None = Field(default=None, min_length=1, max_length=255)
    product_url: AnyHttpUrl | None = None
    target_price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    currency: str | None = Field(default=None, min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    is_active: bool | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    url: str


class WatchResponse(BaseModel):
    id: UUID
    product: ProductResponse
    target_price: Decimal
    currency: str
    is_active: bool


class WatchPage(BaseModel):
    items: list[WatchResponse]
    total: int
    limit: int
    offset: int
