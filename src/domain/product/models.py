from uuid import uuid4
from dataclasses import dataclass

UUID = str


@dataclass
class Product:
    id: UUID
    name: str
    category_id: UUID
    description: str

    # in a real production app, I would store this in cents
    # or the lowest possible denomination to keep it accurate
    # I am just using float for simplicity right now
    price: float

    @classmethod
    def create(cls, name: str, category_id: UUID, description: str, price: float) -> "Product":
        return cls(
            id=str(uuid4()),
            name=name,
            category_id=category_id,
            description=description,
            price=price,
        )


@dataclass
class ProductCategory:
    id: UUID
    name: str
    description: str

    @classmethod
    def create(cls, name: str, description: str) -> "ProductCategory":
        return cls(
            id=str(uuid4()),
            name=name,
            description=description,
        )
