# Requirements.md — Local Kirana Store Inventory System
> Gen AI Kata | No-Human Code Hackathon | 2-Hour Sprint | GitHub Copilot Agents Only

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 (Vite) |
| Backend | FastAPI (Python 3.11+) |
| Database | SQLite3 (via SQLAlchemy) |
| Auth | JWT (python-jose + passlib) |
| Styling | Tailwind CSS |
| Routing | React Router v6 |
| HTTP | Native fetch API |

---

## Microservices — Ports

| Service | Port | Owner |
|---|---|---|
| auth-service | 8001 | Aryen Garg |
| inventory-service | 8002 | Pratyush Ojha |
| catalog-service | 8003 | Harshvardhan Singh |
| sales-service | 8004 | Sanidhya Shandilya |
| order-service | 8005 | Atharv Singh |
| coupon-service | 8006 | Atharv Singh |
| alert-service | 8007 | Om Satyam Panda |
| customer-service | 8008 | Aryen Garg |
| Frontend (React) | 5173 | Harshvardhan Singh |

---

## Folder Structure

```
kirana-store/
├── backend/
│   ├── auth-service/        → main.py, models.py, schemas.py, database.py, routers/auth.py, requirements.txt
│   ├── inventory-service/   → main.py, models.py, schemas.py, database.py, routers/inventory.py, requirements.txt
│   ├── catalog-service/     → main.py, models.py, schemas.py, database.py, routers/catalog.py, requirements.txt
│   ├── sales-service/       → main.py, models.py, schemas.py, database.py, routers/sales.py, requirements.txt
│   ├── order-service/       → main.py, models.py, schemas.py, database.py, routers/orders.py, requirements.txt
│   ├── coupon-service/      → main.py, models.py, schemas.py, database.py, routers/coupons.py, requirements.txt
│   ├── alert-service/       → main.py, models.py, schemas.py, database.py, routers/alerts.py, requirements.txt
│   └── customer-service/    → main.py, models.py, schemas.py, database.py, routers/customers.py, requirements.txt
├── frontend/
│   └── src/
│       ├── pages/
│       ├── components/
│       ├── context/
│       ├── api/             → one file per service e.g. authApi.js, catalogApi.js
│       └── config.js        → base URLs for all 8 services
├── db/
│   └── schema.sql
├── docs/
│   └── architecture.md
└── README.md
```

---

