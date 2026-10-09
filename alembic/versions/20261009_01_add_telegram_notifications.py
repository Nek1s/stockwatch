"""Add Telegram settings and notification event log."""

import sqlalchemy as sa

from alembic import op

revision = "20261009_01"
down_revision = "20261008_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("telegram_chat_id", sa.String(length=32), nullable=True))
    op.create_table(
        "notification_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "watch_id",
            sa.Uuid(),
            sa.ForeignKey("price_watches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "price_snapshot_id",
            sa.Uuid(),
            sa.ForeignKey("price_snapshots.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("channel", sa.String(length=32), nullable=False, server_default="telegram"),
        sa.Column(
            "sent_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table("notification_events")
    op.drop_column("users", "telegram_chat_id")
