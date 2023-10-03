from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import date
from typing import List

from database.db_pool import DBPool
from psycopg2.extensions import cursor as pg_cursor
from psycopg2.extras import DictCursor, execute_values
from services.sales.domain.models import Sale


class AbstractSalesRepo(ABC):
    """Abstract repo for persisting Sales in the Database"""

    @abstractmethod
    def add(self, sales: List[Sale]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, sale_ids: List[str]) -> List[Sale]:
        raise NotImplementedError

    @abstractmethod
    def get_sales_by_date_range(self, start: date, end: date) -> List[Sale]:
        raise NotImplementedError


class FakeSalesRepo(AbstractSalesRepo):
    """Fake repo that is used for testing"""

    def __init__(self) -> None:
        super().__init__()
        self.sales: List[Sale] = []

    def add(self, sales: List[Sale]) -> None:
        self.sales.extend(deepcopy(sales))

    def get(self, sale_ids: List[str]) -> List[Sale]:
        return deepcopy([sale for sale in self.sales if sale.id in sale_ids])

    def get_sales_by_date_range(self, start: date, end: date) -> List[Sale]:
        return [sale for sale in self.sales if start <= sale.created_at.date() <= end]


class SalesRepo(AbstractSalesRepo):
    """Actual repo that connects with the database and stores our sales"""

    def __init__(self, db_pool: DBPool):
        super().__init__()
        self.db_pool = db_pool

    def cursor(self, *args, **kwargs) -> pg_cursor:
        return self.db_pool.cursor(*args, **kwargs)

    def read_cursor(self) -> pg_cursor:
        return self.cursor(cursor_factory=DictCursor)

    def add(self, sales: List[Sale]) -> None:
        sql = """
            insert into sales (id, inventory_log_id, price, created_at)
            values %s
            ;
        """
        args = []
        for sale in sales:
            args.append((sale.id, sale.inventory_log_id, sale.price, sale.created_at))

        with self.cursor() as curs:
            execute_values(curs, sql, args)

    def get(self, sale_ids: List[str]) -> List[Sale]:
        sql = """
            select
                id,
                inventory_log_id,
                price,
                created_at
            from sales
            where id = any(%s::uuid[])
            ;
        """

        with self.read_cursor() as curs:
            curs.execute(sql, [sale_ids])
            rows = curs.fetchall()

        return [
            Sale(
                id=row["id"],
                inventory_log_id=row["inventory_log_id"],
                price=row["price"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_sales_by_date_range(self, start: date, end: date) -> List[Sale]:
        sql = """
            select
                id,
                inventory_log_id,
                price,
                created_at
            from sales
            where created_at at time zone 'utc' between %s::date and %s::date
            order by created_at asc
            ;
        """

        with self.read_cursor() as curs:
            curs.execute(sql, [start, end])
            rows = curs.fetchall()

        return [
            Sale(
                id=row["id"],
                inventory_log_id=row["inventory_log_id"],
                price=row["price"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
