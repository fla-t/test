from dataclasses import dataclass
from datetime import date
from typing import List

from services.sales.entrypoint import unit_of_work as uow


@dataclass
class SalesByTimePeriod:
    period: date
    revenue: int


@dataclass
class SalesComparisonByTimePeriod:
    period: date
    revenue_a: int
    revenue_b: int


def sales_by_time_period(
    uow: uow.DBPoolUnitOfWork, start: date, end: date, time_period: str
) -> List[SalesByTimePeriod]:
    """Gets the revenue by day for a date range"""

    if time_period not in ("day", "week", "month", "year"):
        raise ValueError(f"Invalid time_period: {time_period}")

    sql = f"""
        select
            date_trunc('{time_period}', (created_at at time zone 'utc')) as day,
            sum(price) as revenue
        from sales
        where (created_at at time zone 'utc') between %(start)s and %(end)s
        group by date_trunc('{time_period}', created_at at time zone 'utc')
        order by date_trunc('{time_period}', created_at at time zone 'utc') asc
        ;
    """

    with uow, uow.db_pool.dict_cursor() as curs:
        curs.execute(sql, {"start": start, "end": end, "time_period": time_period})
        rows = curs.fetchall()

    return [SalesByTimePeriod(period=row["day"], revenue=row["revenue"]) for row in rows]
