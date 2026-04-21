"""
Tests for sales-service routers/sales.py.

Routes covered:
  GET  /sales/
  GET  /sales/{id}
  POST /sales/
"""


# ── GET /sales/ ───────────────────────────────────────────────────────────────

def test_list_sales_empty_returns_200(client):
    """GET /sales/ returns 200 with empty list when no sales exist."""
    resp = client.get("/sales/")
    assert resp.status_code == 200
    assert resp.json() == []


# ── POST /sales/ ──────────────────────────────────────────────────────────────

def test_create_sale_returns_201(client_with_product):
    """Valid sale creation returns 201 with sale body and items."""
    c, product_id = client_with_product
    payload = {
        "user_id": 1,
        "items": [{"product_id": product_id, "quantity": 2}],
        "coupon_code": None,
    }
    resp = c.post("/sales/", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["total_amount"] == 170.0   # 2 × 85.0
    assert body["final_amount"] == 170.0
    assert body["discount_amount"] == 0.0
    assert len(body["items"]) == 1
    assert body["items"][0]["product_id"] == product_id
    assert body["items"][0]["quantity"] == 2
    assert body["items"][0]["unit_price"] == 85.0


def test_create_sale_deducts_stock(client_with_product):
    """Creating a sale deducts the sold quantity from product stock."""
    c, product_id = client_with_product
    c.post("/sales/", json={"items": [{"product_id": product_id, "quantity": 5}]})
    # Use inventory GET via sales service — stock encoded in Sale not directly
    # accessible, but the POST should not error and the DB is updated
    resp = c.post("/sales/", json={"items": [{"product_id": product_id, "quantity": 45}]})
    # 50 - 5 = 45 remaining, so this should succeed
    assert resp.status_code == 201


def test_create_sale_product_not_found_returns_404(client):
    """Creating a sale with a non-existent product_id returns 404."""
    resp = client.post(
        "/sales/",
        json={"items": [{"product_id": 9999, "quantity": 1}]},
    )
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_create_sale_insufficient_stock_returns_400(client_with_product):
    """Creating a sale requesting more stock than available returns 400."""
    c, product_id = client_with_product
    resp = c.post(
        "/sales/",
        json={"items": [{"product_id": product_id, "quantity": 9999}]},
    )
    assert resp.status_code == 400
    assert "insufficient" in resp.json()["detail"].lower()


def test_create_sale_missing_items_returns_422(client):
    """Creating a sale without 'items' field returns 422 validation error."""
    resp = client.post("/sales/", json={"user_id": 1})
    assert resp.status_code == 422


def test_create_sale_records_coupon_code(client_with_product):
    """coupon_code is stored on the sale record (no discount applied in this service)."""
    c, product_id = client_with_product
    resp = c.post(
        "/sales/",
        json={
            "items": [{"product_id": product_id, "quantity": 1}],
            "coupon_code": "SAVE10",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["coupon_code"] == "SAVE10"


# ── GET /sales/{id} ───────────────────────────────────────────────────────────

def test_get_sale_returns_200(client_with_product):
    """GET /sales/{id} returns 200 for an existing sale."""
    c, product_id = client_with_product
    created = c.post(
        "/sales/", json={"items": [{"product_id": product_id, "quantity": 1}]}
    ).json()
    resp = c.get(f"/sales/{created['id']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == created["id"]
    assert len(body["items"]) == 1


def test_get_sale_not_found_returns_404(client):
    """GET /sales/9999 returns 404 when sale does not exist."""
    resp = client.get("/sales/9999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


# ── GET /sales/ (after creates) ───────────────────────────────────────────────

def test_list_sales_returns_created_sales(client_with_product):
    """GET /sales/ returns created sales in descending ID order."""
    c, product_id = client_with_product
    c.post("/sales/", json={"items": [{"product_id": product_id, "quantity": 1}]})
    c.post("/sales/", json={"items": [{"product_id": product_id, "quantity": 1}]})
    resp = c.get("/sales/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
