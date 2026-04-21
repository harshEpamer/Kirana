from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Product
from schemas import LowStockAlert

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/low-stock", response_model=List[LowStockAlert])
def get_low_stock_alerts(db: Session = Depends(get_db)):
    products = (
        db.query(Product)
        .filter(Product.stock_qty < Product.reorder_threshold)
        .order_by(Product.stock_qty.asc())
        .all()
    )
    return [
        LowStockAlert(
            id=p.id,
            name=p.name,
            category=p.category,
            stock_qty=p.stock_qty,
            reorder_threshold=p.reorder_threshold,
            shortfall=p.reorder_threshold - p.stock_qty,
        )
        for p in products
    ]
