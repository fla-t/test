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
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_inventory_update(self, update: DomainUpdate) -> None:
        # persist the update record
        orm_update = UpdateORM(
            id=update.id,
            product_id=update.product_id,
            quantity=update.quantity,
            created_at=update.created_at,
        )
        self.session.add(orm_update)

        # adjust or create the current inventory item tally
        existing = await self.session.get(ItemORM, update.product_id)
        if existing:
            existing.quantity = existing.quantity + update.quantity
        else:
            new_item = ItemORM(
                product_id=update.product_id,
                quantity=update.quantity,
            )
            self.session.add(new_item)

    async def get_by_product(self, product_id: str) -> Optional[DomainItem]:
        item = await self.session.get(ItemORM, product_id)
        if item:
            return DomainItem(product_id=item.product_id, quantity=item.quantity)

    async def list(self) -> List[DomainItem]:
        result = await self.session.execute(select(ItemORM))
        items = result.scalars().all()
        return [DomainItem(product_id=i.product_id, quantity=i.quantity) for i in items]

    async def low_stock_alerts(self, threshold: int = 10) -> List[DomainItem]:
        query = select(ItemORM).where(ItemORM.quantity <= threshold)
        result = await self.session.execute(query)
        items = result.scalars().all()
        return [DomainItem(product_id=i.product_id, quantity=i.quantity) for i in items]
