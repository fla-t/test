from abc import ABC
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, List

from services.catalog.domain.models import Sku as CatSku
from services.catalog.entrypoint import queries as cat_queries
from services.catalog.entrypoint import unit_of_work as cat_uow


# only add what you want
@dataclass
class Sku:
    id: str
    name: str

    @classmethod
    def from_outer_domain_object(cls, cat_sku: CatSku) -> "Sku":
        return cls(id=cat_sku.id, name=cat_sku.name)


class AbstractCatalogService(ABC):
    def get_skus(self, sku_ids: List[str]) -> List[Sku]:
        raise NotImplementedError


class FakeCatalogService(AbstractCatalogService):
    def __init__(self) -> None:
        super().__init__()
        self.skus: Dict[str, Sku] = {}

    def get_skus(self, sku_ids: List[str]) -> List[Sku]:
        return [self.skus[sku_id] for sku_id in sku_ids]

    def add_skus(self, skus: List[Sku]) -> None:
        for sku in skus:
            self.skus[sku.id] = deepcopy(sku)


class CatalogService(AbstractCatalogService):
    def get_skus(self, sku_ids: List[str]) -> List[Sku]:
        _cat_uow = cat_uow.DBPoolUnitOfWork()
        cat_skus = cat_queries.skus_by_ids(_cat_uow, sku_ids)
        return [Sku.from_outer_domain_object(cat_sku) for cat_sku in cat_skus]
