# tests/infra/storage/repositories/test_sales.py
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from src.domain.product.models import Product, ProductCategory
from src.domain.sales.models import Sale
from src.uow.inmemory import InMemoryUnitOfWork


@pytest.mark.asyncio
async def test_add_and_get_sales_between_dates():
    """
    Creating three sales on different days, then retrieving only
    those within a given date range.
    """
    uow = InMemoryUnitOfWork()

    # bootstrap a category and product
    category = ProductCategory(id=str(uuid.uuid4()), name="cat1", description=None)
    product = Product(
        id=str(uuid.uuid4()),
        name="widget",
        category_id=category.id,
        description="desc",
        price=1.23,
    )

    now = datetime.now(timezone.utc)
    s_old = Sale(
        id=str(uuid.uuid4()),
        product_id=product.id,
        quantity=2,
        total_price=2 * product.price,
        created_at=now - timedelta(days=10),
    )
    s_mid = Sale(
        id=str(uuid.uuid4()),
        product_id=product.id,
        quantity=3,
        total_price=3 * product.price,
        created_at=now - timedelta(days=5),
    )
    s_new = Sale(
        id=str(uuid.uuid4()),
        product_id=product.id,
        quantity=4,
        total_price=4 * product.price,
        created_at=now,
    )

    async with uow:
        await uow.sales.add_product(product)

    # add all three sales
    async with uow:
        await uow.sales.add_sale(s_old)
        await uow.sales.add_sale(s_mid)
        await uow.sales.add_sale(s_new)

    # fetch between 7 days ago and now
    start = now - timedelta(days=7)
    end = now

    async with uow:
        between = await uow.sales.get_sales_between_dates(start_date=start, end_date=end)

    ids = {sale.id for sale in between}
    assert ids == {s_mid.id, s_new.id}


@pytest.mark.asyncio
async def test_get_sales_by_product(database_creation):
    """
    Sales for two different products; filtering by product_id returns only that product's sales.
    """
    uow = InMemoryUnitOfWork()

    cat = ProductCategory(id=str(uuid.uuid4()), name="cat2", description=None)
    p1 = Product(
        id=str(uuid.uuid4()),
        name="p1",
        category_id=cat.id,
        description="",
        price=5.0,
    )
    p2 = Product(
        id=str(uuid.uuid4()),
        name="p2",
        category_id=cat.id,
        description="",
        price=7.0,
    )

    # one sale per product, both at "now"
    now = datetime.now(timezone.utc)
    s1 = Sale(
        id=str(uuid.uuid4()),
        product_id=p1.id,
        quantity=1,
        total_price=5.0,
        created_at=now,
    )
    s2 = Sale(
        id=str(uuid.uuid4()),
        product_id=p2.id,
        quantity=2,
        total_price=14.0,
        created_at=now,
    )

    async with uow:
        await uow.sales.add_product(p1)
        await uow.sales.add_product(p2)

    # add both sales
    async with uow:
        await uow.sales.add_sale(s1)
        await uow.sales.add_sale(s2)

    # filter by product_id == p1.id
    async with uow:
        res = await uow.sales.get_sales_between_dates(product_id=p1.id)

    assert len(res) == 1
    assert res[0].id == s1.id
    assert res[0].product_id == p1.id


@pytest.mark.asyncio
async def test_get_sales_by_category(database_creation):
    """
    Sales for products in two categories; filtering by category_id returns only matching sales.
    """
    uow = InMemoryUnitOfWork()

    cat1 = ProductCategory(id=str(uuid.uuid4()), name="C1", description=None)
    cat2 = ProductCategory(id=str(uuid.uuid4()), name="C2", description=None)

    p1 = Product(
        id=str(uuid.uuid4()),
        name="prod1",
        category_id=cat1.id,
        description="",
        price=2.0,
    )
    p2 = Product(
        id=str(uuid.uuid4()),
        name="prod2",
        category_id=cat2.id,
        description="",
        price=3.0,
    )

    now = datetime.now(timezone.utc)
    s1 = Sale(
        id=str(uuid.uuid4()),
        product_id=p1.id,
        quantity=5,
        total_price=10.0,
        created_at=now,
    )
    s2 = Sale(
        id=str(uuid.uuid4()),
        product_id=p2.id,
        quantity=7,
        total_price=21.0,
        created_at=now,
    )

    async with uow:
        await uow.sales.add_product(p1)
        await uow.sales.add_product(p2)

    # add both sales
    async with uow:
        await uow.sales.add_sale(s1)
        await uow.sales.add_sale(s2)

    # filter by category_id == cat1.id
    async with uow:
        out = await uow.sales.get_sales_between_dates(category_id=cat1.id)

    assert len(out) == 1
    assert out[0].id == s1.id
    assert out[0].product_id == p1.id
