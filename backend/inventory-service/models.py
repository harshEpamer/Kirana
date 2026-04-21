from sqlalchemy import Column, Integer, String, Float, Text
from database import Base


class Product(Base):
    __tablename__ = "products"

    id                = Column(Integer, primary_key=True, index=True)
    name              = Column(String, nullable=False)
    category          = Column(String, nullable=False)
    price             = Column(Float, nullable=False)
    stock_qty         = Column(Integer, nullable=False, default=0)
    reorder_threshold = Column(Integer, nullable=False, default=10)
    image_url         = Column(Text, default="")
    created_at        = Column(String)


class StockAdjustment(Base):
    __tablename__ = "stock_adjustments"

    id              = Column(Integer, primary_key=True, index=True)
    product_id      = Column(Integer, nullable=False)
    adjustment_type = Column(String, nullable=False)
    quantity        = Column(Integer, nullable=False)
    adjusted_at     = Column(String)
