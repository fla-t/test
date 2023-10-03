from dataclasses import dataclass
from uuid import uuid4


@dataclass
class SKU:
    id: str
    name: str
    description: str

    @classmethod
    def create(cls, name: str, description: str) -> "SKU":
        return cls(id=str(uuid4()), name=name, description=description)
