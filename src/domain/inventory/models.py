from dataclasses import dataclass
from datetime import datetime

UUID = str


@dataclass
class InventoryUpdate:
    id: UUID
    product_id: UUID
    quantity: int
    created_at: datetime


@dataclass
class InventoryItem:
    product_id: UUID
    quantity: int
