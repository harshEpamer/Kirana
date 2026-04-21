from pydantic import BaseModel
from typing import Optional


class UserRegister(BaseModel):
    name: str
    phone: str
    address: str
    password: str


class UserLogin(BaseModel):
    phone: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    role: str = "customer"


class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    address: str

    class Config:
        from_attributes = True
