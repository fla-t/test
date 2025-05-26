import pytest
from fastapi.testclient import TestClient

from src.entrypoint.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_categories_endpoints(database_creation, client: TestClient):
    resp = client.post(
        "/categories",
        json={
            "name": "Electronics",
            "description": "Devices and gadgets",
        },
    )
    assert resp.status_code == 200
    cat = resp.json()

    assert cat["name"] == "Electronics"
    assert cat["description"] == "Devices and gadgets"

    # fetch
    resp = client.get("/categories")
    assert resp.status_code == 200
    cats = resp.json()

    assert any(c["id"] == cat["id"] for c in cats)

    # fetch
    id = cat["id"]
    resp = client.get(f"/categories/{id}")
    assert resp.status_code == 200
    cat = resp.json()

    assert cat["id"] == id


def test_products_endpoints(database_creation, client: TestClient):
    # first create a category
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
    assert resp.status_code == 200
    product = resp.json()
    assert product["name"] == "Smartphone"
    assert product["category_id"] == cat["id"]
    assert product["description"] == "Latest model smartphone"
    assert product["price"] == 699.99
    assert product["id"] is not None

    # fetch all products
    resp = client.get("/products")
    assert resp.status_code == 200
    products = resp.json()
    assert any(p["id"] == product["id"] for p in products)

    # fetch a product by ID
    id = product["id"]
    resp = client.get(f"/products/{id}")
    assert resp.status_code == 200
    product = resp.json()
    assert product["id"] == id
    assert product["name"] == "Smartphone"
    assert product["category_id"] == cat["id"]
    assert product["description"] == "Latest model smartphone"
    assert product["price"] == 699.99

    # update the product
    resp = client.put(
        f"/products/{id}",
        json={
            "name": "Smartphone Pro",
            "category_id": cat["id"],
            "description": "Latest model smartphone with advanced features",
            "price": 899.99,
        },
    )
    assert resp.status_code == 200
    updated_product = resp.json()
    assert updated_product["id"] == id
    assert updated_product["name"] == "Smartphone Pro"
    assert updated_product["category_id"] == cat["id"]
    assert updated_product["description"] == "Latest model smartphone with advanced features"
    assert updated_product["price"] == 899.99

    # delete the product
    resp = client.delete(f"/products/{id}")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Product deleted successfully"}

    # verify deletion
    resp = client.get(f"/products/{id}")
    assert resp.status_code == 404
    assert resp.json() == {"status": "error", "message": "Product not found"}
