"""Create price snapshots."""

import sqlalchemy as sa

from alembic import op

revision = "20261008_02"
down_revision = "20261008_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "price_snapshots",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "watch_id",
            sa.Uuid(),
            sa.ForeignKey("price_watches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("is_available", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "captured_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_price_snapshots_watch_id", "price_snapshots", ["watch_id"])


def downgrade() -> None:
    op.drop_index("ix_price_snapshots_watch_id", table_name="price_snapshots")
    op.drop_table("price_snapshots")
