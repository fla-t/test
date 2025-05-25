"""Making the models for sales in db

Revision ID: d51666f213fe
Revises: 59d23d31932d
Create Date: 2025-05-25 16:51:05.426062

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d51666f213fe"
down_revision: Union[str, None] = "59d23d31932d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "sales",
        sa.Column(
            "id", postgresql.UUID(as_uuid=False), primary_key=True, nullable=False, index=True
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("total_price", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, index=True),
    )


def downgrade():
    op.drop_index("ix_sales_created_at", table_name="sales")
    op.drop_index("ix_sales_product_id", table_name="sales")
    op.drop_table("sales")
