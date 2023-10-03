from services.sales.entrypoint import anti_corruption as acl


def test_get_by_skus(fake_inv_service: acl.FakeInventoryService):
    fake_inv_service.add_inventory_log_to_sku_id("sku_1", ["inv_log_1"])
    fake_inv_service.add_inventory_log_to_sku_id("sku_2", ["inv_log_2"])
    fake_inv_service.add_inventory_log_to_sku_id("sku_2", ["inv_log_3"])

    res = fake_inv_service.inventory_log_ids_by_sku(["sku_1"])
    assert res == ["inv_log_1"]

    res = fake_inv_service.inventory_log_ids_by_sku(["sku_2"])
    assert res == ["inv_log_2", "inv_log_3"]


def test_sku_ids_by_category(fake_cat_service: acl.FakeCatalogService):
    fake_cat_service.add_skus("cat_1", ["sku_1"])
    res = fake_cat_service.sku_ids_by_category("cat_1")
    assert res == ["sku_1"]

    fake_cat_service.add_skus("cat_1", ["sku_2"])
    res = fake_cat_service.sku_ids_by_category("cat_1")
    assert res == ["sku_1", "sku_2"]
