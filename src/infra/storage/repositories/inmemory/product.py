from typing import Optional

from src.domain.product.repository import AbstractProductRepository
from src.domain.product.models import Product, ProductCategory


class ProductRepository(AbstractProductRepository):
    def __init__(self) -> None:
        self.products: dict[str, Product] = {}
        self.categories: dict[str, ProductCategory] = {}

    async def create_product(self, product: Product) -> Product:
        self.products[product.id] = product
        return product

    async def get_product(self, product_id: str) -> Optional[Product]:
        return self.products.get(product_id)

    async def get_products(self) -> list[Product]:
        return list(self.products.values())

    async def update_product(self, product: Product) -> Product:
        self.products[product.id] = product
        return product

    async def delete_product(self, product_id: str) -> None:
        del self.products[product_id]

    async def add_category(self, category: ProductCategory) -> ProductCategory:
        self.categories[category.id] = category
        return category

    async def get_category(self, category_id: str) -> Optional[ProductCategory]:
        return self.categories.get(category_id)

    async def get_categories(self) -> list[ProductCategory]:
        return list(self.categories.values())
