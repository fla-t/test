from dataclasses import dataclass

from services.catalog.domain import models as mdl
from services.catalog.entrypoint.unit_of_work import DBPoolUnitOfWork


@dataclass(frozen=True)
class CategoryDTO:
    id: str
    name: str

    @classmethod
    def from_domain_model(cls, category: mdl.Category):
        return cls(category.id, category.name)


@dataclass(frozen=True)
class SkuDTO:
    id: str
    category_id: str
    name: str
    description: str

    @classmethod
    def from_domain_model(cls, sku: mdl.Sku):
        return cls(sku.id, sku.category_id, sku.name, sku.description)


def skus_by_ids(uow: DBPoolUnitOfWork, sku_ids: list[str]) -> list[SkuDTO]:
    with uow:
        skus = uow.skus.get(sku_ids)
        return [SkuDTO.from_domain_model(sku) for sku in skus]


def category_by_ids(uow: DBPoolUnitOfWork, category_ids: list[str]) -> list[CategoryDTO]:
    with uow:
        categories = uow.categories.get(category_ids)
        return [CategoryDTO.from_domain_model(categories) for categories in categories]


def skus_by_categories(uow: DBPoolUnitOfWork, category_ids: list[str]) -> list[SkuDTO]:
    with uow:
        skus = uow.skus.get_by_categories(category_ids)
        return [SkuDTO.from_domain_model(sku) for sku in skus]
