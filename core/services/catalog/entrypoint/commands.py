from services.catalog.domain.models import SKU, Category
from services.catalog.entrypoint.unit_of_work import AbstractUnitOfWork


def create_sku(uow: AbstractUnitOfWork, category_id: str, name: str, description: str) -> str:
    with uow:
        sku = SKU.create(category_id, name, description)
        uow.skus.save([sku])

    return sku.id


def update_sku(
    uow: AbstractUnitOfWork, sku_id: str, category_id: str, name: str, description: str
) -> str:
    with uow:
        sku = SKU(sku_id, category_id, name, description)
        uow.skus.save([sku])

    return sku.id


def create_category(uow: AbstractUnitOfWork, name: str) -> str:
    with uow:
        category = Category.create(name)
        uow.categories.save([category])

    return category.id


def update_category(uow: AbstractUnitOfWork, category_id: str, name: str) -> str:
    with uow:
        category = Category(id=category_id, name=name)
        uow.categories.save([category])

    return category.id
