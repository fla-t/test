from uuid import uuid4

from services.catalog.domain import models as mdl
from services.catalog.entrypoint import queries as qry
from services.catalog.entrypoint.unit_of_work import DBPoolUnitOfWork


def test_skus_by_ids(db_uow: DBPoolUnitOfWork, drop_skus_fk):
    with db_uow as uow:
        sku = mdl.Sku.create(str(uuid4()), "sku1", "desc1")
        uow.skus.save([sku])

    res = qry.skus_by_ids(db_uow, [sku.id])[0]

    assert isinstance(res, qry.SkuDTO)

    assert res.id == sku.id
    assert res.category_id == sku.category_id
    assert res.name == sku.name
    assert res.description == sku.description


def test_category_by_ids(db_uow: DBPoolUnitOfWork):
    with db_uow as uow:
        category = mdl.Category.create("fresh")
        uow.categories.save([category])

    res = qry.category_by_ids(db_uow, [category.id])[0]

    assert isinstance(res, qry.CategoryDTO)

    assert res.id == category.id
    assert res.name == category.name


def test_skus_by_categories(db_uow: DBPoolUnitOfWork):
    with db_uow as uow:
        categories = [mdl.Category.create("fresh"), mdl.Category.create("frozen")]
        category_ids = [c.id for c in categories]

        uow.categories.save(categories)

    with db_uow as uow:
        skus = [
            mdl.Sku.create(category_ids[0], "sku1", "desc1"),
            mdl.Sku.create(category_ids[1], "sku2", "desc2"),
        ]
        skus_by_category = {sku.category_id: sku for sku in skus}

        uow.skus.save(skus)

    for category_id in category_ids:
        res = qry.skus_by_categories(db_uow, [category_id])[0]

        sku = skus_by_category[category_id]
        assert res.id == sku.id
        assert res.category_id == sku.category_id
        assert res.name == sku.name
        assert res.description == res.description
