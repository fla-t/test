from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Dict, List

from database.db_pool import DBPool
from psycopg2.extensions import cursor as pg_cursor
from psycopg2.extras import DictCursor, execute_values
from services.catalog.domain.models import Category, Sku


class AbstractCategoryRepo(ABC):
    """Abstract repo for persisting Categories in the Database"""

    @abstractmethod
    def save(self, categories: List[Category]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, category_ids: List[str]) -> List[Dict]:
        raise NotImplementedError


class FakeCategoryRepo(AbstractCategoryRepo):
    def __init__(self) -> None:
        self.categories: Dict[str, Category] = {}

    def save(self, categories: List[Category]) -> None:
        for category in categories:
            self.categories[category.id] = deepcopy(category)

    def get(self, category_ids: List[str]) -> List[Category]:
        return [self.categories[category_id] for category_id in category_ids]


class CategoryRepo(AbstractCategoryRepo):
    def __init__(self, db_pool: DBPool):
        super().__init__()
        self.db_pool = db_pool

    def cursor(self, *args, **kwargs) -> pg_cursor:
        return self.db_pool.cursor(*args, **kwargs)

    def read_cursor(self) -> pg_cursor:
        return self.cursor(cursor_factory=DictCursor)

    def save(self, categories: List[Category]) -> None:
        sql = """
            insert into categories (id, name)
            values %s
            on conflict (id) do update
            set name = excluded.name
            ;
        """

        args = []
        for category in categories:
            args.append((category.id, category.name))

        with self.cursor() as curs:
            execute_values(curs, sql, args)

    def get(self, category_ids: List[str]) -> List[Category]:
        sql = """
            select
                id,
                name
            from categories
            where id = any(%s::uuid[])
            ;
        """

        with self.read_cursor() as curs:
            curs.execute(sql, [category_ids])
            rows = curs.fetchall()

        return [
            Category(
                id=row["id"],
                name=row["name"],
            )
            for row in rows
        ]


class AbstractSKURepo(ABC):
    """Abstract repo for persisting SKUs in the Database"""

    @abstractmethod
    def save(self, skus: List[Sku]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, sku_ids: List[str]) -> List[Sku]:
        raise NotImplementedError

    @abstractmethod
    def get_by_categories(self, category_ids: List[str]) -> List[Sku]:
        raise NotImplementedError


class FakeSKURepo(AbstractSKURepo):
    """Fake repo that is used for testing"""

    def __init__(self) -> None:
        self.skus: Dict[str, Sku] = {}

    def save(self, skus: List[Sku]) -> None:
        for sku in skus:
            self.skus[sku.id] = deepcopy(sku)

    def get(self, sku_ids: List[str]) -> List[Sku]:
        return [self.skus[sku_id] for sku_id in sku_ids]

    def get_by_categories(self, category_ids: List[str]) -> List[Sku]:
        return [sku for sku in self.skus.values() if sku.category_id in category_ids]


class SKURepo(AbstractSKURepo):
    """Actual repo that connects with the database and stores our skus"""

    def __init__(self, db_pool: DBPool):
        super().__init__()
        self.db_pool = db_pool

    def cursor(self, *args, **kwargs) -> pg_cursor:
        return self.db_pool.cursor(*args, **kwargs)

    def read_cursor(self) -> pg_cursor:
        return self.cursor(cursor_factory=DictCursor)

    def save(self, skus: List[Sku]) -> None:
        sql = """
            insert into skus (id, category_id, name, description)
            values %s
            on conflict (id) do update
            set
                category_id = excluded.category_id,
                name = excluded.name,
                description = excluded.description
            ;
        """

        args = []
        for sku in skus:
            args.append((sku.id, sku.category_id, sku.name, sku.description))

        with self.cursor() as curs:
            execute_values(curs, sql, args)

    def get(self, sku_ids: List[str]) -> List[Sku]:
        sql = """
            select
                id,
                category_id,
                name,
                description
            from skus
            where id = any(%s::uuid[])
            ;
        """
        with self.read_cursor() as curs:
            curs.execute(sql, [sku_ids])
            rows = curs.fetchall()

        return [
            Sku(
                id=row["id"],
                category_id=row["category_id"],
                name=row["name"],
                description=row["description"],
            )
            for row in rows
        ]

    def get_by_categories(self, category_ids: List[str]) -> List[Sku]:
        sql = """
            select
                id,
                category_id,
                name,
                description
            from skus
            where category_id = any(%s::uuid[])
            ;
        """
        with self.read_cursor() as curs:
            curs.execute(sql, [category_ids])
            rows = curs.fetchall()

        return [
            Sku(
                id=row["id"],
                category_id=row["category_id"],
                name=row["name"],
                description=row["description"],
            )
            for row in rows
        ]
