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
