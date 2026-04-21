import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import Base, get_db
from main import app
from models import User, Product, Sale, SaleItem, PurchaseHistory, StockAdjustment

TEST_DATABASE_URL = "sqlite:///./test_orders.db"
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


def _seed_user(db, name="Ravi", phone="9000000001"):
    user = User(name=name, phone=phone, address="Delhi", password_hash="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _seed_product(db, name="Basmati Rice 1kg", category="Grains", price=85.0, stock=50):
    product = Product(name=name, category=category, price=price, stock_qty=stock, reorder_threshold=10)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def _mock_coupon_validate_success(discount=10.0):
    """Returns a mock httpx response for successful coupon validation."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"valid": True, "discount_amount": discount, "message": "Coupon applied"}
    return mock_resp


def _mock_coupon_validate_invalid():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"valid": False, "discount_amount": 0.0, "message": "Invalid coupon"}
    return mock_resp


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
        assert res.json()["service"] == "order-service"


# ────────────────────────── Checkout Validation ──────────────────────────

class TestCheckoutValidation:
    @patch("routers.orders._check_alerts")
    @patch("routers.orders._validate_coupon_remote", return_value=0.0)
    def test_user_not_found(self, mock_coupon, mock_alert):
        res = client.post("/orders/checkout", json={
            "user_id": 999,
            "cart": [{"product_id": 1, "quantity": 1}],
        })
        assert res.status_code == 404
        assert res.json()["detail"] == "User not found"

    @patch("routers.orders._check_alerts")
    @patch("routers.orders._validate_coupon_remote", return_value=0.0)
    def test_product_not_found(self, mock_coupon, mock_alert):
        db = TestingSessionLocal()
        user = _seed_user(db)
        db.close()

        res = client.post("/orders/checkout", json={
            "user_id": user.id,
            "cart": [{"product_id": 999, "quantity": 1}],
        })
        assert res.status_code == 404
        assert "Product 999 not found" in res.json()["detail"]

    @patch("routers.orders._check_alerts")
    @patch("routers.orders._validate_coupon_remote", return_value=0.0)
    def test_insufficient_stock(self, mock_coupon, mock_alert):
        db = TestingSessionLocal()
        user = _seed_user(db)
        product = _seed_product(db, stock=2)
        db.close()

        res = client.post("/orders/checkout", json={
            "user_id": user.id,
            "cart": [{"product_id": product.id, "quantity": 5}],
        })
        assert res.status_code == 400
        assert "Insufficient stock" in res.json()["detail"]

    def test_empty_cart(self):
        """Empty cart should still validate user."""
        db = TestingSessionLocal()
        user = _seed_user(db)
        db.close()

        with patch("routers.orders._check_alerts"), \
             patch("routers.orders._validate_coupon_remote", return_value=0.0):
            res = client.post("/orders/checkout", json={
                "user_id": user.id,
                "cart": [],
            })
        # Empty cart → 0 total → successful order with 0 amount
        assert res.status_code == 201

    def test_missing_fields(self):
        res = client.post("/orders/checkout", json={})
        assert res.status_code == 422


# ────────────────────── Checkout Success (no coupon) ──────────────────────

class TestCheckoutNoCoupon:
    @patch("routers.orders._check_alerts")
    def test_single_item_checkout(self, mock_alert):
        db = TestingSessionLocal()
        user = _seed_user(db)
        product = _seed_product(db, price=85.0, stock=50)
        db.close()

        res = client.post("/orders/checkout", json={
            "user_id": user.id,
            "cart": [{"product_id": product.id, "quantity": 2}],
        })
        assert res.status_code == 201
        data = res.json()
        assert data["order_id"] is not None
        assert data["total_amount"] == 170.0
        assert data["discount_amount"] == 0.0
        assert data["final_amount"] == 170.0
        assert data["coupon_applied"] is None

    @patch("routers.orders._check_alerts")
    def test_multi_item_checkout(self, mock_alert):
        db = TestingSessionLocal()
        user = _seed_user(db)
        p1 = _seed_product(db, name="Rice", price=85.0, stock=50)
        p2 = _seed_product(db, name="Dal", category="Pulses", price=65.0, stock=30)
        db.close()

        res = client.post("/orders/checkout", json={
            "user_id": user.id,
            "cart": [
                {"product_id": p1.id, "quantity": 1},
                {"product_id": p2.id, "quantity": 2},
            ],
        })
        assert res.status_code == 201
        data = res.json()
        assert data["total_amount"] == 85.0 + 130.0
        assert data["final_amount"] == 215.0

    @patch("routers.orders._check_alerts")
    def test_stock_decremented(self, mock_alert):
        db = TestingSessionLocal()
        user = _seed_user(db)
        product = _seed_product(db, stock=50)
        db.close()

        client.post("/orders/checkout", json={
            "user_id": user.id,
            "cart": [{"product_id": product.id, "quantity": 3}],
        })

        db = TestingSessionLocal()
        p = db.query(Product).filter(Product.id == product.id).first()
        assert p.stock_qty == 47
        db.close()

    @patch("routers.orders._check_alerts")
    def test_sale_record_created(self, mock_alert):
        db = TestingSessionLocal()
        user = _seed_user(db)
        product = _seed_product(db)
        db.close()

        res = client.post("/orders/checkout", json={
            "user_id": user.id,
            "cart": [{"product_id": product.id, "quantity": 1}],
        })
        order_id = res.json()["order_id"]

        db = TestingSessionLocal()
        sale = db.query(Sale).filter(Sale.id == order_id).first()
        assert sale is not None
        assert sale.user_id == user.id
        db.close()

    @patch("routers.orders._check_alerts")
    def test_sale_items_created(self, mock_alert):
        db = TestingSessionLocal()
        user = _seed_user(db)
        product = _seed_product(db, price=85.0)
        db.close()

        res = client.post("/orders/checkout", json={
            "user_id": user.id,
            "cart": [{"product_id": product.id, "quantity": 2}],
        })
        order_id = res.json()["order_id"]

        db = TestingSessionLocal()
        items = db.query(SaleItem).filter(SaleItem.sale_id == order_id).all()
        assert len(items) == 1
        assert items[0].product_id == product.id
        assert items[0].quantity == 2
        assert items[0].unit_price == 85.0
        db.close()

    @patch("routers.orders._check_alerts")
    def test_stock_adjustment_recorded(self, mock_alert):
        db = TestingSessionLocal()
        user = _seed_user(db)
        product = _seed_product(db)
        db.close()

        client.post("/orders/checkout", json={
            "user_id": user.id,
            "cart": [{"product_id": product.id, "quantity": 3}],
        })

        db = TestingSessionLocal()
        adj = db.query(StockAdjustment).filter(StockAdjustment.product_id == product.id).first()
        assert adj is not None
        assert adj.adjustment_type == "sale_deduct"
        assert adj.quantity == 3
        db.close()

    @patch("routers.orders._check_alerts")
    def test_purchase_history_recorded(self, mock_alert):
        db = TestingSessionLocal()
        user = _seed_user(db)
        product = _seed_product(db)
        db.close()

        res = client.post("/orders/checkout", json={
            "user_id": user.id,
            "cart": [{"product_id": product.id, "quantity": 1}],
        })
        order_id = res.json()["order_id"]

        db = TestingSessionLocal()
        ph = db.query(PurchaseHistory).filter(PurchaseHistory.user_id == user.id).first()
        assert ph is not None
        assert ph.sale_id == order_id
        db.close()


# ────────────────────── Checkout with Coupon ──────────────────────

class TestCheckoutWithCoupon:
    @patch("routers.orders._check_alerts")
    @patch("routers.orders._validate_coupon_remote", return_value=10.0)
    def test_coupon_applied(self, mock_coupon, mock_alert):
        db = TestingSessionLocal()
        user = _seed_user(db)
        product = _seed_product(db, price=85.0, stock=50)
        db.close()

        res = client.post("/orders/checkout", json={
            "user_id": user.id,
            "cart": [{"product_id": product.id, "quantity": 2}],
            "coupon_code": "SAVE10",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["total_amount"] == 170.0
        assert data["discount_amount"] == 10.0
        assert data["final_amount"] == 160.0
        assert data["coupon_applied"] == "SAVE10"

    @patch("routers.orders._check_alerts")
    @patch("routers.orders._validate_coupon_remote", return_value=0.0)
    def test_invalid_coupon_rejected(self, mock_coupon, mock_alert):
        db = TestingSessionLocal()
        user = _seed_user(db)
        product = _seed_product(db, stock=50)
        db.close()

        res = client.post("/orders/checkout", json={
            "user_id": user.id,
            "cart": [{"product_id": product.id, "quantity": 1}],
            "coupon_code": "FAKE",
        })
        assert res.status_code == 400
        assert "Invalid or inactive coupon" in res.json()["detail"]

    @patch("routers.orders._check_alerts")
    def test_coupon_service_unavailable(self, mock_alert):
        db = TestingSessionLocal()
        user = _seed_user(db)
        product = _seed_product(db, stock=50)
        db.close()

        import httpx
        with patch("routers.orders._validate_coupon_remote", side_effect=httpx.RequestError("connection refused")):
            res = client.post("/orders/checkout", json={
                "user_id": user.id,
                "cart": [{"product_id": product.id, "quantity": 1}],
                "coupon_code": "SAVE10",
            })
        assert res.status_code == 502
        assert "Coupon service unavailable" in res.json()["detail"]


# ────────────────────── Alert Service Calls ──────────────────────

class TestAlertCalls:
    @patch("routers.orders._check_alerts")
    def test_alerts_called_for_each_product(self, mock_alert):
        db = TestingSessionLocal()
        user = _seed_user(db)
        p1 = _seed_product(db, name="Rice", stock=50)
        p2 = _seed_product(db, name="Dal", category="Pulses", price=65.0, stock=30)
        db.close()

        client.post("/orders/checkout", json={
            "user_id": user.id,
            "cart": [
                {"product_id": p1.id, "quantity": 1},
                {"product_id": p2.id, "quantity": 1},
            ],
        })
        assert mock_alert.call_count == 2
        called_ids = [call.args[0] for call in mock_alert.call_args_list]
        assert p1.id in called_ids
        assert p2.id in called_ids
