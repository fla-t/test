from uuid import UUID

import pytest

from src.uow.inmemory import InMemoryUnitOfWork
from src.services.product.service import ProductService
from src.domain.product.models import Product, ProductCategory


@pytest.mark.asyncio
async def test_get_products_initially_empty():
    uow = InMemoryUnitOfWork()
    service = ProductService(uow)

    products = await service.get_products()
    assert products == []


@pytest.mark.asyncio
async def test_create_and_get_product():
    uow = InMemoryUnitOfWork()
    service = ProductService(uow)

    # first create a category
    cat = await service.add_category(name="Beverages", description="Drinks")
    assert isinstance(cat, ProductCategory)

    # create a product
    prod = await service.create_product(
        name="Coffee",
        category_id=cat.id,
        description="Ground coffee beans",
        price=3.50,
    )

    # returned id should be a valid UUID
    UUID(prod.id)
    assert prod.name == "Coffee"
    assert prod.category_id == cat.id

    # fetch it back
    fetched = await service.get_product(prod.id)
    assert isinstance(fetched, Product)
    assert fetched.id == prod.id
    assert fetched.name == "Coffee"
    assert fetched.description == "Ground coffee beans"
    assert fetched.price == pytest.approx(3.50)


@pytest.mark.asyncio
async def test_get_products_after_creations():
    uow = InMemoryUnitOfWork()
    service = ProductService(uow)

    # add two categories and products
    c1 = await service.add_category("Cat A", "desc A")
    p1 = await service.create_product("P1", c1.id, "d1", 1.0)
    c2 = await service.add_category("Cat B", "desc B")
    p2 = await service.create_product("P2", c2.id, "d2", 2.0)

    all_products = await service.get_products()
    # both products present, order not guaranteed
    ids = {p.id for p in all_products}
    assert ids == {p1.id, p2.id}


@pytest.mark.asyncio
async def test_update_product():
    uow = InMemoryUnitOfWork()
    service = ProductService(uow)

    cat = await service.add_category("Widgets", "Various widgets")
    prod = await service.create_product("Widget", cat.id, "small widget", 5.0)

    # mutate domain object
    prod.name = "Super Widget"
    prod.description = "upgraded"
    prod.price = 7.5

    updated = await service.update_product(prod)
    assert updated.id == prod.id
    assert updated.name == "Super Widget"
    assert updated.description == "upgraded"
    assert updated.price == pytest.approx(7.5)

    # double check via get
    fetched = await service.get_product(prod.id)
    assert fetched.name == "Super Widget"


@pytest.mark.asyncio
async def test_delete_product():
    uow = InMemoryUnitOfWork()
    service = ProductService(uow)

    cat = await service.add_category("Tools", "Hand tools")
    prod = await service.create_product("Hammer", cat.id, "steel hammer", 10.0)

    # ensure it's there
    assert await service.get_product(prod.id) is not None

    await service.delete_product(prod.id)
    # now it should be gone
    assert await service.get_product(prod.id) is None


@pytest.mark.asyncio
async def test_category_endpoints():
    uow = InMemoryUnitOfWork()
    service = ProductService(uow)

    # start empty
    cats = await service.get_categories()
    assert cats == []

    # add two
    c1 = await service.add_category("Alpha", "first")
    c2 = await service.add_category("Beta", "second")

    cats = await service.get_categories()
    names = {c.name for c in cats}
    assert names == {"Alpha", "Beta"}

    # fetch each by id
    got1 = await service.get_category(c1.id)
    assert got1 and got1.name == "Alpha"
    got2 = await service.get_category(c2.id)
    assert got2 and got2.description == "second"
