from dataclasses import dataclass
from datetime import datetime

UUID = str


@dataclass
class Sale:
    id: UUID
    product_id: UUID
    quantity: int
    total_price: float
    created_at: datetime
