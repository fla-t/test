from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.inventory.models import InventoryItem, InventoryUpdate


class AbstractInventoryRepository(ABC):
    @abstractmethod
    async def add_inventory_update(self, update: InventoryUpdate) -> None:
        """Persist a new inventory update"""

    @abstractmethod
    async def get_by_product(self, product_id: str) -> Optional[InventoryItem]:
        """Fetch a single inventory item by its product ID"""

    @abstractmethod
    async def list(self) -> List[InventoryItem]:
        """Return all inventory items"""

    @abstractmethod
    async def low_stock_alerts(self, threshold: int = 10) -> List[InventoryItem]:
        """Return items whose quantity is at or below `threshold`"""
