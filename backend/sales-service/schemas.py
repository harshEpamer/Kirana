from pydantic import BaseModel
from typing import List, Optional


class SaleItemOut(BaseModel):
    product_name: str
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class SaleOut(BaseModel):
    id: int
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    items: List[SaleItemOut] = []
    total_amount: float
    discount_amount: float
    final_amount: float
    coupon_code: Optional[str] = None
    sale_time: Optional[str] = None

    class Config:
        from_attributes = True


class SalesSummary(BaseModel):
    today_revenue: float
    today_orders: int
    top_product_name: Optional[str] = None
    top_product_qty: int = 0
