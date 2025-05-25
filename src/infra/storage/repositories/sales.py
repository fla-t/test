# src/infra/storage/repositories/sale.py

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, and_, join
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
        self, start_date: datetime, end_date: datetime
    ) -> List[DomainSale]:
        # assume ISO strings; convert to datetime
        query = (
            select(SaleORM)
            .where(SaleORM.created_at.between(start_date, end_date))
            .order_by(SaleORM.created_at)
        )
        result = await self.session.execute(query)
        return [
            DomainSale(
                id=o.id,
                product_id=o.product_id,
                quantity=o.quantity,
                total_price=o.total_price,
                created_at=o.created_at,
            )
            for o in result.scalars().all()
        ]

    async def get_sales_by_product(
        self,
        product_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[DomainSale]:
        filters = [SaleORM.product_id == product_id]
        if start_date is not None:
            filters.append(SaleORM.created_at >= start_date)
        if end_date is not None:
            filters.append(SaleORM.created_at <= end_date)

        query = select(SaleORM).where(and_(*filters)).order_by(SaleORM.created_at)
        result = await self.session.execute(query)
        return [
            DomainSale(
                id=o.id,
                product_id=o.product_id,
                quantity=o.quantity,
                total_price=o.total_price,
                created_at=o.created_at,
            )
            for o in result.scalars().all()
        ]

    async def get_sales_by_category(
        self,
        category_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[DomainSale]:
        # join Sale → Product to filter by category
        join_query = join(SaleORM, ProductORM, SaleORM.product_id == ProductORM.id)

        filters = [ProductORM.category_id == category_id]
        if start_date is not None:
            filters.append(SaleORM.created_at >= start_date)
        if end_date is not None:
            filters.append(SaleORM.created_at <= end_date)

        query = (
            select(SaleORM)
            .select_from(join_query)
            .where(and_(*filters))
            .order_by(SaleORM.created_at)
        )
        result = await self.session.execute(query)
        return [
            DomainSale(
                id=o.id,
                product_id=o.product_id,
                quantity=o.quantity,
                total_price=o.total_price,
                created_at=o.created_at,
            )
            for o in result.scalars().all()
        ]
