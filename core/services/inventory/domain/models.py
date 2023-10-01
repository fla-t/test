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
class InventoryReceiving:
    """Basically a log of inventory received, the actual quantities will be in the inventory table"""

    id: str
    cost: int
    received_from: str

    @classmethod
    def create(cls, cost: int, received_from: str) -> "InventoryReceiving":
        return cls(id=str(uuid4()), cost=cost, received_from=received_from)


@dataclass
class InventoryLog:
    """
    This is our main inventory aggregate, basically we are storing each log of entry. not a single
    state. Why? because states are hard to manage and we need to have a perfect concurrency model to
    keep it afloat.

    If you are thinking, that computing quantities each time might be a problem, then you are right,
    but we will probably cache that. For the sake of simiplicity, and I am not going to do that here.

    """

    id: str
    sku_id: str
    qty: int
    receiving_id: Optional[str]
    sale_id: Optional[str]
