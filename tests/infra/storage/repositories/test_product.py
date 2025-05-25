import uuid
import pytest

from src.domain.product.models import Product, ProductCategory
from src.uow.sqlalchemy import SQLAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_create_and_get_product(database_creation):
    uow = SQLAlchemyUnitOfWork()

    # prepare domain model
    product_category = ProductCategory(
        id=str(uuid.uuid4()),
        name="mineral water",
        description="Natural mineral water",
    )
    product = Product(
        id=str(uuid.uuid4()),
        name="Test Widget",
        category_id=product_category.id,
        description="A test widget",
        price=9.99,
    )

    # create
    async with uow:
        await uow.products.add_category(product_category)

    async with uow:
        await uow.products.create_product(product)

    # retrieve
    async with uow:
        fetched = await uow.products.get_product(product.id)
        assert fetched is not None
        assert fetched.id == product.id
        assert fetched.name == product.name
        assert fetched.description == product.description
        assert fetched.price == product.price


@pytest.mark.asyncio
async def test_create_and_get_product_1(database_creation):
    uow = SQLAlchemyUnitOfWork()

    # prepare domain model
    product_category = ProductCategory(
        id=str(uuid.uuid4()),
        name="mineral water",
        description="Natural mineral water",
    )
    product = Product(
        id=str(uuid.uuid4()),
        name="Test Widget",
        category_id=product_category.id,
        description="A test widget",
        price=9.99,
    )

    # create
    async with uow:
        await uow.products.add_category(product_category)

    async with uow:
        await uow.products.create_product(product)

    # retrieve
    async with uow:
        fetched = await uow.products.get_product(product.id)
        assert fetched is not None
        assert fetched.id == product.id
        assert fetched.name == product.name
        assert fetched.description == product.description
        assert fetched.price == product.price
