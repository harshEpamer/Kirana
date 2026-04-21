from sqlalchemy import Column, Integer, String, Text, Float
from database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    phone         = Column(String, nullable=False, unique=True)
    address       = Column(Text, nullable=False)
    created_at    = Column(String)


class PurchaseHistory(Base):
    __tablename__ = "purchase_history"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, nullable=False)
    sale_id     = Column(Integer, nullable=False)
    recorded_at = Column(String)


class Sale(Base):
    __tablename__ = "sales"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer)
    final_amount = Column(Float, nullable=False)
    sale_time    = Column(String)
