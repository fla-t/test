from uuid import uuid4
from typing import Optional

from src.uow.abstract import AbstractUnitOfWork
from src.domain.product.models import Product, ProductCategory


class ProductService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create_product(
        self, name: str, category_id: str, description: str, price: float
    ) -> Product:
        product = Product(
            id=str(uuid4()),
            name=name,
            category_id=category_id,
            description=description,
            price=price,
        )

        async with self.uow:
            await self.uow.products.create_product(product)

        return product

    async def get_product(self, product_id: str) -> Optional[Product]:
        async with self.uow:
            return await self.uow.products.get_product(product_id)

    async def get_products(self) -> list[Product]:
        async with self.uow:
            return await self.uow.products.get_products()

    async def update_product(self, product: Product) -> Product:
        async with self.uow:
            updated_product = await self.uow.products.update_product(product)

        return updated_product

    async def delete_product(self, product_id: str) -> None:
        async with self.uow:
            await self.uow.products.delete_product(product_id)

    async def add_category(self, name: str, description: str) -> ProductCategory:
        category = ProductCategory(
            id=str(uuid4()),
            name=name,
            description=description,
        )

        async with self.uow:
            await self.uow.products.add_category(category)

        return category

    async def get_category(self, category_id: str) -> Optional[ProductCategory]:
        async with self.uow:
            return await self.uow.products.get_category(category_id)

    async def get_categories(self) -> list[ProductCategory]:
        async with self.uow:
            return await self.uow.products.get_categories()
