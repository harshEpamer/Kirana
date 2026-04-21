"""
Tests for alert-service routers/alerts.py.

Routes covered:
  GET /alerts/low-stock
"""
from models import Product


def _add_product(db, name, stock_qty, reorder_threshold, category="General", price=10.0):
    """Insert a product via the shared test db_session fixture."""
    p = Product(
        name=name,
        category=category,
        stock_qty=stock_qty,
        reorder_threshold=reorder_threshold,
        price=price,
    )
    db.add(p)
    db.commit()
    return p


# ── GET /alerts/low-stock ─────────────────────────────────────────────────────

def test_low_stock_no_products_returns_empty_list(client):
    """GET /alerts/low-stock returns empty list when no products exist."""
    resp = client.get("/alerts/low-stock")
    assert resp.status_code == 200
    assert resp.json() == []


def test_low_stock_no_alerts_when_stock_is_adequate(client, db_session):
    """GET /alerts/low-stock returns empty list when all stock >= threshold."""
    _add_product(db_session, "Adequate Product", stock_qty=20, reorder_threshold=10)
    resp = client.get("/alerts/low-stock")
    assert resp.status_code == 200
    assert resp.json() == []


def test_low_stock_stock_equal_to_threshold_not_an_alert(client, db_session):
    """stock_qty == reorder_threshold does NOT trigger an alert (strict <)."""
    _add_product(db_session, "Borderline Product", stock_qty=10, reorder_threshold=10)
    resp = client.get("/alerts/low-stock")
    assert resp.status_code == 200
    assert resp.json() == []


def test_low_stock_returns_alert_when_stock_below_threshold(client, db_session):
    """GET /alerts/low-stock returns one alert for a product below threshold."""
    _add_product(db_session, "Low Stock Item", stock_qty=3, reorder_threshold=10)
    resp = client.get("/alerts/low-stock")
    assert resp.status_code == 200
    alerts = resp.json()
    assert len(alerts) == 1
    alert = alerts[0]
    assert alert["name"] == "Low Stock Item"
    assert alert["stock_qty"] == 3
    assert alert["reorder_threshold"] == 10


def test_low_stock_shortfall_is_calculated_correctly(client, db_session):
    """shortfall == reorder_threshold - stock_qty."""
    _add_product(db_session, "Near Empty", stock_qty=2, reorder_threshold=15)
    resp = client.get("/alerts/low-stock")
    assert resp.status_code == 200
    alert = resp.json()[0]
    assert alert["shortfall"] == 13   # 15 - 2


def test_low_stock_filters_out_adequate_products(client, db_session):
    """Only products below threshold appear in low-stock alerts."""
    _add_product(db_session, "Plenty Stock", stock_qty=100, reorder_threshold=10)
    _add_product(db_session, "Low Stock", stock_qty=2, reorder_threshold=10)
    resp = client.get("/alerts/low-stock")
    assert resp.status_code == 200
    alerts = resp.json()
    assert len(alerts) == 1
    assert alerts[0]["name"] == "Low Stock"


def test_low_stock_sorted_by_stock_qty_ascending(client, db_session):
    """Low-stock alerts are ordered by stock_qty ascending (most critical first)."""
    _add_product(db_session, "Medium Low", stock_qty=5, reorder_threshold=10)
    _add_product(db_session, "Very Low", stock_qty=1, reorder_threshold=10)
    _add_product(db_session, "Critically Low", stock_qty=0, reorder_threshold=10)
    resp = client.get("/alerts/low-stock")
    assert resp.status_code == 200
    qtys = [a["stock_qty"] for a in resp.json()]
    assert qtys == sorted(qtys)


def test_low_stock_response_fields_are_complete(client, db_session):
    """Each alert in the response contains all required fields."""
    _add_product(db_session, "Check Fields", stock_qty=4, reorder_threshold=12,
                 category="Grains")
    resp = client.get("/alerts/low-stock")
    alert = resp.json()[0]
    for field in ("id", "name", "category", "stock_qty", "reorder_threshold", "shortfall"):
        assert field in alert, f"Missing field: {field}"
