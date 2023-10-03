from dataclasses import dataclass
from datetime import date
from typing import List, Optional

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
    uow: uow.DBPoolUnitOfWork, time_period: str, start: date, end: Optional[date] = None
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
        where date_trunc('{time_period}', created_at at time zone 'utc') between %(start)s and %(end)s
        group by date_trunc('{time_period}', created_at at time zone 'utc')
        order by date_trunc('{time_period}', created_at at time zone 'utc') asc
        ;
    """

    with uow, uow.db_pool.dict_cursor() as curs:
        curs.execute(sql, {"start": start, "end": end, "time_period": time_period})
        rows = curs.fetchall()

    return [SalesByTimePeriod(period=row["date"].date(), sales=row["sales"]) for row in rows]
