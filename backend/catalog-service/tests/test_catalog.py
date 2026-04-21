"""
Tests for catalog-service routers/catalog.py.

Routes covered:
  GET /catalog/products           (with optional category / search filters)
  GET /catalog/products/{id}
  GET /catalog/categories
"""


# ── GET /catalog/products ─────────────────────────────────────────────────────

def test_list_products_empty_returns_200(client):
    """GET /catalog/products returns 200 with empty list when no products exist."""
    resp = client.get("/catalog/products")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_products_returns_all_seeded_products(seeded_client):
    """GET /catalog/products returns all seeded products."""
    resp = seeded_client.get("/catalog/products")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_products_response_fields_are_correct(seeded_client):
    """Product list items contain expected fields without reorder_threshold."""
    products = seeded_client.get("/catalog/products").json()
    for p in products:
        assert "id" in p
        assert "name" in p
        assert "category" in p
        assert "price" in p
        assert "stock_qty" in p
        assert "image_url" in p


def test_list_products_filter_by_category(seeded_client):
    """GET /catalog/products?category=Grains returns only Grains products."""
    resp = seeded_client.get("/catalog/products?category=Grains")
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["name"] == "Basmati Rice 1kg"


def test_list_products_filter_by_nonexistent_category_returns_empty(seeded_client):
    """GET /catalog/products?category=Electronics returns empty list."""
    resp = seeded_client.get("/catalog/products?category=Electronics")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_products_search_by_name(seeded_client):
    """GET /catalog/products?search=rice returns products matching the name."""
    resp = seeded_client.get("/catalog/products?search=rice")
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert "Rice" in results[0]["name"]


def test_list_products_search_is_case_insensitive(seeded_client):
    """Search filter is case-insensitive (ILIKE match)."""
    resp = seeded_client.get("/catalog/products?search=TOOR")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_list_products_search_no_match_returns_empty(seeded_client):
    """Search returning no matches yields an empty list."""
    resp = seeded_client.get("/catalog/products?search=XYZ_nonexistent")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_products_combined_category_and_search(seeded_client):
    """Category and search filters are applied together (AND logic)."""
    resp = seeded_client.get("/catalog/products?category=Grains&search=rice")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


# ── GET /catalog/products/{id} ────────────────────────────────────────────────

def test_get_product_returns_200(seeded_client):
    """GET /catalog/products/{id} returns 200 for an existing product."""
    products = seeded_client.get("/catalog/products").json()
    product_id = products[0]["id"]
    resp = seeded_client.get(f"/catalog/products/{product_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == product_id


def test_get_product_not_found_returns_404(client):
    """GET /catalog/products/9999 returns 404 when product does not exist."""
    resp = client.get("/catalog/products/9999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


# ── GET /catalog/categories ───────────────────────────────────────────────────

def test_list_categories_empty_returns_empty_list(client):
    """GET /catalog/categories returns empty list when no products exist."""
    resp = client.get("/catalog/categories")
    assert resp.status_code == 200
    assert resp.json()["categories"] == []


def test_list_categories_returns_distinct_categories(seeded_client):
    """GET /catalog/categories returns distinct category names."""
    resp = seeded_client.get("/catalog/categories")
    assert resp.status_code == 200
    categories = resp.json()["categories"]
    assert set(categories) == {"Grains", "Pulses"}
    assert len(categories) == len(set(categories))  # no duplicates
