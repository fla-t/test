import pytest

from src.uow.inmemory import InMemoryUnitOfWork
from src.services.inventory.service import InventoryService
from src.domain.inventory.models import InventoryItem


@pytest.mark.asyncio
async def test_current_inventory_empty():
    uow = InMemoryUnitOfWork()
    service = InventoryService(uow)

    item = await service.current_inventory("nonexistent")
    assert item is None


@pytest.mark.asyncio
async def test_current_inventory_list_empty():
    uow = InMemoryUnitOfWork()
    service = InventoryService(uow)

    items = await service.current_inventory_list()
    assert items == []


@pytest.mark.asyncio
async def test_add_and_get_inventory_update():
    uow = InMemoryUnitOfWork()
    service = InventoryService(uow)

    pid = "prod-123"
    # apply +5 stock
    updated = await service.add_inventory_update(product_id=pid, quantity=5)
    assert isinstance(updated, InventoryItem)
    assert updated.product_id == pid
    assert updated.quantity == 5

    # get current inventory directly
    current = await service.current_inventory(pid)
    assert current.quantity == 5

    # list has exactly one
    all_items = await service.current_inventory_list()
    assert len(all_items) == 1
    assert all_items[0].product_id == pid


@pytest.mark.asyncio
async def test_accumulate_multiple_updates():
    uow = InMemoryUnitOfWork()
    service = InventoryService(uow)

    pid = "prod-xyz"
    # +10
    await service.add_inventory_update(pid, 10)
    # -3
    await service.add_inventory_update(pid, -3)
    # we expect 7
    current = await service.current_inventory(pid)
    assert current.quantity == 7


@pytest.mark.asyncio
async def test_low_stock_alerts():
    uow = InMemoryUnitOfWork()
    service = InventoryService(uow)

    # seed some products
    await service.add_inventory_update("p1", 100)
    await service.add_inventory_update("p2", 5)
    await service.add_inventory_update("p3", 10)

    # threshold default 10: p2 (5) and p3 (10) are <=10
    alerts = await service.low_stock_alerts()
    ids = {item.product_id for item in alerts}
    assert ids == {"p2", "p3"}

    # threshold 6: only p2
    alerts2 = await service.low_stock_alerts(threshold=6)
    assert [it.product_id for it in alerts2] == ["p2"]


@pytest.mark.asyncio
async def test_isolation_between_tests():
    # First UoW
    uow1 = InMemoryUnitOfWork()
    service1 = InventoryService(uow1)
    await service1.add_inventory_update("x", 1)

    # Second UoW should be clean
    uow2 = InMemoryUnitOfWork()
    service2 = InventoryService(uow2)
    all_items = await service2.current_inventory_list()
    assert all_items == []
