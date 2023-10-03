from dataclasses import dataclass
from typing import List

from services.inventory.entrypoint.unit_of_work import DBPoolUnitOfWork


@dataclass
class SkuInventoryDTO:
    sku_id: str
    quantity: int


def inventory_by_skus(uow: DBPoolUnitOfWork, sku_ids: List[str]) -> List[SkuInventoryDTO]:
    """
    Remember our domain object? inventory log, this is the read side of that aggregate.

    Now we will compressed all of those logs that we created to make ourself a inventory view.
    """

    sql = """
        select
            sku_id,
            sum(quantity_changed) as quantity
        from inventory_logs
        where (%(sku_ids)s is null or sku_id = any(%(sku_ids)s::uuid[]))
        group by sku_id
        ;
    """

    with uow, uow.db_pool.dict_cursor() as curs:
        curs.execute(sql, {"sku_ids": sku_ids})
        rows = curs.fetchall()

    return [SkuInventoryDTO(sku_id=row["sku_id"], quantity=row["quantity"]) for row in rows]


def inventory_below_threshold(uow: DBPoolUnitOfWork, threshold: int) -> List[SkuInventoryDTO]:
    sql = """
        select
            sku_id,
            sum(quantity_changed) as quantity
        from inventory_logs
        group by sku_id
        having sum(quantity_changed) < %(threshold)s
        ;
    """

    with uow, uow.db_pool.dict_cursor() as curs:
        curs.execute(sql, {"threshold": threshold})
        rows = curs.fetchall()

    return [SkuInventoryDTO(sku_id=row["sku_id"], quantity=row["quantity"]) for row in rows]
