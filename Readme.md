# 🛒 Kirana Store

A full-stack retail management system for small neighbourhood Indian grocery stores ("kirana" shops). Built as a hackathon prototype with a micro-service backend and a React SPA.

---

## Stack

| Layer        | Tech                                                             |
|--------------|------------------------------------------------------------------|
| Frontend     | React 18 (Vite), React Router v6, Tailwind CSS, Context API      |
| Backend      | FastAPI, SQLAlchemy ORM, python-jose (JWT), passlib[bcrypt]      |
| Database     | SQLite3 (single shared file `kirana.db` at project root)         |
| Architecture | 8 independent FastAPI micro-services, each on its own port       |

### Services & Ports

| Service          | Port | Purpose                                  |
|------------------|------|------------------------------------------|
| auth-service     | 8001 | Registration, login, JWT issuance        |
| inventory-service| 8002 | Products, stock levels, stock log        |
| catalog-service  | 8003 | Public product browsing                  |
| sales-service    | 8004 | Sales transactions & totals              |
| order-service    | 8005 | Order processing                         |
| coupon-service   | 8006 | Coupon CRUD & validation                 |
| alert-service    | 8007 | Low-stock alerts & dashboard stats       |
| customer-service | 8008 | Customer list & purchase history         |
| frontend (vite)  | 5173 | React SPA                                |

---

## Getting Started

### Prerequisites

- Python **3.11+**
- Node.js **18+**
- Git

### 1. Clone & set up the database

```bash
git clone <repo-url>
cd Kirana
python scripts/init-db.py    # creates kirana.db with all tables
python scripts/seed-data.py  # inserts demo users, products, sales
```

> **Note:** `kirana.db` is in `.gitignore`. Every teammate must run the two scripts above after cloning.

### 2. Start the backend services

Each service has its own `requirements.txt`. From the project root, open **eight** terminals (one per service) and run:

```bash
# Example for auth-service (repeat for every service folder, substituting the port)
cd backend/auth-service
pip install -r requirements.txt
uvicorn main:app --port 8001 --reload
```

| Folder                       | Command                                           |
|------------------------------|---------------------------------------------------|
| `backend/auth-service`       | `uvicorn main:app --port 8001 --reload`           |
| `backend/inventory-service`  | `uvicorn main:app --port 8002 --reload`           |
| `backend/catalog-service`    | `uvicorn main:app --port 8003 --reload`           |
| `backend/sales-service`      | `uvicorn main:app --port 8004 --reload`           |
| `backend/order-service`      | `uvicorn main:app --port 8005 --reload`           |
| `backend/coupon-service`     | `uvicorn main:app --port 8006 --reload`           |
| `backend/alert-service`      | `uvicorn main:app --port 8007 --reload`           |
| `backend/customer-service`   | `uvicorn main:app --port 8008 --reload`           |

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

---

## Demo Credentials

All seeded users share the password **`kirana123`**.

| Role     | Phone         | Name                 |
|----------|---------------|----------------------|
| Admin    | `9999900001`  | Pranav Suraparaju    |
| Customer | `9876543210`  | Ananya Sharma        |
| Customer | `9876543211`  | Rohan Gupta          |
| Customer | `9876543212`  | Priya Verma          |
| Customer | `9876543213`  | Arjun Iyer           |
| Customer | `9876543214`  | Meera Nair           |

Admin is identified by the hard-coded phone `9999900001`. Logging in with any other phone yields a standard customer account.

### Sample Coupons

| Code        | Discount               |
|-------------|------------------------|
| `SAVE10`    | 10% off                |
| `FLAT50`    | ₹50 off                |
| `WELCOME15` | 15% off (new user)     |
| `BIGSPEND`  | ₹200 off above ₹2000   |
| `FREEBIE`   | ₹100 off any cart      |
| `NEWYEAR`   | 20% off (limited)      |

---

## Project Structure

```
Kirana/
├── backend/
│   ├── auth-service/
│   ├── inventory-service/
│   ├── catalog-service/
│   ├── sales-service/
│   ├── order-service/
│   ├── coupon-service/
│   ├── alert-service/
│   └── customer-service/
├── frontend/
│   └── src/
│       ├── api/          # fetch wrappers per service
│       ├── components/   # Navbar, AuthGuard, CartDrawer, CouponInput
│       ├── context/      # AuthContext, CartContext (with localStorage)
│       └── pages/        # Login, Register, Catalog, Cart, Admin*, …
├── scripts/
│   ├── init-db.py        # creates kirana.db schema
│   └── seed-data.py      # inserts demo data
├── docs/                 # architecture diagrams
├── kirana.db             # gitignored
└── Readme.md
```

---

## Key Features

- **Customer flow**: register → browse catalog → add to cart (persisted in `localStorage`) → apply coupon → checkout → view purchase history
- **Admin flow**: dashboard → inventory CRUD → manual stock updates with audit log → low-stock alerts with one-click restock → date-filtered sales report → customer list with expandable purchase history
- **Auth**: JWT (HS256, 24h expiry); role (`admin` / `user`) embedded in token and returned on login
- **Cart persistence**: `kirana_cart` key in `localStorage` survives page reloads
- **Auth persistence**: `kirana_token` + `kirana_user` restored on app mount
- **Route protection**: `<AuthGuard>` wrapper redirects unauthenticated users and non-admins
