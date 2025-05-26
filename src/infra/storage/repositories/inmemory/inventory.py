# src/infra/storage/repositories/inventory.py
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.inventory.models import InventoryItem as DomainItem, InventoryUpdate as DomainUpdate
from src.domain.inventory.repository import AbstractInventoryRepository
from src.infra.storage.models.inventory import (
    InventoryItem as ItemORM,
    InventoryUpdate as UpdateORM,
)


class InventoryRepository(AbstractInventoryRepository):
    def __init__(self) -> None:
        self.inventory_updates = []
        self.inventory = {}

    async def add_inventory_update(self, update: DomainUpdate) -> None:
        pass

    async def get_by_product(self, product_id: str) -> Optional[DomainItem]:
        pass

    async def list(self) -> List[DomainItem]:
        pass

    async def low_stock_alerts(self, threshold: int = 10) -> List[DomainItem]:
        pass
