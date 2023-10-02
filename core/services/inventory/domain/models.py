from dataclasses import dataclass
from typing import List, Optional
from uuid import uuid4


@dataclass
class SKU:
    id: str
    name: str
    description: str

    @classmethod
    def create(cls, name: str, description: str) -> "SKU":
        return cls(id=str(uuid4()), name=name, description=description)


@dataclass
class InventoryLog:
    """
    This is our main inventory aggregate, basically we are storing each log of entry. not a single
    state. Why? because states are hard to manage and we need to have a perfect concurrency model to
    keep it afloat.

    If you are thinking, that computing quantities each time might be a problem, then you are right,
    but we will probably cache that. For the sake of simplicity, and I am not going to do that here.

    This model represents a single row of inventory change. again, for simplicity i am not tracking
    any change

    """

    id: str
    sku_id: str
    quantity_changed: int

    @classmethod
    def create(self, sku_id: str, quantity_changed: int) -> "InventoryLog":
        return self(id=str(uuid4()), sku_id=sku_id, quantity_changed=quantity_changed)

    def __post_init__(self) -> None:
        if self.quantity_changed == 0:
            raise ValueError("Quantity changed cannot be zero")
