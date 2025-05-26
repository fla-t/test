from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.uow.sqlalchemy import SQLAlchemyUnitOfWork
from src.services.product.service import ProductService

ProductRouter = APIRouter(prefix="/products", tags=["Product"])
CategoryRouter = APIRouter(prefix="/categories", tags=["Category"])


class ProductSchema(BaseModel):
    """Request schema for products"""

    name: str
    category_id: str
    description: str
    price: float


class ProductCategorySchema(BaseModel):
    """Request schema for product categories"""

    name: str
    description: str


@ProductRouter.get("/")
async def get_products(
    uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork),
):
    """
    Get all products.
    """
    service = ProductService(uow)
    return await service.get_products()


@ProductRouter.get("/{product_id}")
async def get_product(
    product_id: str,
    uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork),
):
    """
    Get a product by ID.
    """
    service = ProductService(uow)
    product = await service.get_product(product_id)

    if not product:
        JSONResponse(
            status_code=404,
            content={"status": "error", "message": "Product not found"},
        )

    return product


@ProductRouter.post("/")
async def create_product(
    product: ProductSchema,
    uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork),
):
    """
    Create a new product.
    """
    service = ProductService(uow)
    return await service.create_product(
        name=product.name,
        category_id=product.category_id,
        description=product.description,
        price=product.price,
    )


@ProductRouter.put("/{product_id}")
async def update_product(
    product_id: str,
    product: ProductSchema,
    uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork),
):
    """
    Update an existing product.
    """
    service = ProductService(uow)
    existing_product = await service.get_product(product_id)

    if not existing_product:
        JSONResponse(
            status_code=404,
            content={"status": "error", "message": "Product not found"},
        )

    return await service.update_product(
        product_id=product_id,
        updated_name=product.name,
        updated_category_id=product.category_id,
        updated_description=product.description,
        updated_price=product.price,
    )


@ProductRouter.delete("/{product_id}")
async def delete_product(
    product_id: str,
    uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork),
):
    """
    Delete a product by ID.
    """
    service = ProductService(uow)
    await service.delete_product(product_id)
    return {"message": "Product deleted successfully"}


@CategoryRouter.get("/")
async def get_categories(
    uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork),
):
    """
    Get all product categories.
    """
    service = ProductService(uow)
    return await service.get_categories()


@CategoryRouter.get("/{category_id}")
async def get_category(
    category_id: str,
    uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork),
):
    """
    Get a product category by ID.
    """
    service = ProductService(uow)
    return await service.get_category(category_id)


@CategoryRouter.post("/")
async def create_category(
    category: ProductCategorySchema,
    uow: SQLAlchemyUnitOfWork = Depends(SQLAlchemyUnitOfWork),
):
    """
    Create a new product category.
    """
    service = ProductService(uow)
    return await service.add_category(
        name=category.name,
        description=category.description,
    )
