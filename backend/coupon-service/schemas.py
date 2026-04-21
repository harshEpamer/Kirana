from pydantic import BaseModel
from typing import Optional, Literal


class CouponCreate(BaseModel):
    code: str
    discount_type: Literal["product_wise", "order_wise"]
    discount_value: float
    product_id: Optional[int] = None


class CouponOut(BaseModel):
    id: int
    code: str
    discount_type: str
    discount_value: float
    product_id: Optional[int]
    is_active: int

    class Config:
        from_attributes = True


class ValidateRequest(BaseModel):
    code: str
    order_total: float
    product_id: Optional[int] = None


class ValidateResponse(BaseModel):
    valid: bool
    discount_amount: float
    message: str
