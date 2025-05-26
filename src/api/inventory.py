from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from src.uow.sqlalchemy import SQLAlchemyUnitOfWork
from src.services.inventory.service import InventoryService

InventoryRouter = APIRouter(prefix="/inventory", tags=["Inventory"])


class InventoryUpdateSchema(BaseModel):
    product_id: str
    quantity: int


@InventoryRouter.get("/current/{product_id}")
async def current_inventory_for_product(
    product_id: str, uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork)
):
    """Fetch the current inventory item for a given product ID"""
    service = InventoryService(uow)
    inventory_item = await service.current_inventory(product_id)

    if inventory_item:
        return JSONResponse(content=jsonable_encoder(inventory_item))

    return JSONResponse(status_code=404, content={"message": "Inventory item not found"})


@InventoryRouter.get("/current")
async def current_inventory_list(uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork)):
    """Fetch all inventory items"""
    service = InventoryService(uow)
    inventory_items = await service.current_inventory_list()

    return JSONResponse(content=jsonable_encoder(inventory_items))


@InventoryRouter.post("/update")
async def add_inventory_update(
    request: InventoryUpdateSchema, uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork)
):
    """Add a new inventory update for a product"""
    service = InventoryService(uow)
    updated_item = await service.add_inventory_update(request.product_id, request.quantity)

    if updated_item:
        return JSONResponse(content=jsonable_encoder(updated_item))

    return JSONResponse(status_code=404, content={"message": "Product not found"})


@InventoryRouter.get("/low-stock-alerts")
async def low_stock_alerts(
    threshold: int = 10, uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork)
):
    """Get a list of inventory items that are at or below the low stock threshold"""
    service = InventoryService(uow)
    low_stock_items = await service.low_stock_alerts(threshold)

    return JSONResponse(content=jsonable_encoder(low_stock_items))
