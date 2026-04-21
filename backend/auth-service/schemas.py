from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    name: str
    phone: str
    address: str
    password: str


class UserLogin(BaseModel):
    phone: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    address: str

    class Config:
        from_attributes = True
