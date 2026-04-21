"""
Pytest configuration and fixtures for alert-service.
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
def db_session():
    """Yield a raw database session for direct data seeding in tests."""
    db = _TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
