-- Kirana Store — Database Schema
-- Run once: python scripts/init-db.py
-- All backend services share this single kirana.db at the project root.

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
  name              TEXT    NOT NULL,
  category          TEXT    NOT NULL,
  price             REAL    NOT NULL,
  stock_qty         INTEGER NOT NULL DEFAULT 0,
  reorder_threshold INTEGER NOT NULL DEFAULT 10,
  image_url         TEXT    DEFAULT '',
  created_at        TEXT    DEFAULT (datetime('now'))
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

-- ── Seed Products ────────────────────────────────────────────────────────────
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

-- ── Seed Coupons ─────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO coupons (code, discount_type, discount_value, product_id) VALUES
  ('SAVE10', 'order_wise',   10.0, NULL),
  ('FLAT50', 'order_wise',   50.0, NULL),
  ('RICE20', 'product_wise', 20.0, 1);
