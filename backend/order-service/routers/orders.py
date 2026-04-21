from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import Sale, SaleItem, Coupon, Product
from schemas import OrderCreate, OrderOut, OrderItemOut

router = APIRouter(prefix="/orders", tags=["orders"])


def _apply_coupon(coupon: Coupon, items: list, total: float) -> float:
    """Return the discount amount for a given coupon and cart."""
    if coupon.discount_type == "order_wise":
        return min(coupon.discount_value, total)
    elif coupon.discount_type == "product_wise":
        discount = 0.0
        for product, qty in items:
            if product.id == coupon.product_id:
                discount += coupon.discount_value * qty
        return min(discount, total)
    return 0.0


@router.post("/", response_model=OrderOut, status_code=201)
def checkout(order_in: OrderCreate, db: Session = Depends(get_db)):
    total = 0.0
    line_items = []

    for item in order_in.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock_qty < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {item.product_id}")
        line_items.append((product, item.quantity))
        total += product.price * item.quantity

    discount = 0.0
    coupon = None
    if order_in.coupon_code:
        coupon = (
            db.query(Coupon)
            .filter(Coupon.code == order_in.coupon_code, Coupon.is_active == 1)
            .first()
        )
        if not coupon:
            raise HTTPException(status_code=400, detail="Invalid or inactive coupon")
        discount = _apply_coupon(coupon, line_items, total)

    final = round(total - discount, 2)
    sale = Sale(
        user_id=order_in.user_id,
        total_amount=round(total, 2),
        discount_amount=round(discount, 2),
        final_amount=final,
        coupon_code=order_in.coupon_code,
        sale_time=datetime.utcnow().isoformat(),
    )
    db.add(sale)
    db.flush()

    items_out = []
    for product, qty in line_items:
        si = SaleItem(sale_id=sale.id, product_id=product.id, quantity=qty, unit_price=product.price)
        db.add(si)
        product.stock_qty -= qty
        items_out.append(OrderItemOut(product_id=product.id, quantity=qty, unit_price=product.price))

    db.commit()
    db.refresh(sale)

    return OrderOut(
        sale_id=sale.id,
        user_id=sale.user_id,
        total_amount=sale.total_amount,
        discount_amount=sale.discount_amount,
        final_amount=sale.final_amount,
        coupon_code=sale.coupon_code,
        sale_time=sale.sale_time,
        items=items_out,
    )
