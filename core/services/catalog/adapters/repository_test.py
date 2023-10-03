# mypy: ignore-errors
# type: ignore
from uuid import uuid4

import pytest
from services.catalog.domain.models import SKU
from services.catalog.entrypoint import unit_of_work as uow


class TestSKURepo:
    def setup_method(self):
        self.args = {
            "id": str(uuid4()),
            "name": "test_name",
            "description": "test_description",
        }

    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_get(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            skus = [SKU(**self.args)]

            uow.skus.save([SKU(**self.args)])
            res = uow.skus.get([self.args["id"]])

            assert res == skus

    @pytest.mark.parametrize("selected_uow", ["fake_uow", "db_uow"], indirect=["selected_uow"])
    def test_save(self, selected_uow: uow.AbstractUnitOfWork):
        with selected_uow as uow:
            sku = SKU(**self.args)

            uow.skus.save([sku])
            assert uow.skus.get([self.args["id"]]) == [sku]

        # small change
        sku.name = "Someother name"

        with selected_uow as uow:
            uow.skus.save([sku])
            assert uow.skus.get([self.args["id"]]) == [sku]
