from pydantic import BaseModel


class LowStockAlert(BaseModel):
    id: int
    name: str
    category: str
    stock_qty: int
    reorder_threshold: int
    shortfall: int

    class Config:
        from_attributes = True