## Database Schema — db/schema.sql
> Run once at startup. All services share `kirana.db` at the project root.

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT    NOT NULL,
  phone         TEXT    NOT NULL UNIQUE,
  address       TEXT    NOT NULL,
  password_hash TEXT    NOT NULL,
  created_at    TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS products (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  name              TEXT  NOT NULL,
  category          TEXT  NOT NULL,
  price             REAL  NOT NULL,
  stock_qty         INTEGER NOT NULL DEFAULT 0,
  reorder_threshold INTEGER NOT NULL DEFAULT 10,
  image_url         TEXT  DEFAULT '',
  created_at        TEXT  DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sales (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id         INTEGER REFERENCES users(id),
  total_amount    REAL    NOT NULL,
  discount_amount REAL    NOT NULL DEFAULT 0,
  final_amount    REAL    NOT NULL,
  coupon_code     TEXT    DEFAULT NULL,
  sale_time       TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sale_items (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  sale_id     INTEGER NOT NULL REFERENCES sales(id),
  product_id  INTEGER NOT NULL REFERENCES products(id),
  quantity    INTEGER NOT NULL,
  unit_price  REAL    NOT NULL
);

CREATE TABLE IF NOT EXISTS purchase_history (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id     INTEGER NOT NULL REFERENCES users(id),
  sale_id     INTEGER NOT NULL REFERENCES sales(id),
  recorded_at TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS coupons (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  code            TEXT    NOT NULL UNIQUE,
  discount_type   TEXT    NOT NULL CHECK(discount_type IN ('product_wise','order_wise')),
  discount_value  REAL    NOT NULL,
  product_id      INTEGER REFERENCES products(id),
  is_active       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS stock_adjustments (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id      INTEGER NOT NULL REFERENCES products(id),
  adjustment_type TEXT    NOT NULL CHECK(adjustment_type IN ('add','set','sale_deduct')),
  quantity        INTEGER NOT NULL,
  adjusted_at     TEXT    DEFAULT (datetime('now'))
);

-- Seed products
INSERT OR IGNORE INTO products (name, category, price, stock_qty, reorder_threshold) VALUES
  ('Basmati Rice 1kg',    'Grains',  85.0,  50, 10),
  ('Toor Dal 500g',       'Pulses',  65.0,  30,  8),
  ('Sunflower Oil 1L',    'Oils',   135.0,  20,  5),
  ('Aashirvaad Atta 5kg', 'Flour',  280.0,  15,  5),
  ('Amul Butter 100g',    'Dairy',   55.0,  40, 10),
  ('Parle-G Biscuits',    'Snacks',  10.0, 100, 20),
  ('Maggi Noodles',       'Instant', 14.0,  80, 15),
  ('Tata Salt 1kg',       'Spices',  22.0,  60, 10),
  ('Dettol Soap 75g',     'Hygiene', 40.0,   8,  5),
  ('Colgate 100g',        'Hygiene', 59.0,   3, 10);

-- Seed coupons
INSERT OR IGNORE INTO coupons (code, discount_type, discount_value, product_id) VALUES
  ('SAVE10', 'order_wise',   10.0, NULL),
  ('FLAT50', 'order_wise',   50.0, NULL),
  ('RICE20', 'product_wise', 20.0, 1);
```

---

## Global Conventions — ALL agents must follow

### Backend
- Every service: standalone FastAPI app, entry point `main.py`, `app = FastAPI(title="<service-name>")`
- Enable CORS: `allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"]`
- Every `requirements.txt` must include: `fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt]`
- Run command: `uvicorn main:app --reload --port <PORT>`
- All responses: JSON. Use correct HTTP status codes (200, 201, 400, 401, 404)
- DB path: `../../kirana.db` (relative from each service folder to project root)
- Follow SOLID, KISS, DRY, YAGNI

### Frontend
- Base URLs in `src/config.js`:
```js
export const API = {
  auth:      "http://localhost:8001",
  inventory: "http://localhost:8002",
  catalog:   "http://localhost:8003",
  sales:     "http://localhost:8004",
  orders:    "http://localhost:8005",
  coupons:   "http://localhost:8006",
  alerts:    "http://localhost:8007",
  customers: "http://localhost:8008",
};
```
- JWT token stored in `localStorage` as `kirana_token`
- All authenticated requests send header: `Authorization: Bearer <token>`
- Use React Router v6 for navigation
- All forms: controlled components via `useState`

---

## Git Workflow

```
main  ← protected, Pranav merges only
  └── feature/S-01  ← Pranav: scaffold + schema + architecture
  └── feature/U-01  ← Aryen: auth service + frontend auth pages
  └── feature/U-02  ← Aryen: customer service + purchase history
  └── feature/U-03  ← Atharv: order service + checkout page
  └── feature/U-04  ← Atharv: coupon service + coupon component
  └── feature/U-05  ← Harshvardhan: catalog service + catalog page
  └── feature/U-06  ← Harshvardhan: cart context + navbar
  └── feature/A-01  ← Om Satyam: alert service + admin dashboard
  └── feature/A-02  ← Om Satyam: low stock alerts + reorder page
  └── feature/A-03  ← Pratyush: inventory service CRUD + bulk import
  └── feature/A-04  ← Pratyush: stock update + adjustment log
  └── feature/A-05  ← Sanidhya: sales service + admin sales page
  └── feature/A-06  ← Sanidhya: customer management admin page
```

```bash
# Each member runs:
git checkout -b feature/<ticket-id>
# paste agent output into correct service folder
git add .
git commit -m "<ticket-id>: short description"
git push origin feature/<ticket-id>
# open PR on GitHub → assign Pranav as reviewer → merge to main
```

---

## SDLC Timeline

```
0:00 – 0:20   Phase 1 — Planning: Pranav sets up repo, pushes schema.sql and scaffold
0:20 – 1:30   Phase 2 — Development: Everyone runs their Copilot agent, pushes feature branch
1:30 – 1:40   Phase 3 — Integration: Pranav merges all PRs, resolves conflicts
1:40 – 1:50   Phase 4 — Smoke Test: Start all 8 services + frontend, run demo flow
1:50 – 2:00   Phase 5 — Presentation Prep: Export diagrams, rehearse demo order
```

---

---

# AGENT PROMPTS
> Each person copies their section below, pastes it as-is into their GitHub Copilot agent, and saves the output to the correct service folder.

---

## PRANAV — S-01: Scaffold, Schema, Architecture & Integration

```
You are a senior software engineer scaffolding a Local Kirana Store Inventory System.

Tech stack: FastAPI (Python 3.11), React 18 (Vite), SQLite3 (SQLAlchemy), Tailwind CSS.
The backend is split into 8 microservices each on its own port. The shared database file
is kirana.db at the project root.

Generate the following files exactly:

1. db/schema.sql
   Full SQLite schema with these tables: users, products, sales, sale_items,
   purchase_history, coupons, stock_adjustments.
   Include PRAGMA foreign_keys = ON.
   Seed 10 sample Kirana products and 3 coupons: SAVE10 (10% order-wise),
   FLAT50 (flat 50 rupees off), RICE20 (20% off product_id=1).

2. README.md
   Setup instructions:
   - Clone repo
   - Run schema: sqlite3 kirana.db < db/schema.sql
   - For each backend service: cd backend/<service> && pip install -r requirements.txt && uvicorn main:app --reload --port <PORT>
   - Frontend: cd frontend && npm install && npm run dev
   - Service port table (auth=8001, inventory=8002, catalog=8003, sales=8004, order=8005, coupon=8006, alert=8007, customer=8008)

3. frontend/src/config.js
   Export const API object with base URLs for all 8 services on localhost.

4. docs/architecture.md
   A Mermaid flowchart (flowchart TD) showing:
   - React Frontend at the top
   - 8 FastAPI microservices in the middle (each labeled with port)
   - SQLite kirana.db at the bottom
   - Arrows from frontend to each service, and each service to DB

5. docs/sequence.md
   A Mermaid sequenceDiagram showing the full purchase flow:
   Admin adds product → User browses catalog → User adds to cart →
   User applies coupon → Checkout triggered → sale recorded →
   stock auto-decremented → low-stock check → alert fired if below threshold →
   Admin views dashboard alert → Admin triggers reorder.

6. backend/init_db.py
   A Python script that runs db/schema.sql against kirana.db.
   Usage: python backend/init_db.py

Follow SOLID, KISS, DRY. Output only working code and files.
```

---

## PRANAV — S-02: Integration Glue

```
You are the integration engineer for a Local Kirana Store Inventory System.
Backend: FastAPI microservices. Frontend: React 18 (Vite). DB: SQLite3.

Generate:

1. A git-workflow.md file:
   Explains the branching strategy: main is protected, each member works on
   feature/<ticket-id>, opens a PR, Pranav reviews and merges.
   Include exact git commands: checkout, add, commit, push, PR creation.

2. backend/order-service/routers/orders.py
   After recording a sale, this service must call alert-service at
   http://localhost:8007/api/alerts/check/<product_id> for every product in the order.
   Use httpx for async HTTP calls between services.
   Add httpx to requirements.txt for order-service.

3. frontend/src/components/Navbar.jsx
   Top nav bar with:
   - App name "Kirana Store" on the left
   - Links: Catalog, My Orders
   - Cart icon with item count badge (reads from CartContext)
   - Username from AuthContext on the right
   - Logout button that clears localStorage and redirects to /login
   - If user is admin (role === 'admin'), show Admin link instead

4. frontend/src/App.jsx
   React Router v6 routes:
   Public: /login, /register
   User (protected): /catalog, /cart, /checkout, /orders
   Admin (protected): /admin/dashboard, /admin/inventory, /admin/stock,
                       /admin/alerts, /admin/sales, /admin/customers
   Wrap protected routes in an AuthGuard component that checks localStorage
   for kirana_token and redirects to /login if missing.

Follow SOLID, KISS, DRY. Output only working code.
```

---

## ARYEN — U-01: Auth Service + Frontend Auth Pages

```
You are building the Authentication microservice for a Local Kirana Store Inventory System.
Tech: FastAPI (Python 3.11), SQLite3 (SQLAlchemy), JWT (python-jose + passlib).
This service runs on port 8001. DB file path: ../../kirana.db (relative to service folder).
CORS must allow: http://localhost:5173.

Generate these files inside backend/auth-service/:

1. database.py
   SQLAlchemy engine pointing to ../../kirana.db.
   SessionLocal factory and Base declarative base.
   get_db() dependency.

2. models.py
   User SQLAlchemy model mapped to the users table:
   id, name, phone, address, password_hash, created_at.

3. schemas.py
   Pydantic models:
   - UserRegister: name, phone, address, password
   - UserLogin: phone, password
   - TokenResponse: access_token, token_type, user_id, name, role

4. routers/auth.py
   FastAPI router with prefix /api/auth:
   POST /register → hash password with passlib bcrypt → insert user → return 201
   POST /login → verify password → generate JWT (expire 8h, secret="kirana_secret_key")
     → return TokenResponse
   GET /me → requires Bearer token → returns current user info

5. main.py
   FastAPI app on port 8001, CORS enabled, include auth router.

6. requirements.txt
   fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt]

Also generate these frontend files:

7. frontend/src/context/AuthContext.jsx
   React context with: user state, login(token, userData), logout().
   Persist token to localStorage key "kirana_token".
   On mount, decode token if present and restore user state.

8. frontend/src/api/authApi.js
   Functions: registerUser(data), loginUser(data), getMe(token).
   Base URL: http://localhost:8001.

9. frontend/src/pages/Login.jsx
   Controlled form: Phone, Password. Submit → POST /api/auth/login.
   On success: save token, set AuthContext, redirect to /catalog.
   Show error message on failure.

10. frontend/src/pages/Register.jsx
    Controlled form: Name, Phone, Address, Password.
    Submit → POST /api/auth/register. On success redirect to /login.

Follow SOLID, KISS, DRY. Output only working code.
```

---

## ARYEN — U-02: Customer Service + Purchase History

```
You are building the Customer microservice for a Local Kirana Store Inventory System.
Tech: FastAPI (Python 3.11), SQLite3 (SQLAlchemy).
This service runs on port 8008. DB file path: ../../kirana.db.
CORS must allow: http://localhost:5173.

Generate these files inside backend/customer-service/:

1. database.py — SQLAlchemy engine, SessionLocal, get_db(), Base.

2. models.py
   SQLAlchemy models for: users, sales, sale_items, products, purchase_history.
   Read-only — this service only reads, not writes, sales data.

3. schemas.py
   Pydantic models:
   - PurchaseItem: product_name, quantity, unit_price
   - PurchaseRecord: sale_id, sale_time, items (list of PurchaseItem),
     total_amount, discount_amount, final_amount, coupon_code
   - CustomerSummary: id, name, phone, address, total_orders, total_spent

4. routers/customers.py
   FastAPI router with prefix /api/customers:
   GET /              → returns list of CustomerSummary (admin use)
   GET /{user_id}/history → returns list of PurchaseRecord for that user

5. main.py — FastAPI app, CORS, include customers router.

6. requirements.txt — fastapi uvicorn sqlalchemy

Also generate:

7. frontend/src/api/customerApi.js
   Functions: getAllCustomers(token), getCustomerHistory(userId, token).
   Base URL: http://localhost:8008.

8. frontend/src/pages/PurchaseHistory.jsx
   User-facing page. On mount fetch /api/customers/<user_id>/history.
   Render a table: Date | Items | Total | Discount | Final Amount.
   Show "No purchases yet" if empty.

Follow SOLID, KISS, DRY. Output only working code.
```

---

## ATHARV — U-03: Order Service + Checkout Page

```
You are building the Order/Checkout microservice for a Local Kirana Store Inventory System.
Tech: FastAPI (Python 3.11), SQLite3 (SQLAlchemy), httpx (for inter-service calls).
This service runs on port 8005. DB file path: ../../kirana.db.
CORS must allow: http://localhost:5173.

Generate these files inside backend/order-service/:

1. database.py — SQLAlchemy engine, SessionLocal, get_db(), Base.

2. models.py — SQLAlchemy models for: users, products, sales, sale_items, purchase_history.

3. schemas.py
   Pydantic models:
   - CartItem: product_id (int), quantity (int)
   - CheckoutRequest: user_id (int), cart (list of CartItem), coupon_code (str, optional)
   - CheckoutResponse: order_id, total_amount, discount_amount, final_amount, coupon_applied

4. routers/orders.py
   FastAPI router with prefix /api/orders:
   POST /checkout:
     1. Validate all products exist and have sufficient stock
     2. Call coupon-service POST http://localhost:8006/api/coupons/validate with
        {coupon_code, cart_total, product_ids} using httpx — get discount back
     3. Create sale record in sales table
     4. Insert sale_items rows
     5. Decrement stock_qty in products table for each item
     6. Insert into stock_adjustments (type: sale_deduct)
     7. Insert into purchase_history
     8. For each product, call alert-service GET http://localhost:8007/api/alerts/check/{product_id}
     9. Return CheckoutResponse with 201

5. main.py — FastAPI app on port 8005, CORS, include orders router.

6. requirements.txt — fastapi uvicorn sqlalchemy httpx

Also generate:

7. frontend/src/api/orderApi.js
   Function: placeOrder(checkoutData, token). Base URL: http://localhost:8005.

8. frontend/src/pages/Checkout.jsx
   Reads cart from CartContext. Displays:
   - Item list table: Name | Qty | Unit Price | Subtotal
   - CouponInput component (reusable, defined separately)
   - Order total, discount line, final amount
   - "Place Order" button → POST /api/orders/checkout
   - On success: show confirmation with order_id, clear cart, link to /orders

Follow SOLID, KISS, DRY. Output only working code.
```

---

## ATHARV — U-04: Coupon Service + Coupon Component

```
You are building the Coupon microservice for a Local Kirana Store Inventory System.
Tech: FastAPI (Python 3.11), SQLite3 (SQLAlchemy).
This service runs on port 8006. DB file path: ../../kirana.db.
CORS must allow: http://localhost:5173.

Generate these files inside backend/coupon-service/:

1. database.py — SQLAlchemy engine, SessionLocal, get_db(), Base.

2. models.py — SQLAlchemy model for coupons table:
   id, code, discount_type, discount_value, product_id, is_active.

3. schemas.py
   Pydantic models:
   - CouponValidateRequest: coupon_code (str), cart_total (float), product_ids (list of int)
   - CouponValidateResponse: is_valid (bool), discount_type (str), discount_value (float),
     discount_amount (float), final_total (float), message (str)

4. routers/coupons.py
   FastAPI router with prefix /api/coupons:
   POST /validate:
     - Look up coupon by code where is_active = 1
     - If not found: return is_valid=False, message="Invalid coupon"
     - If discount_type = order_wise: apply discount_value % off cart_total
     - If discount_type = product_wise: apply discount_value % off all matching
       products in cart (by product_id), rest at full price
     - Return CouponValidateResponse with calculated discount_amount and final_total
   GET /list → returns all active coupons (admin use)

5. main.py — FastAPI app on port 8006, CORS, include coupons router.

6. requirements.txt — fastapi uvicorn sqlalchemy

Also generate:

7. frontend/src/api/couponApi.js
   Function: validateCoupon(data). Base URL: http://localhost:8006.

8. frontend/src/components/CouponInput.jsx
   Reusable React component props: cartTotal, productIds, onDiscountApplied(discountData).
   Renders: text input + "Apply" button.
   On click: POST /api/coupons/validate.
   On success: show green text "SAVE10 applied — ₹X off", call onDiscountApplied.
   On failure: show red text with message from API.
   On remove: "Remove" link clears the coupon and resets discount.

Follow SOLID, KISS, DRY. Output only working code.
```

---

## HARSHVARDHAN — U-05: Catalog Service + Catalog Page

```
You are building the Catalog microservice for a Local Kirana Store Inventory System.
Tech: FastAPI (Python 3.11), SQLite3 (SQLAlchemy).
This service runs on port 8003. DB file path: ../../kirana.db.
CORS must allow: http://localhost:5173.

Generate these files inside backend/catalog-service/:

1. database.py — SQLAlchemy engine, SessionLocal, get_db(), Base.

2. models.py — SQLAlchemy model for products table:
   id, name, category, price, stock_qty, reorder_threshold, image_url.

3. schemas.py
   Pydantic model:
   - ProductOut: id, name, category, price, stock_qty, image_url, in_stock (bool),
     low_stock (bool — true if stock_qty < reorder_threshold)

4. routers/catalog.py
   FastAPI router with prefix /api/catalog:
   GET /        → returns all products where stock_qty > 0 as list of ProductOut
   GET /search  → query params: q (str, optional), category (str, optional)
                  filters by name LIKE %q% and/or category equals value
   GET /categories → returns distinct list of category strings

5. main.py — FastAPI app on port 8003, CORS, include catalog router.

6. requirements.txt — fastapi uvicorn sqlalchemy

Also generate:

7. frontend/src/api/catalogApi.js
   Functions: getProducts(), searchProducts(q, category), getCategories().
   Base URL: http://localhost:8003.

8. frontend/src/pages/Catalog.jsx
   On mount: fetch all products and all categories.
   Render at top: search text input + category dropdown filter.
   Filter is client-side (filter the fetched array).
   Product grid (responsive, 3-4 columns): each card shows:
     product name, category badge, price in ₹, stock status badge
     (green "In Stock", yellow "Low Stock" if stock_qty < reorder_threshold),
     "Add to Cart" button that calls CartContext.addToCart(product).
   Show "No products found" if filtered result is empty.

Follow SOLID, KISS, DRY. Output only working code.
```

---

## HARSHVARDHAN — U-06: Cart Context + Frontend Setup

```
You are building the Cart and Navigation for a Local Kirana Store Inventory System.
Tech: React 18 (Vite), Tailwind CSS, React Router v6.
Frontend runs on port 5173. Config base URLs are in src/config.js.

Generate:

1. frontend/src/context/CartContext.jsx
   React context + provider. State: cartItems (array of {id, name, price, qty, image_url}).
   Actions:
   - addToCart(product): if product already in cart, increment qty by 1; else add with qty=1
   - updateQty(productId, newQty): update qty; if newQty <= 0 remove the item
   - removeFromCart(productId): remove item from cart
   - clearCart(): empty the cart
   - cartCount: total number of items (sum of qty)
   - cartTotal: sum of (price * qty) for all items
   Persist cartItems to localStorage key "kirana_cart". Restore on mount.

2. frontend/src/components/CartDrawer.jsx
   A slide-in panel (right side) that shows when cart icon is clicked.
   Lists all cart items: product name, qty +/- stepper, unit price, line total, remove button.
   Footer: subtotal in ₹, "Proceed to Checkout" button → navigate to /checkout.
   "Your cart is empty" state if no items.
   Close button (X) at top right.

3. frontend/src/components/Navbar.jsx
   Top navigation bar:
   Left: "Kirana Store" brand text
   Center: links to /catalog, /orders (user) or /admin/dashboard (if role=admin)
   Right: cart icon with red badge showing cartCount, username, logout button.
   Logout: clear localStorage kirana_token and kirana_cart, redirect to /login.

4. frontend/package.json
   Vite + React 18 project. Dependencies: react-router-dom, tailwindcss.

5. frontend/vite.config.js
   Standard Vite config for React.

6. frontend/src/main.jsx
   Entry point wrapping App in AuthContextProvider and CartContextProvider.

Follow SOLID, KISS, DRY. Output only working code.
```

---

## OM SATYAM — A-01: Alert Service + Admin Dashboard

```
You are building the Alert/Dashboard microservice for a Local Kirana Store Inventory System.
Tech: FastAPI (Python 3.11), SQLite3 (SQLAlchemy).
This service runs on port 8007. DB file path: ../../kirana.db.
CORS must allow: http://localhost:5173.

Generate these files inside backend/alert-service/:

1. database.py — SQLAlchemy engine, SessionLocal, get_db(), Base.

2. models.py — SQLAlchemy models for: products, sales, sale_items (read-only for stats).

3. schemas.py
   Pydantic models:
   - DashboardStats: total_products (int), total_stock_value (float),
     low_stock_count (int), today_revenue (float), today_orders (int)
   - LowStockProduct: id, name, category, stock_qty, reorder_threshold,
     suggested_reorder_qty (int — calculated as reorder_threshold*2 - stock_qty)

4. routers/alerts.py
   FastAPI router with prefix /api/alerts:
   GET /dashboard   → returns DashboardStats
     total_products = count of all products
     total_stock_value = sum(price * stock_qty) for all products
     low_stock_count = count of products where stock_qty < reorder_threshold
     today_revenue = sum(final_amount) from sales where date(sale_time) = today
     today_orders = count of sales where date(sale_time) = today
   GET /low-stock    → returns list of LowStockProduct where stock_qty < reorder_threshold
   GET /check/{product_id} → checks single product; returns {alert: bool, product_id, stock_qty, threshold}

5. main.py — FastAPI app on port 8007, CORS, include alerts router.

6. requirements.txt — fastapi uvicorn sqlalchemy

Also generate:

7. frontend/src/api/alertApi.js
   Functions: getDashboardStats(token), getLowStockProducts(token), checkProduct(id, token).
   Base URL: http://localhost:8007.

8. frontend/src/pages/AdminDashboard.jsx
   On mount: fetch /api/alerts/dashboard.
   Row of 5 stat cards: Total Products | Stock Value (₹) | Low Stock Items |
   Today's Revenue (₹) | Today's Orders.
   Below the cards: a full inventory table fetched from inventory-service
   GET http://localhost:8002/api/inventory (all products).
   Columns: Name | Category | Price | Stock Qty | Status.
   Status cell: red badge "Low Stock" if stock_qty < reorder_threshold, green "OK" otherwise.
   Highlight entire row in light red if low stock.

Follow SOLID, KISS, DRY. Output only working code.
```

---

## OM SATYAM — A-02: Low Stock Alerts Page + Reorder

```
You are building the Low Stock Alert management page for the Admin in a
Local Kirana Store Inventory System.
Tech: React 18 (Vite), Tailwind CSS. Backend alert-service runs on port 8007.
Backend inventory-service runs on port 8002.

Generate:

1. frontend/src/pages/AdminAlerts.jsx
   On mount: fetch GET http://localhost:8007/api/alerts/low-stock.
   Show a table of low-stock products:
   Columns: Product Name | Category | Current Qty | Threshold | Suggested Reorder Qty.
   Suggested Reorder Qty column is an editable number input pre-filled with the
   suggested value (reorder_threshold * 2 - stock_qty).
   "Restock" button per row: calls PATCH http://localhost:8002/api/inventory/stock/{id}
   with {adjustment_type: "add", quantity: <edited value>}.
   "Restock All" button at top: fires all restocks in sequence.
   After restock: show a green toast "Stock updated!" and refresh the table.
   If no low-stock items: show green banner "All items are well-stocked."

2. frontend/src/api/alertApi.js (update if already created, else create)
   Add function: restockProduct(productId, qty, token) calling inventory-service PATCH.

Follow SOLID, KISS, DRY. Output only working code.
```

---

## PRATYUSH — A-03: Inventory Service CRUD + Bulk Import

```
You are building the Inventory Management microservice for a Local Kirana Store Inventory System.
Tech: FastAPI (Python 3.11), SQLite3 (SQLAlchemy).
This service runs on port 8002. DB file path: ../../kirana.db.
CORS must allow: http://localhost:5173.

Generate these files inside backend/inventory-service/:

1. database.py — SQLAlchemy engine, SessionLocal, get_db(), Base.

2. models.py — SQLAlchemy model for products table and stock_adjustments table.

3. schemas.py
   Pydantic models:
   - ProductCreate: name, category, price, stock_qty, reorder_threshold, image_url (optional)
   - ProductUpdate: all fields optional
   - ProductOut: all fields including id and created_at
   - BulkProductImport: products (list of ProductCreate)
   - StockAdjust: adjustment_type (Literal["add","set"]), quantity (int)

4. routers/inventory.py
   FastAPI router with prefix /api/inventory:
   GET    /            → list all products
   GET    /{id}        → get single product
   POST   /            → create product, return 201 with ProductOut
   PUT    /{id}        → update product fields
   DELETE /{id}        → delete product, return 204
   POST   /bulk        → insert list of products in single DB transaction, return count inserted
   PATCH  /stock/{id}  → adjust stock:
     if adjustment_type=add: stock_qty += quantity
     if adjustment_type=set: stock_qty = quantity
     insert row into stock_adjustments table
     return updated ProductOut

5. main.py — FastAPI app on port 8002, CORS, include inventory router.

6. requirements.txt — fastapi uvicorn sqlalchemy

Also generate:

7. frontend/src/api/inventoryApi.js
   Functions: getAllProducts, getProduct, createProduct, updateProduct, deleteProduct,
   bulkImportProducts, adjustStock. Base URL: http://localhost:8002.

8. frontend/src/pages/AdminInventoryManager.jsx
   Two sections:

   Section 1 — Product form (Add / Edit):
   Fields: Name, Category, Price, Stock Qty, Reorder Threshold.
   Submit adds new product (POST /api/inventory).
   Clicking Edit on a table row populates the form; submit updates (PUT /{id}).
   Clicking Delete shows a confirm dialog, then DELETE /{id}.
   Product table below form: Name | Category | Price | Stock | Actions (Edit / Delete).

   Section 2 — Bulk Import:
   Textarea for JSON array of products.
   "Import" button → POST /api/inventory/bulk.
   Show success: "X products imported" or error message.

Follow SOLID, KISS, DRY. Output only working code.
```

---

## PRATYUSH — A-04: Stock Update Page + Adjustment Log

```
You are building the Stock Update admin page for a Local Kirana Store Inventory System.
Tech: React 18 (Vite), Tailwind CSS. Backend inventory-service runs on port 8002.

Generate:

1. backend/inventory-service/routers/stock_log.py
   Add to inventory-service (new router file):
   FastAPI router with prefix /api/inventory:
   GET /stock/log → returns last 50 rows from stock_adjustments joined with
   products table: product_name, adjustment_type, quantity, adjusted_at.
   Register this router in backend/inventory-service/main.py.

2. frontend/src/api/stockApi.js
   Functions: adjustStock(productId, data, token), getStockLog(token).
   Base URL: http://localhost:8002.

3. frontend/src/pages/AdminStockUpdate.jsx
   Top section — Manual Adjustment Form:
   Dropdown: select product (fetched from GET /api/inventory).
   Radio: "Add to existing stock" or "Set stock to value".
   Number input: quantity.
   Submit → PATCH /api/inventory/stock/{id}.
   Show success toast with updated stock quantity.

   Bottom section — Adjustment Log:
   Read-only table, fetched from GET /api/inventory/stock/log.
   Columns: Product | Adjustment Type | Quantity | Date & Time.
   Refresh button to reload.

Follow SOLID, KISS, DRY. Output only working code.
```

---

## SANIDHYA — A-05: Sales Service + Admin Sales Page

```
You are building the Sales microservice for a Local Kirana Store Inventory System.
Tech: FastAPI (Python 3.11), SQLite3 (SQLAlchemy).
This service runs on port 8004. DB file path: ../../kirana.db.
CORS must allow: http://localhost:5173.

Generate these files inside backend/sales-service/:

1. database.py — SQLAlchemy engine, SessionLocal, get_db(), Base.

2. models.py — SQLAlchemy models for: sales, sale_items, products, users (all read-only).

3. schemas.py
   Pydantic models:
   - SaleItemOut: product_name (str), quantity (int), unit_price (float)
   - SaleOut: id, customer_name, customer_phone, items (list of SaleItemOut),
     total_amount, discount_amount, final_amount, coupon_code, sale_time
   - SalesSummary: today_revenue (float), today_orders (int), top_product_name (str),
     top_product_qty (int)

4. routers/sales.py
   FastAPI router with prefix /api/sales:
   GET /          → query param: date (YYYY-MM-DD, default today)
                    returns list of SaleOut for that date
   GET /summary   → returns SalesSummary for today
     today_revenue = sum of final_amount for today's sales
     today_orders = count of today's sales
     top_product = product with highest sum(quantity) in sale_items today

5. main.py — FastAPI app on port 8004, CORS, include sales router.

6. requirements.txt — fastapi uvicorn sqlalchemy

Also generate:

7. frontend/src/api/salesApi.js
   Functions: getSalesByDate(date, token), getSalesSummary(token).
   Base URL: http://localhost:8004.

8. frontend/src/pages/AdminSales.jsx
   Top: date picker input (default today).
   Summary strip (3 stat cards): Today's Revenue (₹) | Orders | Top Selling Product.
   Below: table of sales for selected date.
   Columns: Time | Customer | Items (comma-separated names) | Total | Discount | Final Amount.
   "No sales recorded for this date" empty state.
   Auto-fetch when date changes.

Follow SOLID, KISS, DRY. Output only working code.
```

---

## SANIDHYA — A-06: Admin Customer Management Page

```
You are building the Admin Customer Management page for a Local Kirana Store Inventory System.
Tech: React 18 (Vite), Tailwind CSS.
Customer data: GET http://localhost:8008/api/customers
Customer history: GET http://localhost:8008/api/customers/{id}/history

Generate:

1. frontend/src/pages/AdminCustomers.jsx
   On mount: fetch GET /api/customers (all customers).
   Render a table:
   Columns: Name | Phone | Address | Total Orders | Total Spent (₹) | Actions.
   "View History" button in Actions column.

   Clicking "View History" expands an inline sub-row (accordion style) below that
   customer showing their purchase history table:
   Columns: Date | Items | Total | Discount | Final Amount | Coupon Used.
   Fetch the history only when expanded (lazy load).
   Show "No purchase history" if empty.

2. frontend/src/api/customerApi.js (create or update)
   Functions: getAllCustomers(token), getCustomerHistory(userId, token).
   Base URL: http://localhost:8008.

Follow SOLID, KISS, DRY. Output only working code.
```

---

## Presentation Flow (All Members)

```
Demo order for the panel:

Step 1 — Admin: Login as admin → show Dashboard (stats cards + inventory table with low-stock rows)
Step 2 — Admin: Go to Inventory Manager → add a new product live
Step 3 — Admin: Go to Alerts page → show low stock items → trigger Restock All
Step 4 — User: Open new tab → Register as new user → Login
Step 5 — User: Browse Catalog → search for a product → Add to Cart
Step 6 — User: Open Cart drawer → proceed to Checkout → apply coupon SAVE10
Step 7 — User: Place Order → show confirmation with final amount
Step 8 — Admin: Refresh Dashboard → show updated Today's Revenue and Orders
Step 9 — Admin: Go to Sales page → show the just-recorded transaction
Step 10 — Admin: Go to Customers → find the new user → expand purchase history

Diagrams to show:
- Architecture diagram (docs/architecture.md rendered on mermaid.live)
- Sequence diagram (docs/sequence.md rendered on mermaid.live)

Talking points:
- Microservices design: each service independently deployable
- GitHub Copilot agent generated 100% of the code
- Git branching: feature branches + PRs + merge to main
- SDLC practiced end-to-end in 2 hours: Plan → Build → Integrate → Test → Present
```

---

*Last updated: Sprint Day — do not modify during active development.*