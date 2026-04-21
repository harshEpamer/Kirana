"""
Pytest configuration and fixtures for order-service.
"""
import sys
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

SERVICE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SERVICE_DIR not in sys.path:
    sys.path.insert(0, SERVICE_DIR)

import database as _db_module  # noqa: E402

_TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_TEST_ENGINE)
_db_module.engine = _TEST_ENGINE
_db_module.SessionLocal = _TestSessionLocal

from main import app  # noqa: E402
from database import get_db, Base  # noqa: E402
from models import Product, Coupon  # noqa: E402


@pytest.fixture()
def client():
    """Provide a TestClient backed by a fresh in-memory database per test."""
    Base.metadata.drop_all(bind=_TEST_ENGINE)
    Base.metadata.create_all(bind=_TEST_ENGINE)

    def _override_get_db():
        db = _TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def client_with_product(client):
    """Return (client, product_id) with one product: price=100, stock=50."""
    db = _TestSessionLocal()
    p = Product(name="Test Product", price=100.0, stock_qty=50)
    db.add(p)
    db.commit()
    db.refresh(p)
    pid = p.id
    db.close()
    return client, pid


@pytest.fixture()
def client_with_product_and_coupons(client_with_product):
    """Extend client_with_product with order_wise and product_wise coupons."""
    c, pid = client_with_product
    db = _TestSessionLocal()
    db.add_all([
        Coupon(code="SAVE10", discount_type="order_wise",
               discount_value=10.0, product_id=None, is_active=1),
        Coupon(code="PROD5", discount_type="product_wise",
               discount_value=5.0, product_id=pid, is_active=1),
        Coupon(code="INACTIVE", discount_type="order_wise",
               discount_value=50.0, product_id=None, is_active=0),
    ])
    db.commit()
    db.close()
    return c, pid
