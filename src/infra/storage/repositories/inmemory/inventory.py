from typing import Optional

from src.domain.inventory.models import InventoryItem, InventoryUpdate
from src.domain.inventory.repository import AbstractInventoryRepository


class InventoryRepository(AbstractInventoryRepository):
    def __init__(self) -> None:
        self.inventory_updates: list[InventoryUpdate] = []
        self.inventory: dict[str, InventoryItem] = {}

    async def add_inventory_update(self, update: InventoryUpdate) -> None:
        self.inventory_updates.append(update)

        if update.product_id in self.inventory:
            self.inventory[update.product_id].quantity += update.quantity
        else:
            self.inventory[update.product_id] = InventoryItem(
                product_id=update.product_id, quantity=update.quantity
            )

    async def get_by_product(self, product_id: str) -> Optional[InventoryItem]:
        return self.inventory.get(product_id)

    async def low_stock_alerts(self, threshold: int = 10) -> list[InventoryItem]:
        return [item for item in self.inventory.values() if item.quantity <= threshold]

    async def list(self) -> list[InventoryItem]:
        return list(self.inventory.values())
