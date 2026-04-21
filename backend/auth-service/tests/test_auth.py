import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add service directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import Base, get_db
from main import app
from models import User

# In-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

USER_DATA = {
    "name": "Test User",
    "phone": "9999999999",
    "address": "123 Test Street",
    "password": "securepass123",
}


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ────────────────────────── Health ──────────────────────────

class TestHealth:
    def test_health_returns_ok(self):
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["service"] == "auth-service"


# ────────────────────────── Register ──────────────────────────

class TestRegister:
    def test_register_success(self):
        res = client.post("/auth/register", json=USER_DATA)
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == USER_DATA["name"]
        assert data["phone"] == USER_DATA["phone"]
        assert data["address"] == USER_DATA["address"]
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_duplicate_phone(self):
        client.post("/auth/register", json=USER_DATA)
        res = client.post("/auth/register", json=USER_DATA)
        assert res.status_code == 400
        assert res.json()["detail"] == "Phone already registered"

    def test_register_missing_fields(self):
        res = client.post("/auth/register", json={"name": "Test"})
        assert res.status_code == 422

    def test_register_empty_body(self):
        res = client.post("/auth/register", json={})
        assert res.status_code == 422


# ────────────────────────── Login ──────────────────────────

class TestLogin:
    def test_login_success(self):
        client.post("/auth/register", json=USER_DATA)
        res = client.post("/auth/login", json={
            "phone": USER_DATA["phone"],
            "password": USER_DATA["password"],
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] is not None
        assert data["name"] == USER_DATA["name"]
        assert data["role"] == "user"

    def test_login_wrong_password(self):
        client.post("/auth/register", json=USER_DATA)
        res = client.post("/auth/login", json={
            "phone": USER_DATA["phone"],
            "password": "wrongpassword",
        })
        assert res.status_code == 401
        assert res.json()["detail"] == "Invalid phone or password"

    def test_login_nonexistent_user(self):
        res = client.post("/auth/login", json={
            "phone": "0000000000",
            "password": "whatever",
        })
        assert res.status_code == 401
        assert res.json()["detail"] == "Invalid phone or password"

    def test_login_missing_fields(self):
        res = client.post("/auth/login", json={"phone": "9999999999"})
        assert res.status_code == 422


# ────────────────────────── GET /auth/me ──────────────────────────

class TestGetMe:
    def _get_token(self):
        client.post("/auth/register", json=USER_DATA)
        res = client.post("/auth/login", json={
            "phone": USER_DATA["phone"],
            "password": USER_DATA["password"],
        })
        return res.json()["access_token"]

    def test_me_success(self):
        token = self._get_token()
        res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["name"] == USER_DATA["name"]
        assert data["phone"] == USER_DATA["phone"]
        assert data["address"] == USER_DATA["address"]
        assert "password" not in data
        assert "password_hash" not in data

    def test_me_no_token(self):
        res = client.get("/auth/me")
        assert res.status_code in (401, 403)

    def test_me_invalid_token(self):
        res = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken123"})
        assert res.status_code == 401
        assert res.json()["detail"] == "Invalid token"

    def test_me_expired_token_format(self):
        # Malformed JWT
        res = client.get("/auth/me", headers={"Authorization": "Bearer a.b.c"})
        assert res.status_code == 401


# ────────────────────────── Token Content ──────────────────────────

class TestTokenContent:
    def test_token_contains_user_id_and_name(self):
        client.post("/auth/register", json=USER_DATA)
        res = client.post("/auth/login", json={
            "phone": USER_DATA["phone"],
            "password": USER_DATA["password"],
        })
        token = res.json()["access_token"]
        import base64, json as json_lib
        payload = json_lib.loads(base64.urlsafe_b64decode(token.split(".")[1] + "=="))
        assert "sub" in payload
        assert "name" in payload
        assert "phone" in payload
        assert "exp" in payload
        assert payload["name"] == USER_DATA["name"]
