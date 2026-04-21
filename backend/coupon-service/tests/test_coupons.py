"""
Tests for coupon-service routers/coupons.py.

Routes covered:
  GET    /coupons/
  POST   /coupons/
  DELETE /coupons/{id}
  POST   /coupons/validate
"""


# ── Helpers ──────────────────────────────────────────────────────────────────

def _order_wise_payload(code="TESTSAVE"):
    return {"code": code, "discount_type": "order_wise", "discount_value": 10.0}


def _product_wise_payload(code="TESTPROD", product_id=1):
    return {
        "code": code,
        "discount_type": "product_wise",
        "discount_value": 5.0,
        "product_id": product_id,
    }


# ── GET /coupons/ ─────────────────────────────────────────────────────────────

def test_list_coupons_empty_returns_200(client):
    """GET /coupons/ returns 200 with empty list when no coupons exist."""
    resp = client.get("/coupons/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_coupons_returns_seeded_coupons(client_with_coupons):
    """GET /coupons/ returns all seeded coupons."""
    resp = client_with_coupons.get("/coupons/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# ── POST /coupons/ ────────────────────────────────────────────────────────────

def test_create_order_wise_coupon_returns_201(client):
    """Creating an order_wise coupon returns 201 with coupon fields."""
    resp = client.post("/coupons/", json=_order_wise_payload())
    assert resp.status_code == 201
    body = resp.json()
    assert body["code"] == "TESTSAVE"
    assert body["discount_type"] == "order_wise"
    assert body["discount_value"] == 10.0
    assert body["is_active"] == 1
    assert "id" in body


def test_create_product_wise_coupon_returns_201(client):
    """Creating a product_wise coupon stores product_id correctly."""
    resp = client.post("/coupons/", json=_product_wise_payload())
    assert resp.status_code == 201
    body = resp.json()
    assert body["discount_type"] == "product_wise"
    assert body["product_id"] == 1


def test_create_coupon_duplicate_code_returns_400(client):
    """Creating a coupon with a duplicate code returns 400."""
    client.post("/coupons/", json=_order_wise_payload(code="DUP"))
    resp = client.post("/coupons/", json=_order_wise_payload(code="DUP"))
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"].lower()


def test_create_coupon_missing_code_returns_422(client):
    """Creating coupon without 'code' field returns 422."""
    payload = _order_wise_payload()
    del payload["code"]
    resp = client.post("/coupons/", json=payload)
    assert resp.status_code == 422


def test_create_coupon_missing_discount_type_returns_422(client):
    """Creating coupon without 'discount_type' field returns 422."""
    payload = _order_wise_payload()
    del payload["discount_type"]
    resp = client.post("/coupons/", json=payload)
    assert resp.status_code == 422


def test_create_coupon_invalid_discount_type_returns_422(client):
    """Creating coupon with invalid discount_type returns 422."""
    payload = {**_order_wise_payload(), "discount_type": "unknown_type"}
    resp = client.post("/coupons/", json=payload)
    assert resp.status_code == 422


# ── DELETE /coupons/{id} ──────────────────────────────────────────────────────

def test_deactivate_coupon_returns_204(client):
    """DELETE /coupons/{id} returns 204 and sets is_active=0."""
    created = client.post("/coupons/", json=_order_wise_payload()).json()
    resp = client.delete(f"/coupons/{created['id']}")
    assert resp.status_code == 204
    # Verify coupon is no longer active — validate should return invalid
    validate_resp = client.post(
        "/coupons/validate",
        json={"code": "TESTSAVE", "order_total": 200.0},
    )
    assert validate_resp.json()["valid"] is False


def test_deactivate_coupon_not_found_returns_404(client):
    """DELETE /coupons/9999 returns 404 when coupon does not exist."""
    resp = client.delete("/coupons/9999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


# ── POST /coupons/validate ────────────────────────────────────────────────────

def test_validate_order_wise_coupon_applies_discount(client_with_coupons):
    """Validating an order_wise coupon returns valid=True with correct discount."""
    resp = client_with_coupons.post(
        "/coupons/validate",
        json={"code": "SAVE10", "order_total": 200.0},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is True
    assert body["discount_amount"] == 10.0
    assert "applied" in body["message"].lower()


def test_validate_order_wise_coupon_capped_at_total(client_with_coupons):
    """order_wise discount is capped at the order total (min logic)."""
    resp = client_with_coupons.post(
        "/coupons/validate",
        json={"code": "SAVE10", "order_total": 5.0},   # total < discount_value
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is True
    assert body["discount_amount"] == 5.0  # capped at order_total


def test_validate_product_wise_coupon_correct_product(client_with_coupons):
    """Validating product_wise coupon with matching product_id returns valid=True."""
    resp = client_with_coupons.post(
        "/coupons/validate",
        json={"code": "RICE20", "order_total": 500.0, "product_id": 1},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is True
    assert body["discount_amount"] == 20.0


def test_validate_product_wise_coupon_wrong_product(client_with_coupons):
    """Validating product_wise coupon with wrong product_id returns valid=False."""
    resp = client_with_coupons.post(
        "/coupons/validate",
        json={"code": "RICE20", "order_total": 500.0, "product_id": 999},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is False


def test_validate_invalid_coupon_code_returns_not_valid(client):
    """Validating a non-existent code returns valid=False without 404."""
    resp = client.post(
        "/coupons/validate",
        json={"code": "DOESNOTEXIST", "order_total": 100.0},
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is False


def test_validate_inactive_coupon_returns_not_valid(client):
    """Validating a deactivated coupon returns valid=False."""
    created = client.post("/coupons/", json=_order_wise_payload(code="OFF50")).json()
    client.delete(f"/coupons/{created['id']}")
    resp = client.post(
        "/coupons/validate",
        json={"code": "OFF50", "order_total": 100.0},
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is False
