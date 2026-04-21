from sqlalchemy import Column, Integer, String, Text
from database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    phone         = Column(String, nullable=False, unique=True)
    address       = Column(Text, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at    = Column(String)
