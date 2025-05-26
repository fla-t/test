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

    async def get_sales_between_dates(self, start_date: datetime, end_date: datetime) -> list[Sale]:
        return [sale for sale in self.sales if start_date <= sale.created_at <= end_date]

    async def get_sales_by_product(
        self,
        product_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[Sale]:
        return [
            sale
            for sale in self.sales
            if sale.product_id == product_id
            and (start_date is None or sale.created_at >= start_date)
            and (end_date is None or sale.created_at <= end_date)
        ]

    async def get_sales_by_category(
        self,
        category_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[Sale]:
        products_in_category = [
            product_id
            for product_id, product in self.products.items()
            if product.category_id == category_id
        ]

        return [
            sale
            for sale in self.sales
            if sale.product_id in products_in_category
            and (start_date is None or sale.created_at >= start_date)
            and (end_date is None or sale.created_at <= end_date)
        ]
