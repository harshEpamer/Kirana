from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Product, StockAdjustment
from schemas import (
    ProductCreate, ProductUpdate, ProductOut,
    StockAdjustRequest, StockAdjustOut,
    BulkCreateResponse, ReorderItem,
)

router = APIRouter(prefix="/inventory", tags=["inventory"])


# ── List all products ───────────────────────────────────────────────────────
@router.get("/products", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


# ── Low-stock items (MUST be before /{product_id}) ─────────────────────────
@router.get("/low-stock", response_model=List[ProductOut])
def low_stock(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.stock_qty < Product.reorder_threshold).all()


# ── Reorder suggestions (MUST be before /{product_id}) ─────────────────────
@router.get("/reorder", response_model=List[ReorderItem])
def reorder_list(db: Session = Depends(get_db)):
    items = db.query(Product).filter(Product.stock_qty < Product.reorder_threshold).all()
    return [
        ReorderItem(
            product_id=p.id,
            name=p.name,
            category=p.category,
            stock_qty=p.stock_qty,
            reorder_threshold=p.reorder_threshold,
            suggested_qty=p.reorder_threshold * 2 - p.stock_qty,
        )
        for p in items
    ]


# ── Bulk insert (MUST be before /{product_id}) ─────────────────────────────
@router.post("/products/bulk", response_model=BulkCreateResponse, status_code=201)
def bulk_create(products_in: List[ProductCreate], db: Session = Depends(get_db)):
    created = []
    for p_in in products_in:
        product = Product(**p_in.model_dump(), created_at=datetime.utcnow().isoformat())
        db.add(product)
        db.flush()
        created.append(product)
    db.commit()
    for p in created:
        db.refresh(p)
    return BulkCreateResponse(created=len(created), products=created)


# ── Single product by ID ───────────────────────────────────────────────────
@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products", response_model=ProductOut, status_code=201)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**product_in.model_dump(), created_at=datetime.utcnow().isoformat())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, updates: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in updates.model_dump(exclude_none=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()


@router.post("/stock-adjust", response_model=StockAdjustOut, status_code=201)
def adjust_stock(req: StockAdjustRequest, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == req.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if req.adjustment_type == "add":
        product.stock_qty += req.quantity
    elif req.adjustment_type == "set":
        product.stock_qty = req.quantity
    elif req.adjustment_type == "sale_deduct":
        if product.stock_qty < req.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        product.stock_qty -= req.quantity

    adj = StockAdjustment(
        product_id=req.product_id,
        adjustment_type=req.adjustment_type,
        quantity=req.quantity,
        adjusted_at=datetime.utcnow().isoformat(),
    )
    db.add(adj)
    db.commit()
    db.refresh(adj)
    return adj
