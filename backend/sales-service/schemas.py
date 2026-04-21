from pydantic import BaseModel
from typing import List, Optional


class SaleItemIn(BaseModel):
    product_id: int
    quantity: int


class SaleCreate(BaseModel):
    user_id: Optional[int] = None
    items: List[SaleItemIn]
    coupon_code: Optional[str] = None


class SaleItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class SaleOut(BaseModel):
    id: int
    user_id: Optional[int]
    total_amount: float
    discount_amount: float
    final_amount: float
    coupon_code: Optional[str]
    sale_time: Optional[str]
    items: List[SaleItemOut] = []

    class Config:
        from_attributes = True
