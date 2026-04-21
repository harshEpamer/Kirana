from pydantic import BaseModel
from typing import Optional, List


class PurchaseItem(BaseModel):
    product_name: str
    quantity: int
    unit_price: float


class PurchaseRecord(BaseModel):
    sale_id: int
    sale_time: Optional[str]
    items: List[PurchaseItem]
    total_amount: float
    discount_amount: float
    final_amount: float
    coupon_code: Optional[str]


class CustomerSummary(BaseModel):
    id: int
    name: str
    phone: str
    address: str
    total_orders: int
    total_spent: float

    class Config:
        from_attributes = True
