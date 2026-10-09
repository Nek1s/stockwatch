import json
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class TemporaryNotificationError(Exception):
    """A delivery failure that Celery may retry."""


class Notifier(Protocol):
    def send_price_alert(
        self, chat_id: str, product_name: str, price: str, currency: str
    ) -> None: ...


class TelegramNotifier:
    """Small synchronous Telegram Bot API adapter used from Celery workers."""

    def __init__(self, bot_token: str) -> None:
        self._url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def send_price_alert(self, chat_id: str, product_name: str, price: str, currency: str) -> None:
        payload = json.dumps(
            {
                "chat_id": chat_id,
                "text": f"StockWatch: {product_name} теперь стоит {price} {currency}.",
            }
        ).encode()
        request = Request(self._url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=10) as response:  # noqa: S310
                if response.status >= 500:
                    raise TemporaryNotificationError("Telegram is temporarily unavailable")
        except (HTTPError, URLError, TimeoutError) as error:
            raise TemporaryNotificationError("Telegram delivery failed") from error
