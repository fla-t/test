from dataclasses import dataclass
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
    id: str
    sku_id: str
    qty: int

    @classmethod
    def create(cls, sku_id: str, qty: int) -> "InventoryReceiving":
        return cls(id=str(uuid4()), sku_id=sku_id, qty=qty)


@dataclass
class Inventory:
    sku_id: str
    qty: int

    @classmethod
    def create(cls, sku_id: str, qty: int) -> "Inventory":
        return cls(sku_id=sku_id, qty=qty)
