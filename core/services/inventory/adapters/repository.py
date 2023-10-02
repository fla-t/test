from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Dict, List

from database.db_pool import DBPool
from psycopg2.extensions import cursor
from psycopg2.extras import DictCursor, execute_values
from services.inventory.domain.models import SKU, InventoryLog


class AbstractSKURepo(ABC):
    """Abstract repo for persisting SKUs in the Database"""

    @abstractmethod
    def save(self, skus: List[SKU]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, sku_ids: List[str]) -> List[SKU]:
        raise NotImplementedError


class FakeSKURepo(AbstractSKURepo):
    """Fake repo that is used for testing"""

    def __init__(self) -> None:
        self.skus: Dict[str, SKU] = {}

    def save(self, skus: List[SKU]) -> None:
        for sku in skus:
            self.skus[sku.id] = deepcopy(sku)

    def get(self, sku_ids: List[str]) -> List[SKU]:
        return [self.skus[sku_id] for sku_id in sku_ids]


class SKURepo(AbstractSKURepo):
    """Actual repo that connects with the database and stores our skus"""

    def __init__(self, db_pool: DBPool):
        super().__init__()
        self.db_pool = db_pool

    def cursor(self, *args, **kwargs) -> cursor:
        return self.db_pool.cursor(*args, **kwargs)

    def read_cursor(self):
        return self.cursor(cursor_factory=DictCursor)

    def save(self, skus: List[SKU]) -> None:
        sql = """
            insert into skus (
                id, name, description
            )
            values %s
            on conflict (id) do update
            set
                name = excluded.name,
                description = excluded.description
            ;
        """

        args = []
        for sku in skus:
            args.append((sku.id, sku.name, sku.description))

        with self.cursor() as curs:
            execute_values(curs, sql, args)

    def get(self, sku_ids: List[str]) -> List[SKU]:
        sql = """
            select
                id,
                name,
                description
            from skus
            where id = any(%s::uuid[])
            ;
        """
        with self.read_cursor() as curs:
            curs.execute(sql, [sku_ids])
            rows = curs.fetchall()

        return [SKU(id=row["id"], name=row["name"], description=row["description"]) for row in rows]


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

    def cursor(self, *args, **kwargs) -> cursor:
        return self.db_pool.cursor(*args, **kwargs)

    def read_cursor(self):
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
