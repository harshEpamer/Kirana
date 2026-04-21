from sqlalchemy import Column, Integer, String, Text, Float
from database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    phone         = Column(String, nullable=False, unique=True)
    address       = Column(Text, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at    = Column(String)


class Product(Base):
    __tablename__ = "products"

    id       = Column(Integer, primary_key=True, index=True)
    name     = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price    = Column(Float, nullable=False)


class Sale(Base):
    __tablename__ = "sales"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer)
    total_amount    = Column(Float, nullable=False)
    discount_amount = Column(Float, nullable=False, default=0)
    final_amount    = Column(Float, nullable=False)
    coupon_code     = Column(String)
    sale_time       = Column(String)


class SaleItem(Base):
    __tablename__ = "sale_items"

    id         = Column(Integer, primary_key=True, index=True)
    sale_id    = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity   = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)


class PurchaseHistory(Base):
    __tablename__ = "purchase_history"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, nullable=False)
    sale_id     = Column(Integer, nullable=False)
    recorded_at = Column(String)
