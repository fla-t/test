import pytest
from fastapi.testclient import TestClient

from src.entrypoint.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_current_inventory_for_product(database_creation, client: TestClient):
    # create a category
    resp = client.post(
        "/categories",
        json={
            "name": "Electronics",
            "description": "Devices and gadgets",
        },
    )
    assert resp.status_code == 200
    cat = resp.json()

    # create a product
    resp = client.post(
        "/products",
        json={
            "name": "Smartphone",
            "category_id": cat["id"],
            "description": "Latest model smartphone",
            "price": 699.99,
        },
    )

    # update inventory for the product
    product = resp.json()
    resp = client.post(
        "/inventory/update",
        json={
            "product_id": product["id"],
            "quantity": 50,
        },
    )
    assert resp.status_code == 200
    inventory_item = resp.json()
    assert inventory_item["product_id"] == product["id"]
    assert inventory_item["quantity"] == 50

    # check if the inventory was updated
    resp = client.get(f"/inventory/current/{product['id']}")
    assert resp.status_code == 200
    inventory_item = resp.json()
    assert inventory_item["product_id"] == product["id"]
    assert inventory_item["quantity"] == 50
