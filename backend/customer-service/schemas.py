from pydantic import BaseModel
from typing import Optional, List


class CustomerOut(BaseModel):
    id: int
    name: str
    phone: str
    address: str
    created_at: Optional[str]

    class Config:
        from_attributes = True


class PurchaseOut(BaseModel):
    sale_id: int
    final_amount: float
    sale_time: Optional[str]

    class Config:
        from_attributes = True
