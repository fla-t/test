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


@dataclass
class ProductCategory:
    id: UUID
    name: str
    description: str
