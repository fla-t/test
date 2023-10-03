from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from services.sales.utils import now_in_utc


@dataclass
class Sale:
    """
    Represents how we store a sale as, what's the metadata that goes behind the sale?

    Since we don't have users, and I don't want to bloat the scope so I am not adding and
    "Who ordered this" field.
    """

    id: str
    inventory_log_id: str
    price: int
    created_at: datetime

    @classmethod
    def create(cls, inventory_log_id: str, price: int) -> "Sale":
        return cls(
            id=str(uuid4()), inventory_log_id=inventory_log_id, price=price, created_at=now_in_utc()
        )
