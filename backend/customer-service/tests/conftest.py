"""
Pytest configuration and fixtures for customer-service.
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
from models import User, PurchaseHistory, Sale  # noqa: E402


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
def client_with_customer(client):
    """Return (client, customer_id) with one user seeded."""
    db = _TestSessionLocal()
    user = User(name="Priya Sharma", phone="9000000001", address="1 Anna Salai")
    db.add(user)
    db.commit()
    db.refresh(user)
    uid = user.id
    db.close()
    return client, uid


@pytest.fixture()
def db_session():
    """Yield a raw database session for direct data seeding in tests."""
    db = _TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client_with_history(client_with_customer):
    """Extend client_with_customer with a sale and purchase_history record."""
    c, uid = client_with_customer
    db = _TestSessionLocal()
    sale = Sale(user_id=uid, final_amount=250.0, sale_time="2026-04-21T10:00:00")
    db.add(sale)
    db.commit()
    db.refresh(sale)
    ph = PurchaseHistory(user_id=uid, sale_id=sale.id)
    db.add(ph)
    db.commit()
    db.close()
    return c, uid
