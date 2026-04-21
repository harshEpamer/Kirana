"""
Tests for auth-service routers/auth.py.

Routes covered:
  POST /auth/register
  POST /auth/login
  GET  /auth/me
  GET  /health
"""


# ── Helpers ──────────────────────────────────────────────────────────────────

def _reg_payload(**overrides):
    """Return a valid registration payload, with optional field overrides."""
    base = {
        "name": "Ravi Kumar",
        "phone": "9876543210",
        "address": "12 MG Road, Mumbai",
        "password": "StrongPass@123",
    }
    base.update(overrides)
    return base


# ── POST /auth/register ───────────────────────────────────────────────────────

def test_register_returns_201(client):
    """Valid registration payload returns 201 and user JSON without password."""
    resp = client.post("/auth/register", json=_reg_payload())
    assert resp.status_code == 201
    body = resp.json()
    assert body["phone"] == "9876543210"
    assert body["name"] == "Ravi Kumar"
    assert "id" in body
    assert "password" not in body
    assert "password_hash" not in body


def test_register_duplicate_phone_returns_400(client):
    """Registering the same phone twice returns 400."""
    client.post("/auth/register", json=_reg_payload())
    resp = client.post("/auth/register", json=_reg_payload())
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"].lower()


def test_register_missing_name_returns_422(client):
    """Missing required field 'name' returns 422 validation error."""
    payload = _reg_payload()
    del payload["name"]
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 422


def test_register_missing_phone_returns_422(client):
    """Missing required field 'phone' returns 422 validation error."""
    payload = _reg_payload()
    del payload["phone"]
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 422


def test_register_missing_password_returns_422(client):
    """Missing required field 'password' returns 422 validation error."""
    payload = _reg_payload()
    del payload["password"]
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 422


# ── POST /auth/login ──────────────────────────────────────────────────────────

def test_login_valid_credentials_returns_token(client):
    """Logging in with correct credentials returns a bearer token."""
    client.post("/auth/register", json=_reg_payload())
    resp = client.post(
        "/auth/login",
        json={"phone": "9876543210", "password": "StrongPass@123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 10


def test_login_wrong_password_returns_401(client):
    """Login with incorrect password returns 401."""
    client.post("/auth/register", json=_reg_payload())
    resp = client.post(
        "/auth/login",
        json={"phone": "9876543210", "password": "WrongPass!"},
    )
    assert resp.status_code == 401
    assert "invalid" in resp.json()["detail"].lower()


def test_login_unknown_phone_returns_401(client):
    """Login with a phone number not in the database returns 401."""
    resp = client.post(
        "/auth/login",
        json={"phone": "0000000000", "password": "AnyPass"},
    )
    assert resp.status_code == 401


def test_login_missing_phone_returns_422(client):
    """Login payload missing phone returns 422 validation error."""
    resp = client.post("/auth/login", json={"password": "SomePass"})
    assert resp.status_code == 422


# ── GET /auth/me ──────────────────────────────────────────────────────────────

def test_get_me_returns_501(client):
    """GET /auth/me is not yet implemented and returns 501."""
    resp = client.get("/auth/me")
    assert resp.status_code == 501


# ── GET /health ───────────────────────────────────────────────────────────────

def test_health_endpoint_returns_200(client):
    """Health endpoint returns 200 and service metadata."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
