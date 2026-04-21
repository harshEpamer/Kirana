from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, PurchaseHistory, Sale
from schemas import CustomerOut, PurchaseOut

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/", response_model=List[CustomerOut])
def list_customers(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id).all()


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == customer_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    return user


@router.get("/{customer_id}/history", response_model=List[PurchaseOut])
def get_purchase_history(customer_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == customer_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")

    history = (
        db.query(PurchaseHistory)
        .filter(PurchaseHistory.user_id == customer_id)
        .order_by(PurchaseHistory.id.desc())
        .all()
    )
    result = []
    for ph in history:
        sale = db.query(Sale).filter(Sale.id == ph.sale_id).first()
        if sale:
            result.append(PurchaseOut(sale_id=sale.id, final_amount=sale.final_amount, sale_time=sale.sale_time))
    return result
