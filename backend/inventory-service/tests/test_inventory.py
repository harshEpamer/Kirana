# ── Product CRUD ────────────────────────────────────────────────────────────


def test_create_product(client):
    resp = client.post("/inventory/products", json={
        "name": "Rice",
        "category": "Grocery",
        "price": 60.0,
        "stock_qty": 100,
        "reorder_threshold": 20,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["name"] == "Rice"
    assert data["stock_qty"] == 100


def test_create_product_missing_field(client):
    resp = client.post("/inventory/products", json={
        "category": "Grocery",
        "price": 60.0,
    })
    assert resp.status_code == 422


def test_list_products_empty(client):
    resp = client.get("/inventory/products")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_products(client):
    for i in range(3):
        client.post("/inventory/products", json={
            "name": f"Item {i}",
            "category": "Test",
            "price": 10.0,
        })
    resp = client.get("/inventory/products")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_get_product(client, sample_product):
    pid = sample_product["id"]
    resp = client.get(f"/inventory/products/{pid}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Toor Dal"


def test_get_product_not_found(client):
    resp = client.get("/inventory/products/9999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Product not found"


def test_update_product(client, sample_product):
    pid = sample_product["id"]
    resp = client.put(f"/inventory/products/{pid}", json={"price": 150.0})
    assert resp.status_code == 200
    data = resp.json()
    assert data["price"] == 150.0
    assert data["name"] == "Toor Dal"  # unchanged


def test_update_product_not_found(client):
    resp = client.put("/inventory/products/9999", json={"price": 99.0})
    assert resp.status_code == 404


def test_delete_product(client, sample_product):
    pid = sample_product["id"]
    resp = client.delete(f"/inventory/products/{pid}")
    assert resp.status_code == 204


def test_delete_product_not_found(client):
    resp = client.delete("/inventory/products/9999")
    assert resp.status_code == 404


# ── Stock Adjustment ────────────────────────────────────────────────────────


def test_stock_adjust_add(client, sample_product):
    pid = sample_product["id"]
    resp = client.post("/inventory/stock-adjust", json={
        "product_id": pid, "adjustment_type": "add", "quantity": 20,
    })
    assert resp.status_code == 201
    product = client.get(f"/inventory/products/{pid}").json()
    assert product["stock_qty"] == 70  # 50 + 20


def test_stock_adjust_set(client, sample_product):
    pid = sample_product["id"]
    resp = client.post("/inventory/stock-adjust", json={
        "product_id": pid, "adjustment_type": "set", "quantity": 100,
    })
    assert resp.status_code == 201
    product = client.get(f"/inventory/products/{pid}").json()
    assert product["stock_qty"] == 100


def test_stock_adjust_sale_deduct(client, sample_product):
    pid = sample_product["id"]
    resp = client.post("/inventory/stock-adjust", json={
        "product_id": pid, "adjustment_type": "sale_deduct", "quantity": 5,
    })
    assert resp.status_code == 201
    product = client.get(f"/inventory/products/{pid}").json()
    assert product["stock_qty"] == 45  # 50 - 5


def test_stock_adjust_insufficient(client, sample_product):
    pid = sample_product["id"]
    resp = client.post("/inventory/stock-adjust", json={
        "product_id": pid, "adjustment_type": "sale_deduct", "quantity": 999,
    })
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Insufficient stock"


def test_stock_adjust_product_not_found(client):
    resp = client.post("/inventory/stock-adjust", json={
        "product_id": 9999, "adjustment_type": "add", "quantity": 10,
    })
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Product not found"


# ── Low Stock ───────────────────────────────────────────────────────────────


def test_low_stock_returns_items(client):
    client.post("/inventory/products", json={
        "name": "Sugar",
        "category": "Grocery",
        "price": 45.0,
        "stock_qty": 3,
        "reorder_threshold": 10,
    })
    resp = client.get("/inventory/low-stock")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Sugar"


def test_low_stock_empty(client):
    client.post("/inventory/products", json={
        "name": "Rice",
        "category": "Grocery",
        "price": 60.0,
        "stock_qty": 50,
        "reorder_threshold": 10,
    })
    resp = client.get("/inventory/low-stock")
    assert resp.status_code == 200
    assert resp.json() == []


# ── Bulk Insert ─────────────────────────────────────────────────────────────


def test_bulk_insert(client):
    products = [
        {"name": f"Bulk Item {i}", "category": "Test", "price": 10.0 + i, "stock_qty": i * 5}
        for i in range(5)
    ]
    resp = client.post("/inventory/products/bulk", json=products)
    assert resp.status_code == 201
    data = resp.json()
    assert data["created"] == 5
    assert len(data["products"]) == 5


# ── Reorder List ────────────────────────────────────────────────────────────


def test_reorder_list(client):
    client.post("/inventory/products", json={
        "name": "Low Item",
        "category": "Grocery",
        "price": 30.0,
        "stock_qty": 2,
        "reorder_threshold": 15,
    })
    # Also add a healthy-stock item (should NOT appear)
    client.post("/inventory/products", json={
        "name": "OK Item",
        "category": "Grocery",
        "price": 50.0,
        "stock_qty": 100,
        "reorder_threshold": 10,
    })
    resp = client.get("/inventory/reorder")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Low Item"
    assert data[0]["suggested_qty"] == 28  # 15*2 - 2


# ── Health ──────────────────────────────────────────────────────────────────


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
