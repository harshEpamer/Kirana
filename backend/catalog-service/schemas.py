from pydantic import BaseModel
from typing import Optional


class ProductOut(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock_qty: int
    image_url: str
    created_at: Optional[str]

    class Config:
        from_attributes = True
