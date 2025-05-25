"""Making the models for inventory in db

Revision ID: 59d23d31932d
Revises: 20250524_create_products_and_categories
Create Date: 2025-05-25 14:32:15.116389

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "59d23d31932d"
down_revision: Union[str, None] = "20250524_create_products_and_categories"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inventory_items",
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            nullable=False,
            index=True,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
    )
    op.create_table(
        "inventory_updates",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("inventory_items.product_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_index("ix_inventory_updates_created_at", "inventory_updates", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_inventory_updates_created_at", table_name="inventory_updates")
    op.drop_table("inventory_updates")
    op.drop_table("inventory_items")
