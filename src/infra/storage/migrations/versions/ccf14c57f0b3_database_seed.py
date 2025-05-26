"""Database seed

Revision ID: ccf14c57f0b3
Revises: d51666f213fe
Create Date: 2025-05-27 01:12:49.632969

"""

from typing import Sequence, Union
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "ccf14c57f0b3"
down_revision: Union[str, None] = "d51666f213fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema"""

    # THIS IS A MIGRATION FOR SEEDING THE DATABASE

    # define tables
    product_categories_table = table(
        "product_categories",
        column("id", postgresql.UUID(as_uuid=False)),
        column("name", sa.String()),
        column("description", sa.Text()),
    )

    products_table = table(
        "products",
        column("id", postgresql.UUID(as_uuid=False)),
        column("name", sa.String()),
        column("category_id", postgresql.UUID(as_uuid=False)),
        column("description", sa.Text()),
        column("price", sa.Float()),
    )

    inventory_table = table(
        "inventory_items",
        column("product_id", postgresql.UUID(as_uuid=False)),
        column("quantity", sa.Integer()),
    )
    inventory_updates_table = table(
        "inventory_updates",
        column("id", postgresql.UUID(as_uuid=False)),
        column("product_id", postgresql.UUID(as_uuid=False)),
        column("quantity", sa.Integer()),
        column("created_at", sa.DateTime(timezone=True)),
    )

    sales_table = table(
        "sales",
        column("id", postgresql.UUID(as_uuid=False)),
        column("product_id", postgresql.UUID(as_uuid=False)),
        column("quantity", sa.Integer()),
        column("total_price", sa.Float()),
        column("created_at", sa.DateTime(timezone=True)),
    )

    # first add categories
    categories = [
        {"id": str(uuid4()), "name": "Electronics", "description": "Devices and gadgets"},
        {"id": str(uuid4()), "name": "Food", "description": "Groceries and food items"},
        {"id": str(uuid4()), "name": "Medicines", "description": "Health and wellness products"},
        {"id": str(uuid4()), "name": "Beverages", "description": "Drinks and refreshments"},
    ]
    op.bulk_insert(product_categories_table, categories)

    products = [
        {
            "id": str(uuid4()),
            "name": "Smartphone",
            "description": "Latest model smartphone with advanced features",
            "price": 699.99,
            "category_id": categories[0]["id"],
        },
        {
            "id": str(uuid4()),
            "name": "Laptop",
            "description": "High-performance laptop for work and gaming",
            "price": 1299.99,
            "category_id": categories[0]["id"],
        },
        {
            "id": str(uuid4()),
            "name": "Organic Apples",
            "description": "Fresh organic apples from local farms",
            "price": 3.99,
            "category_id": categories[1]["id"],
        },
        {
            "id": str(uuid4()),
            "name": "Whole Wheat Bread",
            "description": "Healthy whole wheat bread, perfect for sandwiches",
            "price": 2.49,
            "category_id": categories[1]["id"],
        },
        {
            "id": str(uuid4()),
            "name": "Pain Reliever",
            "description": "Effective pain relief medication",
            "price": 9.99,
            "category_id": categories[2]["id"],
        },
        {
            "id": str(uuid4()),
            "name": "Vitamins",
            "description": "Daily vitamins for overall health",
            "price": 19.99,
            "category_id": categories[2]["id"],
        },
        {
            "id": str(uuid4()),
            "name": "Coffee Beans",
            "description": "Premium coffee beans for a perfect brew",
            "price": 12.99,
            "category_id": categories[3]["id"],
        },
        {
            "id": str(uuid4()),
            "name": "Green Tea",
            "description": "Refreshing green tea leaves for a healthy drink",
            "price": 8.99,
            "category_id": categories[3]["id"],
        },
    ]
    op.bulk_insert(products_table, products)

    # add inventory for those products
    inventory = [
        {"product_id": products[0]["id"], "quantity": 100},
        {"product_id": products[1]["id"], "quantity": 100},
        {"product_id": products[2]["id"], "quantity": 100},
        {"product_id": products[3]["id"], "quantity": 100},
        {"product_id": products[4]["id"], "quantity": 100},
    ]
    inventory_updates = [
        {
            "id": str(uuid4()),
            "product_id": products[0]["id"],
            "quantity": 100,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "id": str(uuid4()),
            "product_id": products[1]["id"],
            "quantity": 100,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "id": str(uuid4()),
            "product_id": products[2]["id"],
            "quantity": 100,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "id": str(uuid4()),
            "product_id": products[3]["id"],
            "quantity": 100,
            "created_at": datetime.now(timezone.utc),
        },
    ]
    op.bulk_insert(inventory_table, inventory)
    op.bulk_insert(inventory_updates_table, inventory_updates)

    # add sales data
    sales = [
        {
            "id": str(uuid4()),
            "product_id": products[0]["id"],
            "quantity": 1,
            "total_price": 699.99,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "id": str(uuid4()),
            "product_id": products[1]["id"],
            "quantity": 1,
            "total_price": 1299.99,
            "created_at": datetime.now(timezone.utc) - timedelta(days=1),
        },
        {
            "id": str(uuid4()),
            "product_id": products[2]["id"],
            "quantity": 3,
            "total_price": 11.97,
            "created_at": datetime.now(timezone.utc) - timedelta(days=2),
        },
    ]
    op.bulk_insert(sales_table, sales)


def downgrade() -> None:
    """Downgrade schema"""
    # dont have the capacity to write this rn :)
    pass
