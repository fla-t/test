from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from .models import Sale


class SaleRepository(ABC):
    @abstractmethod
    def get_sales_between_dates(
        self,
        start_date: str,
        end_date: str,
    ) -> list[Sale]:
        """Retrieve sales between two dates."""
        pass

    @abstractmethod
    def get_sales_by_product(
        self,
        product_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[Sale]:
        """Retrieve sales for a specific product."""
        pass

    @abstractmethod
    def get_sales_by_category(
        self,
        category_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[Sale]:
        """Retrieve sales for a specific product category."""
        pass
