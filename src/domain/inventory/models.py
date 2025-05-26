from uuid import uuid4
from dataclasses import dataclass
from datetime import datetime, timezone

UUID = str


@dataclass
class InventoryUpdate:
    id: UUID
    product_id: UUID
    quantity: int
    created_at: datetime

    @classmethod
    def create(cls, product_id: UUID, quantity: int) -> "InventoryUpdate":
        """Factory method to create a new inventory update"""
        return cls(
            id=str(uuid4()),
            product_id=product_id,
            quantity=quantity,
            created_at=datetime.now(timezone.utc),
        )


@dataclass
class InventoryItem:
    product_id: UUID
    quantity: int
