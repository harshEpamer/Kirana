"""
Tests for inventory-service routers/inventory.py.

Routes covered:
  GET    /inventory/products
  GET    /inventory/products/{id}
  POST   /inventory/products
  PUT    /inventory/products/{id}
  DELETE /inventory/products/{id}
  POST   /inventory/stock-adjust
"""


# ── Helpers ──────────────────────────────────────────────────────────────────

def _product_payload(**overrides):
    """Return a valid product creation payload."""
    base = {
        "name": "Basmati Rice 1kg",
        "category": "Grains",
        "price": 85.0,
        "stock_qty": 50,
        "reorder_threshold": 10,
        "image_url": "",
    }
    base.update(overrides)
    return base


def _create_product(client, **overrides):
    """Helper: POST a product and return the created JSON."""
    resp = client.post("/inventory/products", json=_product_payload(**overrides))
    assert resp.status_code == 201
    return resp.json()


# ── GET /inventory/products ───────────────────────────────────────────────────

def test_list_products_empty_returns_200(client):
    """GET /inventory/products returns 200 with empty list when no products exist."""
    resp = client.get("/inventory/products")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_products_returns_all_products(client):
    """GET /inventory/products returns all created products."""
    _create_product(client, name="Toor Dal 500g")
    _create_product(client, name="Sunflower Oil 1L", phone="1111111111")
    resp = client.get("/inventory/products")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# ── POST /inventory/products ──────────────────────────────────────────────────

def test_create_product_returns_201(client):
    """Valid product payload returns 201 with created product fields."""
    resp = client.post("/inventory/products", json=_product_payload())
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Basmati Rice 1kg"
    assert body["category"] == "Grains"
    assert body["price"] == 85.0
    assert body["stock_qty"] == 50
    assert "id" in body


def test_create_product_missing_name_returns_422(client):
    """Creating a product without 'name' returns 422 validation error."""
    payload = _product_payload()
    del payload["name"]
    resp = client.post("/inventory/products", json=payload)
    assert resp.status_code == 422


def test_create_product_missing_category_returns_422(client):
    """Creating a product without 'category' returns 422 validation error."""
    payload = _product_payload()
    del payload["category"]
    resp = client.post("/inventory/products", json=payload)
    assert resp.status_code == 422


def test_create_product_missing_price_returns_422(client):
    """Creating a product without 'price' returns 422 validation error."""
    payload = _product_payload()
    del payload["price"]
    resp = client.post("/inventory/products", json=payload)
    assert resp.status_code == 422


# ── GET /inventory/products/{id} ──────────────────────────────────────────────

def test_get_product_returns_200(client):
    """GET /inventory/products/{id} returns 200 for an existing product."""
    created = _create_product(client)
    resp = client.get(f"/inventory/products/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_product_not_found_returns_404(client):
    """GET /inventory/products/9999 returns 404 when product does not exist."""
    resp = client.get("/inventory/products/9999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


# ── PUT /inventory/products/{id} ──────────────────────────────────────────────

def test_update_product_returns_200(client):
    """PUT /inventory/products/{id} returns 200 with updated fields."""
    created = _create_product(client)
    resp = client.put(
        f"/inventory/products/{created['id']}",
        json={"price": 99.0, "stock_qty": 100},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["price"] == 99.0
    assert body["stock_qty"] == 100
    assert body["name"] == "Basmati Rice 1kg"  # unchanged


def test_update_product_not_found_returns_404(client):
    """PUT /inventory/products/9999 returns 404 when product does not exist."""
    resp = client.put("/inventory/products/9999", json={"price": 99.0})
    assert resp.status_code == 404


# ── DELETE /inventory/products/{id} ──────────────────────────────────────────

def test_delete_product_returns_204(client):
    """DELETE /inventory/products/{id} returns 204 and removes the product."""
    created = _create_product(client)
    resp = client.delete(f"/inventory/products/{created['id']}")
    assert resp.status_code == 204
    # Verify product is gone
    get_resp = client.get(f"/inventory/products/{created['id']}")
    assert get_resp.status_code == 404


def test_delete_product_not_found_returns_404(client):
    """DELETE /inventory/products/9999 returns 404 when product does not exist."""
    resp = client.delete("/inventory/products/9999")
    assert resp.status_code == 404


# ── POST /inventory/stock-adjust ─────────────────────────────────────────────

def test_stock_adjust_add_increases_stock(client):
    """Stock adjustment 'add' increases product stock_qty and returns 201."""
    created = _create_product(client, stock_qty=10)
    resp = client.post(
        "/inventory/stock-adjust",
        json={"product_id": created["id"], "adjustment_type": "add", "quantity": 20},
    )
    assert resp.status_code == 201
    # Verify stock increased
    product = client.get(f"/inventory/products/{created['id']}").json()
    assert product["stock_qty"] == 30


def test_stock_adjust_set_replaces_stock(client):
    """Stock adjustment 'set' replaces stock_qty with given value."""
    created = _create_product(client, stock_qty=50)
    resp = client.post(
        "/inventory/stock-adjust",
        json={"product_id": created["id"], "adjustment_type": "set", "quantity": 5},
    )
    assert resp.status_code == 201
    product = client.get(f"/inventory/products/{created['id']}").json()
    assert product["stock_qty"] == 5


def test_stock_adjust_sale_deduct_decreases_stock(client):
    """Stock adjustment 'sale_deduct' subtracts quantity from stock_qty."""
    created = _create_product(client, stock_qty=30)
    resp = client.post(
        "/inventory/stock-adjust",
        json={
            "product_id": created["id"],
            "adjustment_type": "sale_deduct",
            "quantity": 10,
        },
    )
    assert resp.status_code == 201
    product = client.get(f"/inventory/products/{created['id']}").json()
    assert product["stock_qty"] == 20


def test_stock_adjust_sale_deduct_insufficient_returns_400(client):
    """sale_deduct with more than available stock returns 400."""
    created = _create_product(client, stock_qty=5)
    resp = client.post(
        "/inventory/stock-adjust",
        json={
            "product_id": created["id"],
            "adjustment_type": "sale_deduct",
            "quantity": 10,
        },
    )
    assert resp.status_code == 400
    assert "insufficient" in resp.json()["detail"].lower()


def test_stock_adjust_product_not_found_returns_404(client):
    """stock-adjust for non-existent product_id returns 404."""
    resp = client.post(
        "/inventory/stock-adjust",
        json={"product_id": 9999, "adjustment_type": "add", "quantity": 5},
    )
    assert resp.status_code == 404


def test_stock_adjust_invalid_type_returns_422(client):
    """stock-adjust with an invalid adjustment_type returns 422."""
    created = _create_product(client)
    resp = client.post(
        "/inventory/stock-adjust",
        json={
            "product_id": created["id"],
            "adjustment_type": "remove",  # not a valid Literal
            "quantity": 5,
        },
    )
    assert resp.status_code == 422
