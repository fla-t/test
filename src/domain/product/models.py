from dataclasses import dataclass

UUID = str


@dataclass
class Product:
    id: UUID
    name: str
    catagory: UUID
    description: str
    price: float


@dataclass
class ProductCategory:
    id: UUID
    name: str
    description: str
