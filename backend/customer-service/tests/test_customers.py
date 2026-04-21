import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import Base, get_db
from main import app
from models import User, Product, Sale, SaleItem, PurchaseHistory

TEST_DATABASE_URL = "sqlite:///./test_customer.db"
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


def _seed_user(db, name="Ravi", phone="9000000001", address="Delhi"):
    user = User(id=None, name=name, phone=phone, address=address, password_hash="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _seed_product(db, name="Rice 1kg", category="Grains", price=85.0):
    product = Product(name=name, category=category, price=price)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def _seed_sale(db, user_id, total=170.0, discount=10.0, final=160.0, coupon="SAVE10"):
    sale = Sale(
        user_id=user_id,
        total_amount=total,
        discount_amount=discount,
        final_amount=final,
        coupon_code=coupon,
        sale_time="2026-04-21T10:00:00",
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def _seed_sale_item(db, sale_id, product_id, quantity=2, unit_price=85.0):
    si = SaleItem(sale_id=sale_id, product_id=product_id, quantity=quantity, unit_price=unit_price)
    db.add(si)
    db.commit()
    db.refresh(si)
    return si


def _seed_purchase_history(db, user_id, sale_id):
    ph = PurchaseHistory(user_id=user_id, sale_id=sale_id, recorded_at="2026-04-21T10:00:00")
    db.add(ph)
    db.commit()


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
        assert res.json()["service"] == "customer-service"


# ────────────────────────── GET /customers/ ──────────────────────────

class TestListCustomers:
    def test_list_empty(self):
        res = client.get("/customers/")
        assert res.status_code == 200
        assert res.json() == []

    def test_list_single_customer_no_orders(self):
        db = TestingSessionLocal()
        _seed_user(db)
        db.close()

        res = client.get("/customers/")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["name"] == "Ravi"
        assert data[0]["total_orders"] == 0
        assert data[0]["total_spent"] == 0

    def test_list_customer_with_orders(self):
        db = TestingSessionLocal()
        user = _seed_user(db)
        _seed_sale(db, user.id, total=200.0, discount=0.0, final=200.0, coupon=None)
        _seed_sale(db, user.id, total=100.0, discount=10.0, final=90.0, coupon="SAVE10")
        db.close()

        res = client.get("/customers/")
        data = res.json()
        assert len(data) == 1
        assert data[0]["total_orders"] == 2
        assert data[0]["total_spent"] == 290.0

    def test_list_multiple_customers(self):
        db = TestingSessionLocal()
        _seed_user(db, name="Ravi", phone="9000000001")
        _seed_user(db, name="Priya", phone="9000000002")
        db.close()

        res = client.get("/customers/")
        assert len(res.json()) == 2

    def test_customer_summary_fields(self):
        db = TestingSessionLocal()
        _seed_user(db, name="Amit", phone="9000000003", address="Mumbai")
        db.close()

        res = client.get("/customers/")
        c = res.json()[0]
        assert "id" in c
        assert c["name"] == "Amit"
        assert c["phone"] == "9000000003"
        assert c["address"] == "Mumbai"
        assert "total_orders" in c
        assert "total_spent" in c


# ────────────────────── GET /customers/{user_id}/history ──────────────────────

class TestPurchaseHistory:
    def test_history_nonexistent_user(self):
        res = client.get("/customers/999/history")
        assert res.status_code == 404
        assert res.json()["detail"] == "Customer not found"

    def test_history_empty(self):
        db = TestingSessionLocal()
        user = _seed_user(db)
        db.close()

        res = client.get(f"/customers/{user.id}/history")
        assert res.status_code == 200
        assert res.json() == []

    def test_history_with_purchases(self):
        db = TestingSessionLocal()
        user = _seed_user(db)
        product = _seed_product(db)
        sale = _seed_sale(db, user.id, total=170.0, discount=10.0, final=160.0, coupon="SAVE10")
        _seed_sale_item(db, sale.id, product.id, quantity=2, unit_price=85.0)
        _seed_purchase_history(db, user.id, sale.id)
        user_id, sale_id = user.id, sale.id
        db.close()

        res = client.get(f"/customers/{user_id}/history")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1

        record = data[0]
        assert record["sale_id"] == sale_id
        assert record["total_amount"] == 170.0
        assert record["discount_amount"] == 10.0
        assert record["final_amount"] == 160.0
        assert record["coupon_code"] == "SAVE10"
        assert len(record["items"]) == 1
        assert record["items"][0]["product_name"] == "Rice 1kg"
        assert record["items"][0]["quantity"] == 2
        assert record["items"][0]["unit_price"] == 85.0

    def test_history_multiple_purchases(self):
        db = TestingSessionLocal()
        user = _seed_user(db)
        p1 = _seed_product(db, name="Rice", category="Grains", price=85.0)
        p2 = _seed_product(db, name="Dal", category="Pulses", price=65.0)
        sale1 = _seed_sale(db, user.id, total=85.0, discount=0.0, final=85.0, coupon=None)
        _seed_sale_item(db, sale1.id, p1.id, quantity=1, unit_price=85.0)
        _seed_purchase_history(db, user.id, sale1.id)
        sale2 = _seed_sale(db, user.id, total=130.0, discount=0.0, final=130.0, coupon=None)
        _seed_sale_item(db, sale2.id, p2.id, quantity=2, unit_price=65.0)
        _seed_purchase_history(db, user.id, sale2.id)
        user_id = user.id
        db.close()

        res = client.get(f"/customers/{user_id}/history")
        data = res.json()
        assert len(data) == 2

    def test_history_does_not_leak_other_users(self):
        db = TestingSessionLocal()
        user1 = _seed_user(db, name="A", phone="1111111111")
        user2 = _seed_user(db, name="B", phone="2222222222")
        product = _seed_product(db)
        sale = _seed_sale(db, user1.id)
        _seed_sale_item(db, sale.id, product.id)
        _seed_purchase_history(db, user1.id, sale.id)
        user2_id = user2.id
        db.close()

        res = client.get(f"/customers/{user2_id}/history")
        assert res.status_code == 200
        assert res.json() == []
