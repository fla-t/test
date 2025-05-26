from abc import ABC, abstractmethod
from typing import Optional

from .models import Product, ProductCategory


class AbstractProductRepository(ABC):
    @abstractmethod
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get a product by its ID"""
        pass

    @abstractmethod
    async def get_products(self) -> list[Product]:
        """Get all products"""
        pass

    @abstractmethod
    async def create_product(self, product: Product) -> Product:
        """Create a new product"""
        pass

    @abstractmethod
    async def update_product(self, product: Product) -> Product:
        """Update an existing product"""

        # I have worked in a lot of inventory related codebase,
        # and the best way to update is to create a new product
        # on each update, u can store a id that connects all of the
        # versions of the product together, but again keeping it simple :)
        pass

    @abstractmethod
    async def delete_product(self, product_id: str) -> None:
        """Delete a product by its ID"""
        pass

    @abstractmethod
    async def add_category(self, category: ProductCategory) -> ProductCategory:
        """Get a product category by its ID"""
        pass

    @abstractmethod
    async def get_category(self, category_id: str) -> Optional[ProductCategory]:
        """Get a product category by its ID"""
        pass

    @abstractmethod
    async def get_categories(self) -> list[ProductCategory]:
        """Get all product categories"""
        pass
