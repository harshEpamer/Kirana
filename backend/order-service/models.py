from sqlalchemy import Column, Integer, String, Float
from database import Base


class Coupon(Base):
    __tablename__ = "coupons"

    id             = Column(Integer, primary_key=True, index=True)
    code           = Column(String, nullable=False, unique=True)
    discount_type  = Column(String, nullable=False)
    discount_value = Column(Float, nullable=False)
    product_id     = Column(Integer)
    is_active      = Column(Integer, nullable=False, default=1)


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


class Product(Base):
    __tablename__ = "products"

    id        = Column(Integer, primary_key=True, index=True)
    name      = Column(String, nullable=False)
    price     = Column(Float, nullable=False)
    stock_qty = Column(Integer, nullable=False, default=0)
