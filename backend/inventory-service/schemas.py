from pydantic import BaseModel
from typing import Optional, Literal, List


class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    stock_qty: int = 0
    reorder_threshold: int = 10
    image_url: str = ""


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock_qty: Optional[int] = None
    reorder_threshold: Optional[int] = None
    image_url: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock_qty: int
    reorder_threshold: int
    image_url: str
    created_at: Optional[str]

    class Config:
        from_attributes = True


class StockAdjustRequest(BaseModel):
    product_id: int
    adjustment_type: Literal["add", "set", "sale_deduct"]
    quantity: int


class StockPatchRequest(BaseModel):
    adjustment_type: Literal["add", "set", "sale_deduct"]
    quantity: int


class StockAdjustOut(BaseModel):
    id: int
    product_id: int
    adjustment_type: str
    quantity: int
    adjusted_at: Optional[str]

    class Config:
        from_attributes = True


class BulkImportRequest(BaseModel):
    products: List[ProductCreate]


class BulkImportResponse(BaseModel):
    inserted: int


class StockLogEntry(BaseModel):
    id: int
    product_id: int
    product_name: str
    adjustment_type: str
    quantity: int
    adjusted_at: Optional[str]


class BulkCreateResponse(BaseModel):
    created: int
    products: List[ProductOut]


class ReorderItem(BaseModel):
    product_id: int
    name: str
    category: str
    stock_qty: int
    reorder_threshold: int
    suggested_qty: int

    class Config:
        from_attributes = True
