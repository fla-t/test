from uuid import uuid4
from dataclasses import dataclass
from datetime import datetime, timezone

UUID = str


@dataclass
class Sale:
    id: UUID
    product_id: UUID
    quantity: int
    total_price: float
    created_at: datetime

    @classmethod
    def create(cls, product_id: UUID, quantity: int, total_price: float) -> "Sale":
        return cls(
            id=str(uuid4()),
            product_id=product_id,
            quantity=quantity,
            total_price=total_price,
            created_at=datetime.now(timezone.utc),
        )
