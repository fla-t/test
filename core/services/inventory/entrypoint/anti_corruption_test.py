from uuid import uuid4

from services.inventory.entrypoint import anti_corruption as acl


def test_get_skus(fake_cat_service: acl.FakeCatalogService):
    skus = [
        acl.Sku(id=str(uuid4()), name="acl_sku_1"),
        acl.Sku(id=str(uuid4()), name="acl_sku_2"),
        acl.Sku(id=str(uuid4()), name="acl_sku_3"),
    ]

    fake_cat_service.add_skus(skus)

    res = fake_cat_service.get_skus([sku.id for sku in skus])
    assert res == skus
