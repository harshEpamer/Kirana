from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from database import get_db
from models import User, PurchaseHistory, Sale, SaleItem, Product
from schemas import CustomerSummary, PurchaseRecord, PurchaseItem

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/", response_model=List[CustomerSummary])
def list_customers(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id).all()
    result = []
    for u in users:
        stats = (
            db.query(
                func.count(Sale.id).label("total_orders"),
                func.coalesce(func.sum(Sale.final_amount), 0).label("total_spent"),
            )
            .filter(Sale.user_id == u.id)
            .first()
        )
        result.append(
            CustomerSummary(
                id=u.id,
                name=u.name,
                phone=u.phone,
                address=u.address,
                total_orders=stats.total_orders,
                total_spent=round(stats.total_spent, 2),
            )
        )
    return result


@router.get("/{user_id}/history", response_model=List[PurchaseRecord])
def get_purchase_history(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")

    history = (
        db.query(PurchaseHistory)
        .filter(PurchaseHistory.user_id == user_id)
        .order_by(PurchaseHistory.id.desc())
        .all()
    )
    records = []
    for ph in history:
        sale = db.query(Sale).filter(Sale.id == ph.sale_id).first()
        if not sale:
            continue
        sale_items = db.query(SaleItem).filter(SaleItem.sale_id == sale.id).all()
        items = []
        for si in sale_items:
            product = db.query(Product).filter(Product.id == si.product_id).first()
            items.append(
                PurchaseItem(
                    product_name=product.name if product else f"Product #{si.product_id}",
                    quantity=si.quantity,
                    unit_price=si.unit_price,
                )
            )
        records.append(
            PurchaseRecord(
                sale_id=sale.id,
                sale_time=sale.sale_time,
                items=items,
                total_amount=sale.total_amount,
                discount_amount=sale.discount_amount,
                final_amount=sale.final_amount,
                coupon_code=sale.coupon_code,
            )
        )
    return records
