from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from src.domain.product.repository import AbstractProductRepository
from src.domain.product.models import Product, ProductCategory
from src.infra.storage.models.product import (
    Product as ProductORM,
    ProductCategory as ProductCategoryORM,
)


class ProductRepository(AbstractProductRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_product(self, product: Product) -> Product:
        product_orm = ProductORM(
            id=product.id,
            name=product.name,
            category_id=product.category_id,
            description=product.description,
            price=product.price,
        )
        self.session.add(product_orm)
        return product

    async def get_product(self, product_id: str) -> Optional[Product]:
        query = select(ProductORM).where(ProductORM.id == product_id)
        result = await self.session.execute(query)
        product_orm = result.scalar_one_or_none()

        if product_orm:
            return Product(
                id=product_orm.id,
                name=product_orm.name,
                category_id=product_orm.category_id,
                description=product_orm.description,
                price=product_orm.price,
            )

    async def get_products(self) -> list[Product]:
        query = select(ProductORM)
        result = await self.session.execute(query)
        products_orm = result.scalars().all()

        return [
            Product(
                id=product_orm.id,
                name=product_orm.name,
                category_id=product_orm.category_id,
                description=product_orm.description,
                price=product_orm.price,
            )
            for product_orm in products_orm
        ]

    async def update_product(self, product: Product) -> Product:
        query = (
            update(ProductORM)
            .where(ProductORM.id == product.id)
            .values(
                name=product.name,
                category_id=product.category_id,
                description=product.description,
                price=product.price,
            )
            .returning(ProductORM)
        )
        result = await self.session.execute(query)
        updated_product_orm = result.scalar_one()

        return Product(
            id=updated_product_orm.id,
            name=updated_product_orm.name,
            category_id=updated_product_orm.category_id,
            description=updated_product_orm.description,
            price=updated_product_orm.price,
        )

    async def delete_product(self, product_id: str) -> None:
        query = delete(ProductORM).where(ProductORM.id == product_id)
        await self.session.execute(query)

    async def add_category(self, category: ProductCategory) -> ProductCategory:
        category_orm = ProductCategoryORM(
            id=category.id,
            name=category.name,
            description=category.description,
        )
        self.session.add(category_orm)
        return category

    async def get_category(self, category_id: str) -> Optional[ProductCategory]:
        query = select(ProductCategoryORM).where(ProductCategoryORM.id == category_id)
        result = await self.session.execute(query)
        category_orm = result.scalar_one_or_none()

        if category_orm:
            return ProductCategory(
                id=category_orm.id,
                name=category_orm.name,
                description=category_orm.description,
            )

    async def get_categories(self) -> list[ProductCategory]:
        category_orms = await self.session.execute(select(ProductCategoryORM))
        categories_orm = category_orms.scalars().all()

        return [
            ProductCategory(
                id=category_orm.id,
                name=category_orm.name,
                description=category_orm.description,
            )
            for category_orm in categories_orm
        ]
