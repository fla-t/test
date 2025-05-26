from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from src.uow.sqlalchemy import SQLAlchemyUnitOfWork
from src.services.sales.service import ProductService

SalesRouter = APIRouter(prefix="/sales", tags=["Sales"])


class SaleSchema(BaseModel):
    product_id: str
    quantity: int
    total_price: float


@SalesRouter.post("/")
async def create_sale(
    request: SaleSchema,
    uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork),
):
    """
    Create a new sale.
    """
    service = ProductService(uow)
    sale = await service.create_sale(request.product_id, request.quantity, request.total_price)

    return JSONResponse(content=jsonable_encoder(sale), status_code=201)


@SalesRouter.get("/between-dates")
async def get_sales_between_dates(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    product_id: Optional[str] = None,
    category_id: Optional[str] = None,
    uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork),
):
    """
    Get sales between two dates.
    """
    service = ProductService(uow)
    sales = await service.get_sales_between_dates(start_date, end_date, product_id, category_id)

    return JSONResponse(content=jsonable_encoder(sales))


@SalesRouter.get("/compare")
async def compare_sales(
    first_start: datetime,
    first_end: datetime,
    second_start: datetime,
    second_end: datetime,
    product_id: Optional[str] = None,
    category_id: Optional[str] = None,
    uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork),
):
    """
    Compare sales for a product or category.
    """
    service = ProductService(uow)
    comparison = await service.compare_sales(
        first_start, first_end, second_start, second_end, product_id, category_id
    )

    return JSONResponse(content=jsonable_encoder(comparison))
