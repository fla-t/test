from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from services.sales.entrypoint import anti_corruption as acl
from services.sales.entrypoint import unit_of_work as uow


@dataclass
class SalesByTimePeriod:
    period: date
    sales: int


@dataclass
class SalesComparisonByTimePeriod:
    period: date
    revenue_a: int
    revenue_b: int


def sales_by_time_period(
    uow: uow.DBPoolUnitOfWork,
    time_period: str,
    start: date,
    end: Optional[date] = None,
    # this is so that the function is generic, see sales_by_sku and sales_by_category below
    inventory_log_ids: Optional[List[str]] = None,
) -> List[SalesByTimePeriod]:
    """Gets the revenue by day for a date range"""

    if end is None:
        end = start

    if time_period not in ("day", "week", "month", "year"):
        raise ValueError(f"Invalid time_period: {time_period}")

    sql = f"""
        select
            date_trunc('{time_period}', (created_at at time zone 'utc')) as date,
            sum(price) as sales
        from sales
        where
            date_trunc('{time_period}', created_at at time zone 'utc') between %(start)s and %(end)s
            and (%(il_ids)s is null or inventory_log_id = any(%(il_ids)s::uuid[]))
        group by date_trunc('{time_period}', created_at at time zone 'utc')
        order by date_trunc('{time_period}', created_at at time zone 'utc') asc
        ;
    """

    with uow, uow.db_pool.dict_cursor() as curs:
        curs.execute(
            sql,
            {"start": start, "end": end, "time_period": time_period, "il_ids": inventory_log_ids},
        )
        rows = curs.fetchall()

    return [SalesByTimePeriod(period=row["date"].date(), sales=row["sales"]) for row in rows]


def sales_by_sku(
    uow: uow.DBPoolUnitOfWork,
    inv_svc: acl.AbstractInventoryService,
    sku_id: str,
    time_period: str,
    start: date,
    end: Optional[date] = None,
) -> List[SalesByTimePeriod]:
    """Gets the sales by sku by using a acl to get information from the inventory service"""

    inventory_log_ids = inv_svc.inventory_log_ids_by_sku(sku_id)
    sales = sales_by_time_period(
        uow,
        time_period=time_period,
        start=start,
        end=end,
        inventory_log_ids=inventory_log_ids,
    )

    return sales


def sales_by_category(
    uow: uow.DBPoolUnitOfWork,
    inv_svc: acl.AbstractInventoryService,
    cat_svc: acl.AbstractCatalogService,
    cat_id: str,
    time_period: str,
    start: date,
    end: Optional[date] = None,
) -> List[SalesByTimePeriod]:
    """Gets the sales by sku by using a acl to get information from the inventory service"""

    sku_ids = cat_svc.sku_ids_by_category(cat_id)
    inventory_log_ids = inv_svc.inventory_log_ids_by_sku(sku_ids)
    sales = sales_by_time_period(
        uow,
        time_period=time_period,
        start=start,
        end=end,
        inventory_log_ids=inventory_log_ids,
    )

    return sales
