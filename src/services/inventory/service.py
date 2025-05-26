from typing import Optional

from src.uow.abstract import AbstractUnitOfWork
from src.domain.inventory.models import InventoryItem, InventoryUpdate


class InventoryService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def current_inventory(self, product_id: str) -> Optional[InventoryItem]:
        """Fetch the current inventory item for a given product ID."""
        async with self.uow:
            return await self.uow.inventory.get_by_product(product_id)

    async def current_inventory_list(self) -> list[InventoryItem]:
        """Fetch all inventory items."""
        async with self.uow:
            return await self.uow.inventory.list()

    async def add_inventory_update(self, product_id: str, quantity: int) -> Optional[InventoryItem]:
        """Add a new inventory update for a product."""
        update = InventoryUpdate.create(product_id=product_id, quantity=quantity)
        async with self.uow:
            await self.uow.inventory.add_inventory_update(update)
            return await self.uow.inventory.get_by_product(product_id)

    async def low_stock_alerts(self, threshold: int = 10) -> list[InventoryItem]:
        """Get a list of inventory items that are at or below the low stock threshold."""
        async with self.uow:
            return await self.uow.inventory.low_stock_alerts(threshold)
