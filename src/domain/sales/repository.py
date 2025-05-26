from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from .models import Sale


class AbstractSalesRepository(ABC):
    @abstractmethod
    async def add_sale(self, sale: Sale) -> Sale:
        """Persist a new sale"""
        # just for testing, because I have no way to simulate perchases
        pass

    @abstractmethod
    async def get_sales_between_dates(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        product_id: Optional[str] = None,
        category_id: Optional[str] = None,
    ) -> list[Sale]:
        """Retrieve sales between two dates"""
        pass
