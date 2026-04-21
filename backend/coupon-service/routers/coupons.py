from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Coupon
from schemas import CouponCreate, CouponOut, ValidateRequest, ValidateResponse

router = APIRouter(prefix="/coupons", tags=["coupons"])


@router.get("/", response_model=List[CouponOut])
def list_coupons(db: Session = Depends(get_db)):
    return db.query(Coupon).all()


@router.post("/", response_model=CouponOut, status_code=201)
def create_coupon(coupon_in: CouponCreate, db: Session = Depends(get_db)):
    if db.query(Coupon).filter(Coupon.code == coupon_in.code).first():
        raise HTTPException(status_code=400, detail="Coupon code already exists")
    coupon = Coupon(**coupon_in.model_dump())
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


@router.delete("/{coupon_id}", status_code=204)
def deactivate_coupon(coupon_id: int, db: Session = Depends(get_db)):
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    coupon.is_active = 0
    db.commit()


@router.post("/validate", response_model=ValidateResponse)
def validate_coupon(req: ValidateRequest, db: Session = Depends(get_db)):
    coupon = (
        db.query(Coupon)
        .filter(Coupon.code == req.code, Coupon.is_active == 1)
        .first()
    )
    if not coupon:
        return ValidateResponse(valid=False, discount_amount=0.0, message="Invalid or inactive coupon")

    discount = 0.0
    if coupon.discount_type == "order_wise":
        discount = min(coupon.discount_value, req.order_total)
    elif coupon.discount_type == "product_wise":
        if req.product_id and coupon.product_id == req.product_id:
            discount = coupon.discount_value
        else:
            return ValidateResponse(valid=False, discount_amount=0.0, message="Coupon not applicable to this product")

    return ValidateResponse(valid=True, discount_amount=round(discount, 2), message="Coupon applied")
