from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Sale, SaleItem, Product
from schemas import SaleOut, SaleItemOut, SalesSummary

router = APIRouter(prefix="/api/sales", tags=["sales"])


@router.get("/", response_model=List[SaleOut])
def get_sales_by_date(
    date: Optional[str] = Query(default=None, description="YYYY-MM-DD, defaults to today"),
    db: Session = Depends(get_db),
):
    target_date = date or datetime.utcnow().strftime("%Y-%m-%d")

    sales = (
        db.query(Sale)
        .options(
            joinedload(Sale.user),
            joinedload(Sale.items).joinedload(SaleItem.product),
        )
        .filter(func.date(Sale.sale_time) == target_date)
        .order_by(Sale.sale_time.desc())
        .all()
    )

    result = []
    for sale in sales:
        items_out = [
            SaleItemOut(
                product_name=item.product.name if item.product else "Unknown",
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in sale.items
        ]
        result.append(SaleOut(
            id=sale.id,
            customer_name=sale.user.name if sale.user else None,
            customer_phone=sale.user.phone if sale.user else None,
            items=items_out,
            total_amount=sale.total_amount,
            discount_amount=sale.discount_amount,
            final_amount=sale.final_amount,
            coupon_code=sale.coupon_code,
            sale_time=sale.sale_time,
        ))

    return result


@router.get("/summary", response_model=SalesSummary)
def get_sales_summary(db: Session = Depends(get_db)):
    today = datetime.utcnow().strftime("%Y-%m-%d")

    revenue = (
        db.query(func.coalesce(func.sum(Sale.final_amount), 0.0))
        .filter(func.date(Sale.sale_time) == today)
        .scalar()
    )

    orders_count = (
        db.query(func.count(Sale.id))
        .filter(func.date(Sale.sale_time) == today)
        .scalar()
    )

    top_product_row = (
        db.query(
            Product.name,
            func.sum(SaleItem.quantity).label("total_qty"),
        )
        .join(SaleItem, SaleItem.product_id == Product.id)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .filter(func.date(Sale.sale_time) == today)
        .group_by(Product.id)
        .order_by(func.sum(SaleItem.quantity).desc())
        .first()
    )

    return SalesSummary(
        today_revenue=round(float(revenue), 2),
        today_orders=orders_count or 0,
        top_product_name=top_product_row[0] if top_product_row else None,
        top_product_qty=int(top_product_row[1]) if top_product_row else 0,
    )
