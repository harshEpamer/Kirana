"""
Tests for order-service routers/orders.py.

Routes covered:
  POST /orders/
"""


# ── POST /orders/ ─────────────────────────────────────────────────────────────

def test_checkout_returns_201(client_with_product):
    """Valid checkout returns 201 with sale_id, totals, and items."""
    c, pid = client_with_product
    resp = c.post(
        "/orders/",
        json={"user_id": 1, "items": [{"product_id": pid, "quantity": 3}]},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "sale_id" in body
    assert body["total_amount"] == 300.0    # 3 × 100.0
    assert body["discount_amount"] == 0.0
    assert body["final_amount"] == 300.0
    assert body["coupon_code"] is None
    assert len(body["items"]) == 1


def test_checkout_deducts_stock(client_with_product):
    """Checkout deducts purchased quantity from product stock."""
    c, pid = client_with_product
    # Buy 50 (all available)
    resp = c.post(
        "/orders/",
        json={"items": [{"product_id": pid, "quantity": 50}]},
    )
    assert resp.status_code == 201
    # Now stock is 0 — buying even 1 should fail
    resp2 = c.post(
        "/orders/",
        json={"items": [{"product_id": pid, "quantity": 1}]},
    )
    assert resp2.status_code == 400


def test_checkout_product_not_found_returns_404(client):
    """Checkout with a non-existent product_id returns 404."""
    resp = client.post(
        "/orders/",
        json={"items": [{"product_id": 9999, "quantity": 1}]},
    )
    assert resp.status_code == 404


def test_checkout_insufficient_stock_returns_400(client_with_product):
    """Checkout requesting more than available stock returns 400."""
    c, pid = client_with_product
    resp = c.post(
        "/orders/",
        json={"items": [{"product_id": pid, "quantity": 9999}]},
    )
    assert resp.status_code == 400
    assert "insufficient" in resp.json()["detail"].lower()


def test_checkout_invalid_coupon_returns_400(client_with_product):
    """Checkout with an invalid coupon code returns 400."""
    c, pid = client_with_product
    resp = c.post(
        "/orders/",
        json={
            "items": [{"product_id": pid, "quantity": 1}],
            "coupon_code": "FAKE_COUPON",
        },
    )
    assert resp.status_code == 400
    assert "invalid" in resp.json()["detail"].lower()


def test_checkout_inactive_coupon_returns_400(client_with_product_and_coupons):
    """Checkout with an inactive coupon returns 400."""
    c, pid = client_with_product_and_coupons
    resp = c.post(
        "/orders/",
        json={
            "items": [{"product_id": pid, "quantity": 1}],
            "coupon_code": "INACTIVE",
        },
    )
    assert resp.status_code == 400


def test_checkout_with_order_wise_coupon_applies_discount(
    client_with_product_and_coupons,
):
    """Order-wise coupon (SAVE10 = 10 off) is subtracted from total."""
    c, pid = client_with_product_and_coupons
    resp = c.post(
        "/orders/",
        json={
            "user_id": 1,
            "items": [{"product_id": pid, "quantity": 2}],  # total = 200
            "coupon_code": "SAVE10",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["total_amount"] == 200.0
    assert body["discount_amount"] == 10.0
    assert body["final_amount"] == 190.0
    assert body["coupon_code"] == "SAVE10"


def test_checkout_with_product_wise_coupon_applies_per_unit_discount(
    client_with_product_and_coupons,
):
    """Product-wise coupon (PROD5 = 5 off per unit) discounts each matching item."""
    c, pid = client_with_product_and_coupons
    resp = c.post(
        "/orders/",
        json={
            "items": [{"product_id": pid, "quantity": 4}],  # total = 400
            "coupon_code": "PROD5",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["total_amount"] == 400.0
    assert body["discount_amount"] == 20.0   # 5 × 4 units
    assert body["final_amount"] == 380.0


def test_checkout_missing_items_returns_422(client):
    """Checkout without 'items' field returns 422 validation error."""
    resp = client.post("/orders/", json={"user_id": 1})
    assert resp.status_code == 422
