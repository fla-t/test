from services.catalog.domain.models import SKU
from services.catalog.entrypoint.unit_of_work import AbstractUnitOfWork


def create_sku(uow: AbstractUnitOfWork, name: str, description: str) -> str:
    with uow:
        sku = SKU.create(name, description)
        uow.skus.save([sku])

    return sku.id


def update_sku(uow: AbstractUnitOfWork, sku_id: str, name: str, description: str) -> str:
    with uow:
        sku = SKU(sku_id, name, description)
        uow.skus.save([sku])

    return sku.id
