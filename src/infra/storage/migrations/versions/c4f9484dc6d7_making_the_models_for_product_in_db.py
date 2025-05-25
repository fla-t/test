"""Making the models for product in db

Revision ID: c4f9484dc6d7
Revises:
Create Date: 2025-05-25 14:03:44.387292

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4f9484dc6d7"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# src/infra/storage/migrations/versions/20250524_create_products_and_categories.py
"""create product_categories and products tables (updated)

Revision ID: 20250524_create_products_and_categories
Revises:
Create Date: 2025-05-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20250524_create_products_and_categories"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "alembic_version",
        "version_num",
        type_=sa.String(length=128),
        existing_type=sa.String(length=32),
        existing_nullable=False,
    )

    op.create_table(
        "product_categories",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
    )

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("product_categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Float(), nullable=False),
    )
    # Explicit indexes
    op.create_index("ix_products_category_id", "products", ["category_id"])


def downgrade() -> None:
    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_index("ix_products_id", table_name="products")

    op.drop_table("products")
    op.drop_table("product_categories")
