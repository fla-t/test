# tests/services/test_sales_service.py
import pytest
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from src.uow.inmemory import InMemoryUnitOfWork
from src.services.sales.service import ProductService, SaleComparison


@pytest.mark.asyncio
async def test_get_sales_initially_empty():
    uow = InMemoryUnitOfWork()
    service = ProductService(uow)

    # no sales at the start
    out = await service.get_sales_between_dates()
    assert out == []


@pytest.mark.asyncio
async def test_create_and_get_sales_between_dates_roundtrip():
    uow = InMemoryUnitOfWork()
    service = ProductService(uow)

    now = datetime.now(timezone.utc)
    # create three sales via the service
    s1 = await service.create_sale("p1", 1, 10.0)
    s2 = await service.create_sale("p1", 2, 20.0)
    s3 = await service.create_sale("p2", 1, 5.0)

    # override their created_at so we can reliably query
    s1.created_at = now - timedelta(days=2)
    s2.created_at = now - timedelta(days=1)
    s3.created_at = now

    # fetch only the last 2 days for product "p1"
    start = now - timedelta(days=2)
    end = now
    results = await service.get_sales_between_dates(start_date=start, end_date=end, product_id="p1")
    ids = {r.id for r in results}
    assert ids == {s1.id, s2.id}

    # check total_price filtering too
    prices = sorted(r.total_price for r in results)
    assert prices == [10.0, 20.0]


@pytest.mark.asyncio
async def test_compare_sales_day_granularity():
    uow = InMemoryUnitOfWork()
    service = ProductService(uow)

    # align to midnight UTC
    now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    first_start = now - timedelta(days=3)
    first_end = now - timedelta(days=1)
    second_start = now - timedelta(days=10)
    second_end = now - timedelta(days=8)

    # bucket 1 and 2 in first period
    a = await service.create_sale("X", 1, 100.0)
    b = await service.create_sale("X", 1, 200.0)
    a.created_at = first_start + timedelta(hours=1)
    b.created_at = first_start + timedelta(days=1, hours=2)

    # same shape two periods earlier
    c = await service.create_sale("X", 1, 10.0)
    d = await service.create_sale("X", 1, 20.0)
    c.created_at = second_start + timedelta(hours=3)
    d.created_at = second_start + timedelta(days=1, hours=4)

    comp: List[SaleComparison] = await service.compare_sales(
        first_start=first_start,
        first_end=first_end,
        second_start=second_start,
        second_end=second_end,
        product_id="X",
        granularity="day",
    )

    # expect two daily buckets
    assert len(comp) == 2

    # first bucket
    assert comp[0].time == first_start
    assert comp[0].time_label == first_start.strftime("%Y-%m-%d")
    assert comp[0].first_total == 100.0
    assert comp[0].second_total == 10.0

    # second bucket
    assert comp[1].time == first_start + timedelta(days=1)
    assert comp[1].first_total == 200.0
    assert comp[1].second_total == 20.0


@pytest.mark.asyncio
async def test_compare_sales_week_and_month_granularity():
    uow = InMemoryUnitOfWork()
    service = ProductService(uow)

    base = datetime(2025, 1, 1, tzinfo=timezone.utc)
    first_start = base
    first_end = base + timedelta(weeks=2)
    second_start = base - timedelta(weeks=4)
    second_end = base - timedelta(weeks=2)

    # one sale per week in each period
    for i in range(2):
        sf = await service.create_sale("Y", 1, 50.0 * (i + 1))
        ss = await service.create_sale("Y", 1, 5.0 * (i + 1))
        sf.created_at = first_start + timedelta(weeks=i, hours=1)
        ss.created_at = second_start + timedelta(weeks=i, hours=2)

    # weekly buckets
    weekly = await service.compare_sales(
        first_start=first_start,
        first_end=first_end,
        second_start=second_start,
        second_end=second_end,
        product_id="Y",
        granularity="week",
    )
    assert len(weekly) == 2
    for idx, bucket in enumerate(weekly):
        assert bucket.first_total == 50.0 * (idx + 1)
        assert bucket.second_total == 5.0 * (idx + 1)
        # label like "2025-W01"
        assert bucket.time_label.startswith(str(bucket.time.isocalendar()[0]))

    # monthly (4-week fallback → all in one bucket)
    monthly = await service.compare_sales(
        first_start=first_start,
        first_end=first_end,
        second_start=second_start,
        second_end=second_end,
        product_id="Y",
        granularity="month",
    )
    assert len(monthly) == 1
    assert monthly[0].first_total == 50.0 + 100.0
    assert monthly[0].second_total == 5.0 + 10.0
    assert monthly[0].time_label == first_start.strftime("%Y-%m")


@pytest.mark.asyncio
async def test_compare_sales_asserts_on_mismatched_periods():
    uow = InMemoryUnitOfWork()
    service = ProductService(uow)

    now = datetime.now(timezone.utc)
    with pytest.raises(AssertionError):
        await service.compare_sales(
            first_start=now - timedelta(days=5),
            first_end=now,
            second_start=now - timedelta(days=3),
            second_end=now,
        )
