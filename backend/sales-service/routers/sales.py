from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Sale, SaleItem, Product
from schemas import SaleCreate, SaleOut, SaleItemOut

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("/", response_model=List[SaleOut])
def list_sales(db: Session = Depends(get_db)):
    sales = db.query(Sale).order_by(Sale.id.desc()).all()
    result = []
    for sale in sales:
        items = db.query(SaleItem).filter(SaleItem.sale_id == sale.id).all()
        out = SaleOut.model_validate(sale)
        out.items = [SaleItemOut.model_validate(i) for i in items]
        result.append(out)
    return result


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    items = db.query(SaleItem).filter(SaleItem.sale_id == sale.id).all()
    out = SaleOut.model_validate(sale)
    out.items = [SaleItemOut.model_validate(i) for i in items]
    return out


@router.post("/", response_model=SaleOut, status_code=201)
def create_sale(sale_in: SaleCreate, db: Session = Depends(get_db)):
    total = 0.0
    line_items = []

    for item in sale_in.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock_qty < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {item.product_id}")
        line_items.append((product, item.quantity))
        total += product.price * item.quantity

    discount = 0.0
    # Coupon validation is handled by order-service before calling this endpoint.
    # coupon_code is recorded here for receipt purposes only.

    final = total - discount
    sale = Sale(
        user_id=sale_in.user_id,
        total_amount=round(total, 2),
        discount_amount=round(discount, 2),
        final_amount=round(final, 2),
        coupon_code=sale_in.coupon_code,
        sale_time=datetime.utcnow().isoformat(),
    )
    db.add(sale)
    db.flush()  # get sale.id without committing

    items_out = []
    for product, qty in line_items:
        si = SaleItem(sale_id=sale.id, product_id=product.id, quantity=qty, unit_price=product.price)
        db.add(si)
        product.stock_qty -= qty
        items_out.append(si)

    db.commit()
    db.refresh(sale)
    out = SaleOut.model_validate(sale)
    out.items = [SaleItemOut.model_validate(i) for i in items_out]
    return out
