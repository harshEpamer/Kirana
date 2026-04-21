"""
Pytest configuration and fixtures for catalog-service.
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
from models import Product  # noqa: E402


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
def seeded_client(client):
    """Return a client with two products pre-seeded in the database."""
    db = _TestSessionLocal()
    db.add_all([
        Product(name="Basmati Rice 1kg", category="Grains", price=85.0,
                stock_qty=50, reorder_threshold=10, image_url="", created_at=None),
        Product(name="Toor Dal 500g", category="Pulses", price=65.0,
                stock_qty=30, reorder_threshold=8, image_url="", created_at=None),
    ])
    db.commit()
    db.close()
    return client
