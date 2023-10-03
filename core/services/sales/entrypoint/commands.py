from services.sales.domain.models import Sale
from services.sales.entrypoint.unit_of_work import AbstractUnitOfWork


def register_sale(uow: AbstractUnitOfWork, inventory_log_id: str, price: int) -> str:
    with uow:
        sale = Sale.create(inventory_log_id, price)
        uow.sales.add([sale])

    return sale.id
