# tests/test_sales_api.py
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from src.entrypoint.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def seed_product(database_creation, client: TestClient) -> int:
    # 1) create a category
    resp = client.post(
        "/categories",
        json={"name": "TestCat", "description": "for sales tests"},
    )
    assert resp.status_code == 200
    cat = resp.json()

    # 2) create a product
    resp = client.post(
        "/products",
        json={
            "name": "TestProduct",
            "category_id": cat["id"],
            "description": "desc",
            "price": 42.0,
        },
    )
    assert resp.status_code == 200
    return resp.json()


def test_create_and_list_sales(database_creation, client: TestClient, seed_product):
    # create a sale
    payload = {
        "product_id": seed_product["id"],
        "quantity": 3,
        "total_price": seed_product["price"] * 3,
    }
    resp = client.post("/sales/", json=payload)
    assert resp.status_code == 201
    sale = resp.json()
    assert sale["product_id"] == seed_product["id"]
    assert sale["quantity"] == 3
    assert sale["total_price"] == pytest.approx(126.0)

    # list all sales (no filters)
    resp = client.get("/sales/between-dates")
    assert resp.status_code == 200
    all_sales = resp.json()
    assert any(s["product_id"] == seed_product["id"] and s["quantity"] == 3 for s in all_sales)


def test_get_sales_between_dates(database_creation, client: TestClient, seed_product):
    # make two sales, one "yesterday", one "today"
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)

    # sale for yesterday
    with patch("src.domain.sales.models.datetime") as mock_datetime:
        mock_datetime.now.return_value = yesterday
        resp1 = client.post(
            "/sales/",
            json={
                "product_id": seed_product["id"],
                "quantity": 1,
                "total_price": seed_product["price"],
            },
        )
        assert resp1.status_code == 201

    # sale for today
    resp2 = client.post(
        "/sales/",
        json={
            "product_id": seed_product["id"],
            "quantity": 2,
            "total_price": seed_product["price"] * 2,
        },
    )
    assert resp2.status_code == 201

    # filter just "yesterday"
    start = yesterday
    end = yesterday + timedelta(hours=1)
    resp = client.get(
        f"/sales/between-dates",
        params={"start_date": start.isoformat(), "end_date": end.isoformat()},
    )
    assert resp.status_code == 200
    sales = resp.json()

    # should include the first sale but not the second
    assert any(s["quantity"] == 1 for s in sales)
    assert all(s["quantity"] != 2 for s in sales)

    # filter just "today"
    start = now
    end = now + timedelta(hours=1)
    resp = client.get(
        f"/sales/between-dates",
        params={"start_date": start.isoformat(), "end_date": end.isoformat()},
    )
    assert resp.status_code == 200
    sales = resp.json()

    assert any(s["quantity"] == 2 for s in sales)
    assert all(s["quantity"] != 1 for s in sales)


def test_compare_sales(database_creation, client: TestClient, seed_product):
    # seed one sale yesterday and one sale today
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)

    # yesterday: quantity=5, total=5*price
    with patch("src.domain.sales.models.datetime") as mock_datetime:
        mock_datetime.now.return_value = yesterday
        client.post(
            "/sales/",
            json={
                "product_id": seed_product["id"],
                "quantity": 5,
                "total_price": seed_product["price"] * 5,
            },
        )

    # today: quantity=7, total=7*price
    client.post(
        "/sales/",
        json={
            "product_id": seed_product["id"],
            "quantity": 7,
            "total_price": seed_product["price"] * 7,
        },
    )

    first_start = yesterday
    first_end = yesterday + timedelta(hours=1)
    second_start = now
    second_end = now + timedelta(hours=1)

    resp = client.get(
        "/sales/compare",
        params={
            "first_start": first_start.isoformat(),
            "first_end": first_end.isoformat(),
            "second_start": second_start.isoformat(),
            "second_end": second_end.isoformat(),
        },
    )
    assert resp.status_code == 200

    comparison = resp.json()
    assert "first_total" in comparison[0]
    assert "second_total" in comparison[0]

    assert comparison[0]["first_total"] == pytest.approx(seed_product["price"] * 5)
    assert comparison[0]["second_total"] == pytest.approx(seed_product["price"] * 7)
