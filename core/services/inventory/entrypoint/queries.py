from dataclasses import dataclass
from typing import List

from services.inventory.entrypoint import anti_corruption as acl
from services.inventory.entrypoint.unit_of_work import DBPoolUnitOfWork


@dataclass
class SkuInventoryDTO:
    id: str
    name: str
    quantity: int


def inventory_by_skus(
    uow: DBPoolUnitOfWork,
    cat_svc: acl.AbstractCatalogService,
    sku_ids: List[str],
) -> List[SkuInventoryDTO]:
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

    acl_sku_dict = {sku.id: sku for sku in cat_svc.get_skus(list(sku_ids))}

    return [
        SkuInventoryDTO(
            id=row["sku_id"],
            name=acl_sku_dict[row["sku_id"]].name,
            quantity=row["quantity"],
        )
        for row in rows
    ]


def inventory_below_threshold(
    uow: DBPoolUnitOfWork,
    cat_svc: acl.AbstractCatalogService,
    threshold: int,
) -> List[SkuInventoryDTO]:
    sql = """
        select
            sku_id,
            sum(quantity_changed) as quantity
        from inventory_logs
        group by sku_id
        having sum(quantity_changed) <= %(threshold)s
        ;
    """

    with uow, uow.db_pool.dict_cursor() as curs:
        curs.execute(sql, {"threshold": threshold})
        rows = curs.fetchall()

    # set to avoid duplication
    sku_ids = {row["sku_id"] for row in rows}
    acl_sku_dict = {sku.id: sku for sku in cat_svc.get_skus(list(sku_ids))}

    return [
        SkuInventoryDTO(
            id=row["sku_id"],
            name=acl_sku_dict[row["sku_id"]].name,
            quantity=row["quantity"],
        )
        for row in rows
    ]
