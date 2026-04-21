from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    phone         = Column(String, nullable=False, unique=True)
    address       = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at    = Column(String)

    sales = relationship("Sale", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id                = Column(Integer, primary_key=True, index=True)
    name              = Column(String, nullable=False)
    category          = Column(String, nullable=False)
    price             = Column(Float, nullable=False)
    stock_qty         = Column(Integer, nullable=False, default=0)
    reorder_threshold = Column(Integer, nullable=False, default=10)
    image_url         = Column(String, default="")
    created_at        = Column(String)

    sale_items = relationship("SaleItem", back_populates="product")


class Sale(Base):
    __tablename__ = "sales"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"))
    total_amount    = Column(Float, nullable=False)
    discount_amount = Column(Float, nullable=False, default=0)
    final_amount    = Column(Float, nullable=False)
    coupon_code     = Column(String)
    sale_time       = Column(String)

    user  = relationship("User", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id         = Column(Integer, primary_key=True, index=True)
    sale_id    = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity   = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    sale    = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
