import uuid
import pytest

from src.domain.product.models import Product, ProductCategory
from src.uow.sqlalchemy import SQLAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_add_and_get_category(database_creation):
    uow = SQLAlchemyUnitOfWork()

    category = ProductCategory(
        id=str(uuid.uuid4()),
        name="Mineral Water",
        description="Natural spring water",
    )

    # add
    async with uow:
        await uow.products.add_category(category)

    # fetch
    async with uow:
        fetched = await uow.products.get_category(category.id)

    assert fetched is not None
    assert fetched.id == category.id
    assert fetched.name == category.name
    assert fetched.description == category.description


@pytest.mark.asyncio
async def test_list_categories(database_creation):
    # prepare two categories
    cats = [
        ProductCategory(id=str(uuid.uuid4()), name=f"Cat {i}", description=f"Desc {i}")
        for i in (1, 2)
    ]
    uow = SQLAlchemyUnitOfWork()
    async with uow:
        for c in cats:
            await uow.products.add_category(c)

    async with uow:
        listed = await uow.products.get_categories()

    # order is not guaranteed, so compare sets of ids
    ids = {c.id for c in listed}
    assert ids == {c.id for c in cats}


@pytest.mark.asyncio
async def test_create_and_get_product(database_creation):
    # first create a category
    cat = ProductCategory(
        id=str(uuid.uuid4()),
        name="Widgets",
        description="All kinds of widgets",
    )
    uow = SQLAlchemyUnitOfWork()
    async with uow:
        await uow.products.add_category(cat)

    # now create a product
    prod = Product(
        id=str(uuid.uuid4()),
        name="Test Widget",
        category_id=cat.id,
        description="A test widget",
        price=9.99,
    )
    async with uow:
        await uow.products.create_product(prod)

    # fetch it back
    async with uow:
        fetched = await uow.products.get_product(prod.id)

    assert fetched is not None
    assert fetched.id == prod.id
    assert fetched.name == prod.name
    assert fetched.category_id == prod.category_id
    assert fetched.description == prod.description
    assert fetched.price == prod.price


@pytest.mark.asyncio
async def test_list_products(database_creation):
    # set up one category and two products
    cat = ProductCategory(id=str(uuid.uuid4()), name="Gadgets", description="Cool gadgets")
    prods = [
        Product(
            id=str(uuid.uuid4()),
            name=f"Gadget {i}",
            category_id=cat.id,
            description=f"Desc {i}",
            price=5.0 + i,
        )
        for i in (1, 2)
    ]

    uow = SQLAlchemyUnitOfWork()
    async with uow:
        await uow.products.add_category(cat)

    async with uow:
        for p in prods:
            await uow.products.create_product(p)

    async with uow:
        listed = await uow.products.get_products()

    ids = {p.id for p in listed}
    assert ids == {p.id for p in prods}


@pytest.mark.asyncio
async def test_update_product(database_creation):
    # prepare initial
    cat = ProductCategory(id=str(uuid.uuid4()), name="Foos", description="Foo products")
    prod = Product(
        id=str(uuid.uuid4()),
        name="Original",
        category_id=cat.id,
        description="Orig desc",
        price=1.23,
    )

    uow = SQLAlchemyUnitOfWork()
    async with uow:
        await uow.products.add_category(cat)

    async with uow:
        await uow.products.create_product(prod)

    # update fields
    updated = Product(
        id=prod.id,
        name="Updated",
        category_id=cat.id,
        description="New desc",
        price=4.56,
    )
    async with uow:
        result = await uow.products.update_product(updated)

    assert result.id == updated.id
    assert result.name == "Updated"
    assert result.description == "New desc"
    assert result.price == 4.56

    # double-check in DB
    async with uow:
        reloaded = await uow.products.get_product(prod.id)
    assert reloaded.name == "Updated"


@pytest.mark.asyncio
async def test_delete_product(database_creation):
    # prepare
    cat = ProductCategory(id=str(uuid.uuid4()), name="Bars", description="Bar products")
    prod = Product(
        id=str(uuid.uuid4()),
        name="ToDelete",
        category_id=cat.id,
        description="Oops",
        price=0.99,
    )

    uow = SQLAlchemyUnitOfWork()
    async with uow:
        await uow.products.add_category(cat)

    async with uow:
        await uow.products.create_product(prod)

    # delete
    async with uow:
        await uow.products.delete_product(prod.id)

    # ensure gone
    async with uow:
        gone = await uow.products.get_product(prod.id)
    assert gone is None
