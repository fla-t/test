from dataclasses import dataclass
from datetime import datetime


@dataclass
class Sale:
    id: str
    product_id: str
    quantity: int
    total_price: float
    created_at: datetime
