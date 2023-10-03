from dataclasses import dataclass
from uuid import uuid4


@dataclass
class Category:
    id: str
    name: str

    @classmethod
    def create(cls, name: str) -> "Category":
        return cls(id=str(uuid4()), name=name)


@dataclass
class Sku:
    id: str
    category_id: str
    name: str
    description: str

    @classmethod
    def create(cls, cat_id: str, name: str, description: str) -> "Sku":
        return cls(id=str(uuid4()), category_id=cat_id, name=name, description=description)
