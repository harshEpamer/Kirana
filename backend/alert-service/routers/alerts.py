from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date

from database import get_db
from models import Product, Sale
from schemas import LowStockAlert, DashboardStats, ProductCheckResult

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
            suggested_reorder_qty=max(1, (p.reorder_threshold * 2) - p.stock_qty),
        )
        for p in products
    ]


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    today_str = date.today().isoformat()

    total_products = db.query(func.count(Product.id)).scalar() or 0
    total_stock_value = db.query(
        func.coalesce(func.sum(Product.price * Product.stock_qty), 0.0)
    ).scalar() or 0.0
    low_stock_count = (
        db.query(func.count(Product.id))
        .filter(Product.stock_qty < Product.reorder_threshold)
        .scalar()
        or 0
    )
    today_revenue = (
        db.query(func.coalesce(func.sum(Sale.final_amount), 0.0))
        .filter(Sale.sale_time.like(f"{today_str}%"))
        .scalar()
        or 0.0
    )
    today_orders = (
        db.query(func.count(Sale.id))
        .filter(Sale.sale_time.like(f"{today_str}%"))
        .scalar()
        or 0
    )

    return DashboardStats(
        total_products=total_products,
        total_stock_value=round(float(total_stock_value), 2),
        low_stock_count=low_stock_count,
        today_revenue=round(float(today_revenue), 2),
        today_orders=today_orders,
    )


@router.get("/check/{product_id}", response_model=ProductCheckResult)
def check_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductCheckResult(
        alert=product.stock_qty < product.reorder_threshold,
        product_id=product.id,
        stock_qty=product.stock_qty,
        threshold=product.reorder_threshold,
    )
