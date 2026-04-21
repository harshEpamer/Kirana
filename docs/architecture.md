# Kirana Store — Architecture

## Overview

A microservices-based kirana (local grocery) store management system built with FastAPI (backend) and React (frontend). Eight independent backend services communicate with a single shared SQLite database (`kirana.db`).

## Service Map

```
Browser (React 18 + Vite, port 5173)
    │
    ├── /auth     → auth-service      :8001  (register / login / JWT)
    ├── /catalog  → catalog-service   :8003  (browse products, filter, search)
    ├── /cart     → order-service     :8005  (checkout, coupon apply, stock deduct)
    │              coupon-service     :8006  (validate coupon)
    ├── /admin    → alert-service     :8007  (low-stock alerts)
    │              sales-service      :8004  (recent sales list)
    └── /inventory→ inventory-service :8002  (product CRUD, stock adjustment)
                   customer-service   :8008  (customer profiles, purchase history)
```

## Database Schema

All services share `kirana.db` (SQLite) at the project root. Each service opens the file via a relative path `../../kirana.db` from its service folder.

**Tables:**
- `users` — registered customers (phone + password_hash + address)
- `products` — product catalog with stock and reorder threshold
- `sales` — sale transactions (user, amounts, coupon, timestamp)
- `sale_items` — line items per sale (product, qty, unit_price)
- `purchase_history` — user ↔ sale junction for customer history
- `coupons` — discount codes (order_wise or product_wise)
- `stock_adjustments` — audit trail for all stock changes

## Authentication Flow

```
Client → POST /auth/login → auth-service
       ← JWT token (HS256, 24h expiry)
Client → includes header: Authorization: Bearer <token>
       → any protected endpoint on any service
```

Token secret: `JWT_SECRET` env var (default: `kirana-secret-key-change-in-production`)

## Data Flow — Checkout

```
CartPage
  → POST /orders/  (order-service :8005)
    ├── validates coupon in coupons table
    ├── checks stock in products table
    ├── creates sale + sale_items in DB
    ├── deducts stock from products table
    └── returns OrderOut (receipt)
```

## Running Locally

```powershell
# 1. Initialize database (run once from project root)
python scripts/init-db.py

# 2. Start all 8 backend services
.\scripts\start-all.ps1

# 3. Start frontend (from frontend/ directory)
cd frontend
npm install
npm run dev
```

Individual service:
```bash
cd backend/auth-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## API Conventions

| Convention | Value |
|---|---|
| Response format | JSON |
| Auth header | `Authorization: Bearer <token>` |
| CORS origin | `http://localhost:5173` |
| Health endpoint | `GET /health` on every service |
| Status codes | 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 404 Not Found |

## Git Workflow

- `main` — protected, Pranav merges only
- Feature branches: `feature/<code>` per owner (see context.txt for full map)
- No direct pushes to main
