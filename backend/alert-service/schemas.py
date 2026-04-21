from pydantic import BaseModel


class LowStockAlert(BaseModel):
    id: int
    name: str
    category: str
    stock_qty: int
    reorder_threshold: int
    shortfall: int
    suggested_reorder_qty: int = 0

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_products: int
    total_stock_value: float
    low_stock_count: int
    today_revenue: float
    today_orders: int


class ProductCheckResult(BaseModel):
    alert: bool
    product_id: int
    stock_qty: int
    threshold: int
