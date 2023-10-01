from uuid import uuid4

import pytest
from services.inventory.domain.models import SKU
from services.inventory.entrypoint import unit_of_work as uow


class TestSKURepo:
    def setup_method(self):
        self.args = {
            "id": str(uuid4()),
            "name": "test_name",
            "description": "test_description",
        }

    @pytest.mark.parametrize("selected_uow", ["db_uow"], indirect=["selected_uow"])
    def test_get(self, selected_uow: uow.AbstractUnitOfWork):
        # run test with both fake and db to check their behavior perfectly matches
        with selected_uow as uow:
            skus = [SKU(**self.args)]

            uow.skus.save([SKU(**self.args)])
            res = uow.skus.get([self.args["id"]])

            assert res == skus
