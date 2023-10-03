from abc import ABC
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, List

from services.catalog.domain.models import Sku as CatSku
from services.catalog.entrypoint import queries as cat_queries
from services.catalog.entrypoint import unit_of_work as cat_uow
from services.inventory.entrypoint import unit_of_work as inv_uow


class AbstractInventoryService(ABC):
    def inventory_log_ids_by_sku(self, sku_ids: List[str]) -> List[str]:
        raise NotImplementedError


class FakeInventoryService(AbstractInventoryService):
    def __init__(self) -> None:
        super().__init__()
        self.inventory_log_to_sku_id: Dict[str, str] = {}

    def add_inventory_log_to_sku_id(self, sku_id: str, inventory_log_id: str) -> None:
        self.inventory_log_to_sku_id[inventory_log_id] = sku_id

    def inventory_log_ids_by_sku(self, sku_ids: List[str]) -> List[str]:
        return [
            inventory_log_id
            for inventory_log_id, sku_id in self.inventory_log_to_sku_id.items()
            if sku_id in sku_ids
        ]


class InventoryService(AbstractInventoryService):
    def inventory_log_ids_by_sku(self, sku_id: str) -> List[str]:
        _inv_uow = inv_uow.DBPoolUnitOfWork()

        with _inv_uow:
            inventory_logs = _inv_uow.inventory_logs.get_by_skus(sku_id)

        return [inventory_log.id for inventory_log in inventory_logs]


class AbstractCatalogService(ABC):
    def sku_ids_by_category(self, cat_id: str) -> List[str]:
        raise NotImplementedError


class FakeCatalogService(AbstractCatalogService):
    def __init__(self) -> None:
        super().__init__()
        self.category_to_sku_ids: Dict[str, List[str]] = defaultdict(list)

    def sku_ids_by_category(self, cat_id: str) -> List[str]:
        return self.category_to_sku_ids[cat_id]

    def add_skus(self, cat_id: str, sku_ids: List[str]) -> None:
        self.category_to_sku_ids[cat_id].extend(sku_ids)


class CatalogService(AbstractCatalogService):
    def sku_ids_by_category(self, cat_id: str) -> List[str]:
        _cat_uow = cat_uow.DBPoolUnitOfWork()
        skus = cat_queries.skus_by_categories(_cat_uow, [cat_id])
        return [sku.id for sku in skus]
