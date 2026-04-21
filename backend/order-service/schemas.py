from pydantic import BaseModel
from typing import List, Optional


class CartItem(BaseModel):
    product_id: int
    quantity: int


class CheckoutRequest(BaseModel):
    user_id: int
    cart: List[CartItem]
    coupon_code: Optional[str] = None


class CheckoutResponse(BaseModel):
    order_id: int
    total_amount: float
    discount_amount: float
    final_amount: float
    coupon_applied: Optional[str] = None
