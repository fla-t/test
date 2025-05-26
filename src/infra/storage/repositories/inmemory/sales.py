from datetime import datetime
from typing import Optional

from src.domain.sales.models import Sale
from src.domain.product.models import Product
from src.domain.sales.repository import AbstractSalesRepository


class SalesRepository(AbstractSalesRepository):
    def __init__(self) -> None:
        self.sales: list[Sale] = []
        # as far as for fake in memory storage,
        # its alright to mix in other stuff that u actually need
        # tbh it depends on the level of boundary between the services
        # and I have kept is weaker, since I don't have time to implement an ACL
        self.products: dict[str, Product] = {}

    async def add_product(self, product: Product) -> Product:
        self.products[product.id] = product
        return product

    async def add_sale(self, sale: Sale) -> Sale:
        self.sales.append(sale)
        return sale

    async def get_sales_between_dates(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        product_id: Optional[str] = None,
        category_id: Optional[str] = None,
    ) -> list[Sale]:
        results = self.sales

        if start_date:
            results = [s for s in results if s.created_at >= start_date]

        if end_date:
            results = [s for s in results if s.created_at <= end_date]

        if product_id:
            results = [s for s in results if s.product_id == product_id]

        if category_id:
            # filter by category, assuming products are available
            product_ids = [p.id for p in self.products.values() if p.category_id == category_id]
            results = [s for s in results if s.product_id in product_ids]

        return results
