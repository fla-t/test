from typing import Optional, Literal
from datetime import datetime, timedelta
from dataclasses import dataclass

from src.uow.abstract import AbstractUnitOfWork
from src.domain.sales.models import Sale


@dataclass
class SaleComparison:
    time_label: str
    first_total: float
    second_total: float


class ProductService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create_sale(self, product_id: str, quantity: int, total_price: float) -> Sale:
        # this is just a test endpoint, its there so I can seed data.
        # otherwise the total_price would be calculated based on the product price
        # and fetched from the products using ACL, which I left was overkill

        sale = Sale.create(
            product_id=product_id,
            quantity=quantity,
            total_price=total_price,
        )

        async with self.uow:
            await self.uow.sales.add_sale(sale)

        return sale

    async def get_sales_between_dates(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        product_id: Optional[str] = None,
        category_id: Optional[str] = None,
    ) -> list[Sale]:
        async with self.uow:
            return await self.uow.sales.get_sales_between_dates(
                start_date, end_date, product_id, category_id
            )

    async def compare_sales(
        self,
        first_start: datetime,
        first_end: datetime,
        second_start: datetime,
        second_end: datetime,
        product_id: Optional[str] = None,
        category_id: Optional[str] = None,
        granularity: Literal["day", "week", "month"] = "day",
    ) -> list[SaleComparison]:
        """
        Compare sales based on total price or quantity.
        """

        assert (
            first_end - first_start == second_end - second_start
        ), "The time periods must be of the same length."

        async with self.uow:
            first_sales = await self.uow.sales.get_sales_between_dates(
                first_start, first_end, product_id, category_id
            )
            second_sales = await self.uow.sales.get_sales_between_dates(
                second_start, second_end, product_id, category_id
            )

        # Now I will group the sales by the specified granularity, and return the results
        # those can be displayed in a chart

        if granularity == "day":
            step = timedelta(days=1)

            def make_label(date: datetime) -> str:
                return date.strftime("%Y-%m-%d")

        elif granularity == "week":
            step = timedelta(weeks=1)

            def make_label(date: datetime) -> str:
                year, week, _ = date.isocalendar()
                return f"{year}-W{week:02d}"

        else:
            step = timedelta(weeks=4)

            def make_label(date: datetime) -> str:
                return date.strftime("%Y-%m")

        def buckets(start: datetime, end: datetime) -> list[tuple[datetime, datetime]]:
            current = start
            buckets: list[tuple[datetime, datetime]] = []
            while current < end:
                next = current + step
                buckets.append((current, next))
                current = next

            return buckets

        first_bucket = buckets(first_start, first_end)
        second_bucket = buckets(second_start, second_end)

        comparison: list[SaleComparison] = []

        for (first_start, first_end), (second_start, second_end) in zip(
            first_bucket, second_bucket
        ):
            first_sales_in_bucket = [
                sale for sale in first_sales if first_start <= sale.created_at < first_end
            ]
            second_sales_in_bucket = [
                sale for sale in second_sales if second_start <= sale.created_at < second_end
            ]

            total_first = sum(sale.total_price for sale in first_sales_in_bucket)
            total_second = sum(sale.total_price for sale in second_sales_in_bucket)

            comparison.append(
                SaleComparison(
                    time_label=make_label(first_start),
                    first_total=total_first,
                    second_total=total_second,
                )
            )

        return comparison
