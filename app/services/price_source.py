from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


class TemporaryPriceSourceError(Exception):
    """A transient source failure suitable for a retry."""


@dataclass(frozen=True)
class PriceResult:
    price: Decimal
    is_available: bool = True


class PriceSource(Protocol):
    def fetch_price(self, url: str) -> PriceResult: ...


class UnsupportedPriceSource:
    """Safe default until an approved provider is configured."""

    def fetch_price(self, url: str) -> PriceResult:
        raise TemporaryPriceSourceError(f"No price source configured for {url}")
