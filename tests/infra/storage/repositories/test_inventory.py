import uuid
from datetime import datetime, timedelta, timezone

import pytest

from src.domain.inventory.models import InventoryItem, InventoryUpdate
from src.uow.sqlalchemy import SQLAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_add_inventory_update_creates_item(database_creation):
    """
    Adding a first inventory update for a product should create
    a new InventoryItem with that quantity.
    """
    uow = SQLAlchemyUnitOfWork()

    product_id = str(uuid.uuid4())
    update = InventoryUpdate(
        id=str(uuid.uuid4()),
        product_id=product_id,
        quantity=15,
        created_at=datetime.now(timezone.utc),
    )

    # perform the update
    async with uow:
        await uow.inventory.add_inventory_update(update)

    # now we should be able to fetch it
    async with uow:
        item = await uow.inventory.get_by_product(product_id)

    assert item is not None
    assert isinstance(item, InventoryItem)
    assert item.product_id == product_id
    assert item.quantity == 15


@pytest.mark.asyncio
async def test_accumulate_inventory_updates(database_creation):
    """
    When you add multiple updates for the same product, the quantities should accumulate.
    """
    uow = SQLAlchemyUnitOfWork()
    product_id = str(uuid.uuid4())

    # first +10
    u1 = InventoryUpdate(
        id=str(uuid.uuid4()),
        product_id=product_id,
        quantity=10,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=5),
    )
    # then +5
    u2 = InventoryUpdate(
        id=str(uuid.uuid4()),
        product_id=product_id,
        quantity=5,
        created_at=datetime.now(timezone.utc),
    )

    async with uow:
        await uow.inventory.add_inventory_update(u1)

    async with uow:
        await uow.inventory.add_inventory_update(u2)

    async with uow:
        item = await uow.inventory.get_by_product(product_id)

    assert item is not None
    assert item.quantity == 15


@pytest.mark.asyncio
async def test_list_all_inventory_items(database_creation):
    """
    list() should return every product that has had at least one update.
    """
    uow = SQLAlchemyUnitOfWork()

    # create two different products
    p1, p2 = str(uuid.uuid4()), str(uuid.uuid4())
    u1 = InventoryUpdate(
        id=str(uuid.uuid4()),
        product_id=p1,
        quantity=3,
        created_at=datetime.now(timezone.utc),
    )
    u2 = InventoryUpdate(
        id=str(uuid.uuid4()),
        product_id=p2,
        quantity=7,
        created_at=datetime.now(timezone.utc),
    )

    async with uow:
        await uow.inventory.add_inventory_update(u1)
        await uow.inventory.add_inventory_update(u2)

    async with uow:
        items = await uow.inventory.list()

    # we expect exactly two items, one per product
    ids = {itm.product_id for itm in items}
    assert ids == {p1, p2}
    # quantities should match the updates
    qtys = {itm.quantity for itm in items}
    assert qtys == {3, 7}


@pytest.mark.asyncio
async def test_low_stock_alerts(database_creation):
    """
    low_stock_alerts(threshold) should return only those items at or below threshold.
    """
    uow = SQLAlchemyUnitOfWork()

    # p1 => quantity 2, p2 => 20
    p1, p2 = str(uuid.uuid4()), str(uuid.uuid4())
    u1 = InventoryUpdate(
        id=str(uuid.uuid4()),
        product_id=p1,
        quantity=2,
        created_at=datetime.now(timezone.utc),
    )
    u2 = InventoryUpdate(
        id=str(uuid.uuid4()),
        product_id=p2,
        quantity=20,
        created_at=datetime.now(timezone.utc),
    )

    async with uow:
        await uow.inventory.add_inventory_update(u1)
        await uow.inventory.add_inventory_update(u2)

    # threshold=5 should only catch p1
    async with uow:
        low = await uow.inventory.low_stock_alerts(threshold=5)

    assert len(low) == 1
    assert low[0].product_id == p1
    assert low[0].quantity == 2
