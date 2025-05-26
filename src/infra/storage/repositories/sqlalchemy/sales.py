from datetime import datetime
from typing import List, Optional, Any

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.sales.models import Sale as DomainSale
from src.domain.sales.repository import AbstractSalesRepository
from src.infra.storage.models.sales import Sale as SaleORM
from src.infra.storage.models.product import Product as ProductORM


class SalesRepository(AbstractSalesRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_sale(self, sale: DomainSale) -> DomainSale:
        orm = SaleORM(
            id=sale.id,
            product_id=sale.product_id,
            quantity=sale.quantity,
            total_price=sale.total_price,
            created_at=sale.created_at,
        )
        self.session.add(orm)
        return sale

    async def get_sales_between_dates(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        product_id: Optional[str] = None,
        category_id: Optional[str] = None,
    ) -> List[DomainSale]:

        query = select(SaleORM)
        filters: list[Any] = []

        if start_date:
            filters.append(SaleORM.created_at >= start_date)

        if end_date:
            filters.append(SaleORM.created_at <= end_date)

        if product_id:
            filters.append(SaleORM.product_id == product_id)

        # if filtering by category, join into ProductORM
        if category_id is not None:
            query = query.join(ProductORM, SaleORM.product_id == ProductORM.id)
            filters.append(ProductORM.category_id == category_id)

        if filters:
            query = query.where(and_(*filters))

        result = await self.session.execute(query)
        results = result.scalars().all()

        return [
            DomainSale(
                id=s.id,
                product_id=s.product_id,
                quantity=s.quantity,
                total_price=s.total_price,
                created_at=s.created_at,
            )
            for s in results
        ]
