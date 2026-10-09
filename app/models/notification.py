from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NotificationEvent(Base):
    """A notification emitted for a single threshold-crossing price snapshot."""

    __tablename__ = "notification_events"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    watch_id: Mapped[UUID] = mapped_column(ForeignKey("price_watches.id", ondelete="CASCADE"))
    price_snapshot_id: Mapped[UUID] = mapped_column(
        ForeignKey("price_snapshots.id", ondelete="CASCADE"), unique=True
    )
    channel: Mapped[str] = mapped_column(String(32), default="telegram")
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
