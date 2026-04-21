from pydantic import BaseModel
from typing import List, Optional


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    user_id: Optional[int] = None
    items: List[OrderItemIn]
    coupon_code: Optional[str] = None


class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    sale_id: int
    user_id: Optional[int]
    total_amount: float
    discount_amount: float
    final_amount: float
    coupon_code: Optional[str]
    sale_time: Optional[str]
    items: List[OrderItemOut] = []
