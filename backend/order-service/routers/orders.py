from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import httpx

from database import get_db
from models import Sale, SaleItem, Product, PurchaseHistory, StockAdjustment, User
from schemas import CheckoutRequest, CheckoutResponse

router = APIRouter(prefix="/orders", tags=["orders"])

COUPON_SERVICE_URL = "http://localhost:8006"
ALERT_SERVICE_URL = "http://localhost:8007"


def _validate_coupon_remote(coupon_code: str, cart_total: float, product_ids: list[int]) -> float:
    with httpx.Client(timeout=5.0) as client:
        # Try without product_id first (handles order_wise coupons)
        resp = client.post(
            f"{COUPON_SERVICE_URL}/coupons/validate",
            json={"code": coupon_code, "order_total": cart_total},
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("valid"):
                return data["discount_amount"]

        # Try each product_id (handles product_wise coupons)
        for pid in product_ids:
            resp = client.post(
                f"{COUPON_SERVICE_URL}/coupons/validate",
                json={"code": coupon_code, "order_total": cart_total, "product_id": pid},
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("valid"):
                    return data["discount_amount"]

    return 0.0


def _check_alerts(product_id: int):
    try:
        with httpx.Client(timeout=3.0) as client:
            client.get(f"{ALERT_SERVICE_URL}/alerts/check/{product_id}")
    except httpx.RequestError:
        pass  # best-effort; don't fail the order


@router.post("/checkout", response_model=CheckoutResponse, status_code=201)
def checkout(req: CheckoutRequest, db: Session = Depends(get_db)):
    # 1. Validate user exists
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Validate all products exist and have sufficient stock
    line_items = []
    total = 0.0
    product_ids = []
    for item in req.cart:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock_qty < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name} (available: {product.stock_qty})",
            )
        line_items.append((product, item.quantity))
        total += product.price * item.quantity
        product_ids.append(product.id)

    # 3. Validate coupon via coupon-service
    discount = 0.0
    if req.coupon_code:
        try:
            discount = _validate_coupon_remote(req.coupon_code, total, product_ids)
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Coupon service unavailable")
        if discount == 0.0:
            raise HTTPException(status_code=400, detail="Invalid or inactive coupon")

    final = round(total - discount, 2)

    # 4. Create sale record
    sale = Sale(
        user_id=req.user_id,
        total_amount=round(total, 2),
        discount_amount=round(discount, 2),
        final_amount=final,
        coupon_code=req.coupon_code,
        sale_time=datetime.utcnow().isoformat(),
    )
    db.add(sale)
    db.flush()

    # 5. Insert sale_items + decrement stock + record stock_adjustments
    for product, qty in line_items:
        db.add(SaleItem(sale_id=sale.id, product_id=product.id, quantity=qty, unit_price=product.price))
        product.stock_qty -= qty
        db.add(
            StockAdjustment(
                product_id=product.id,
                adjustment_type="sale_deduct",
                quantity=qty,
                adjusted_at=datetime.utcnow().isoformat(),
            )
        )

    # 6. Insert purchase_history
    db.add(PurchaseHistory(user_id=req.user_id, sale_id=sale.id, recorded_at=datetime.utcnow().isoformat()))

    db.commit()
    db.refresh(sale)

    # 7. Check alerts for each product (best-effort, non-blocking)
    for product, _ in line_items:
        _check_alerts(product.id)

    return CheckoutResponse(
        order_id=sale.id,
        total_amount=sale.total_amount,
        discount_amount=sale.discount_amount,
        final_amount=sale.final_amount,
        coupon_applied=req.coupon_code if discount > 0 else None,
    )
