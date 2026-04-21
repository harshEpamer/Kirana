"""
Tests for customer-service routers/customers.py.

Routes covered:
  GET /customers/
  GET /customers/{id}
  GET /customers/{id}/history
"""


# ── GET /customers/ ───────────────────────────────────────────────────────────

def test_list_customers_empty_returns_200(client):
    """GET /customers/ returns 200 with empty list when no customers exist."""
    resp = client.get("/customers/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_customers_returns_all_customers(client_with_customer):
    """GET /customers/ returns all seeded customers."""
    c, _ = client_with_customer
    resp = c.get("/customers/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "Priya Sharma"


def test_list_customers_response_fields(client_with_customer):
    """Customer list items contain expected fields without password."""
    c, _ = client_with_customer
    customer = c.get("/customers/").json()[0]
    for field in ("id", "name", "phone", "address"):
        assert field in customer
    assert "password" not in customer
    assert "password_hash" not in customer


# ── GET /customers/{id} ──────────────────────────────────────────────────────

def test_get_customer_returns_200(client_with_customer):
    """GET /customers/{id} returns 200 for an existing customer."""
    c, uid = client_with_customer
    resp = c.get(f"/customers/{uid}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == uid
    assert body["phone"] == "9000000001"


def test_get_customer_not_found_returns_404(client):
    """GET /customers/9999 returns 404 when customer does not exist."""
    resp = client.get("/customers/9999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


# ── GET /customers/{id}/history ───────────────────────────────────────────────

def test_get_purchase_history_customer_not_found_returns_404(client):
    """GET /customers/9999/history returns 404 when customer does not exist."""
    resp = client.get("/customers/9999/history")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_get_purchase_history_empty_when_no_purchases(client_with_customer):
    """GET /customers/{id}/history returns empty list when no purchases exist."""
    c, uid = client_with_customer
    resp = c.get(f"/customers/{uid}/history")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_purchase_history_returns_history(client_with_history):
    """GET /customers/{id}/history returns purchase records with sale details."""
    c, uid = client_with_history
    resp = c.get(f"/customers/{uid}/history")
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) == 1
    entry = history[0]
    assert "sale_id" in entry
    assert entry["final_amount"] == 250.0
    assert entry["sale_time"] == "2026-04-21T10:00:00"


def test_get_purchase_history_ordered_descending(client_with_customer, db_session):
    """Multiple purchases are returned in descending order."""
    from models import Sale, PurchaseHistory
    c, uid = client_with_customer
    for amount in [100.0, 200.0, 300.0]:
        sale = Sale(user_id=uid, final_amount=amount, sale_time="2026-04-21T00:00:00")
        db_session.add(sale)
        db_session.flush()
        db_session.add(PurchaseHistory(user_id=uid, sale_id=sale.id))
    db_session.commit()
    resp = c.get(f"/customers/{uid}/history")
    assert resp.status_code == 200
    amounts = [h["final_amount"] for h in resp.json()]
    assert amounts == sorted(amounts, reverse=True)
