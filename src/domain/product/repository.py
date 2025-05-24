from abc import ABC, abstractmethod

from .models import Product, ProductCategory


class ProductRepository(ABC):
    @abstractmethod
    def get_product(self, product_id: str) -> Product:
        """Get a product by its ID."""
        pass

    @abstractmethod
    def get_products(self) -> list[Product]:
        """Get all products."""
        pass

    @abstractmethod
    def create_product(self, product: Product) -> Product:
        """Create a new product."""
        pass

    @abstractmethod
    def update_product(self, product: Product) -> Product:
        """Update an existing product."""

        # I have worked in a lot of inventory related codebase,
        # and the best way to update is to create a new product
        # on each update, u can store a id that connects all of the
        # versions of the product together, but again keeping it simple :)
        pass

    @abstractmethod
    def delete_product(self, product_id: str) -> None:
        """Delete a product by its ID."""
        pass

    @abstractmethod
    def add_category(self, category_id: str) -> ProductCategory:
        """Get a product category by its ID."""
        pass

    @abstractmethod
    def get_category(self, category_id: str) -> ProductCategory:
        """Get a product category by its ID."""
        pass

    @abstractmethod
    def get_categories(self) -> list[ProductCategory]:
        """Get all product categories."""
        pass
