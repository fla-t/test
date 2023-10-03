# mypy: ignore-errors
# type: ignore
from uuid import uuid4

import pytest
from services.catalog.domain.models import Category, Sku
from services.catalog.entrypoint import unit_of_work as uow


class TestCategoryRepo:
    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_get(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            categories = [Category.create("fresh"), Category.create("frozen")]
            uow.categories.save(categories)

            assert uow.categories.get([categories[0].id, categories[1].id]) == categories

    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_save(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            category = Category.create("fresh")
            uow.categories.save([category])

            assert uow.categories.get([category.id]) == [category]

        # small change
        category.name = "fresh-vegetable"

        with selected_uow as uow:
            uow.categories.save([category])
            assert uow.categories.get([category.id]) == [category]


@pytest.mark.usefixtures("drop_skus_fk")
class TestSKURepo:
    def setup_method(self):
        self.args = {
            "id": str(uuid4()),
            "category_id": str(uuid4()),
            "name": "test_name",
            "description": "test_description",
        }

    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_get(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            skus = [Sku(**self.args)]

            uow.skus.save([Sku(**self.args)])
            res = uow.skus.get([self.args["id"]])

            assert res == skus

    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_get_by_categories(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            skus = [Sku(**self.args)]

            uow.skus.save([Sku(**self.args)])
            res = uow.skus.get_by_categories([self.args["category_id"]])

            assert res == skus

    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_save(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            sku = Sku(**self.args)

            uow.skus.save([sku])
            assert uow.skus.get([self.args["id"]]) == [sku]

        # small change
        sku.name = "Someother name"

        with selected_uow as uow:
            uow.skus.save([sku])
            assert uow.skus.get([self.args["id"]]) == [sku]
