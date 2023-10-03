from abc import ABC, abstractmethod
from copy import deepcopy
from typing import List

from database.db_pool import DBPool
from psycopg2.extensions import cursor as pg_cursor
from psycopg2.extras import DictCursor, execute_values
from services.inventory.domain.models import InventoryLog


class AbstractInventoryLogsRepo(ABC):
    """Abstract repo for persisting inventory logs in the Database"""

    @abstractmethod
    def add(self, inventory_logs: List[InventoryLog]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, inventory_log_ids: List[str]) -> List[InventoryLog]:
        raise NotImplementedError


class FakeInventoryLogsRepo(AbstractInventoryLogsRepo):
    def __init__(self):
        self.inventory_logs: List[InventoryLog] = []

    def add(self, inventory_logs: List[InventoryLog]) -> None:
        for il in inventory_logs:
            self.inventory_logs.append(deepcopy(il))

    def get(self, inventory_log_ids: List[str]) -> List[InventoryLog]:
        to_return = []
        for il in self.inventory_logs:
            if il.id in inventory_log_ids:
                to_return.append(deepcopy(il))

        return to_return


class InventoryLogsRepo(AbstractInventoryLogsRepo):
    def __init__(self, db_pool: DBPool):
        super().__init__()
        self.db_pool = db_pool

    def cursor(self, *args, **kwargs) -> pg_cursor:
        return self.db_pool.cursor(*args, **kwargs)

    def read_cursor(self) -> pg_cursor:
        return self.cursor(cursor_factory=DictCursor)

    def add(self, inventory_logs: List[InventoryLog]) -> None:
        sql = """
            insert into inventory_logs (
                id, sku_id, quantity_changed
            )
            values %s
            ;
        """
        args = []
        for il in inventory_logs:
            args.append((il.id, il.sku_id, il.quantity_changed))

        with self.cursor() as curs:
            execute_values(curs, sql, args)

    def get(self, inventory_logs: List[str]) -> List[InventoryLog]:
        sql = """
            select
                id,
                sku_id,
                quantity_changed
            from inventory_logs
            where id = any(%s::uuid[])
            ;
        """
        with self.read_cursor() as curs:
            curs.execute(sql, [inventory_logs])
            rows = curs.fetchall()

        return [
            InventoryLog(
                id=row["id"], sku_id=row["sku_id"], quantity_changed=row["quantity_changed"]
            )
            for row in rows
        ]
