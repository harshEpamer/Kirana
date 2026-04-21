#!/usr/bin/env python3
"""
Seed realistic Indian grocery store data into kirana.db
Run from project root: python scripts/seed-data.py
"""

import sqlite3
from datetime import datetime, timedelta
import random
import bcrypt

# Database path relative to project root
DB_PATH = "kirana.db"

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    # Convert password to bytes and hash it
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def seed_users(cursor):
    """Seed 1 admin + 5 customer users"""
    password_hash = get_password_hash("kirana123")
    
    users = [
        ("Pranav Suraparaju", "9999900001", "Admin Office, MG Road, Bengaluru", password_hash),
        ("Rajesh Kumar", "9876543210", "12/A, Nehru Nagar, Delhi", password_hash),
        ("Priya Sharma", "9876543211", "45, Gandhi Street, Mumbai", password_hash),
        ("Amit Patel", "9876543212", "78, Lake View, Ahmedabad", password_hash),
        ("Sneha Reddy", "9876543213", "23, Banjara Hills, Hyderabad", password_hash),
        ("Vikram Singh", "9876543214", "56, Civil Lines, Jaipur", password_hash),
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO users (name, phone, address, password_hash) VALUES (?, ?, ?, ?)",
        users
    )
    return cursor.rowcount

def seed_products(cursor):
    """Add 15 more products to existing 10"""
    products = [
        # Grains
        ("Sona Masoori Rice 1kg", "Grains", 75.0, 45, 10),
        ("Brown Rice 1kg", "Grains", 95.0, 25, 8),
        
        # Pulses
        ("Moong Dal 500g", "Pulses", 70.0, 35, 10),
        ("Chana Dal 500g", "Pulses", 68.0, 30, 10),
        ("Masoor Dal 500g", "Pulses", 62.0, 28, 8),
        
        # Oils
        ("Mustard Oil 1L", "Oils", 145.0, 18, 5),
        ("Groundnut Oil 1L", "Oils", 140.0, 15, 5),
        
        # Dairy
        ("Amul Milk 1L", "Dairy", 58.0, 25, 8),
        ("Amul Cheese 200g", "Dairy", 135.0, 12, 5),
        
        # Snacks
        ("Kurkure 90g", "Snacks", 20.0, 60, 15),
        ("Good Day Biscuits", "Snacks", 25.0, 45, 12),
        
        # Beverages
        ("Tata Tea Gold 250g", "Beverages", 185.0, 22, 8),
        ("Bru Coffee 200g", "Beverages", 220.0, 18, 6),
        
        # Frozen
        ("McCain French Fries", "Frozen", 165.0, 10, 5),
        
        # Spices
        ("MDH Garam Masala 100g", "Spices", 85.0, 30, 10),
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO products (name, category, price, stock_qty, reorder_threshold) VALUES (?, ?, ?, ?, ?)",
        products
    )
    return cursor.rowcount

def seed_coupons(cursor):
    """Add 3 more coupons to existing 3"""
    # Get product IDs for product-wise coupons
    cursor.execute("SELECT id FROM products WHERE name = 'Toor Dal 500g'")
    toor_dal_id = cursor.fetchone()
    
    cursor.execute("SELECT id FROM products WHERE name = 'Amul Butter 100g'")
    butter_id = cursor.fetchone()
    
    coupons = [
        ("WELCOME25", "order_wise", 25.0, None, 1),
        ("DAIRY15", "product_wise", 15.0, butter_id[0] if butter_id else None, 1),
        ("NEWYEAR100", "order_wise", 100.0, None, 1),
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO coupons (code, discount_type, discount_value, product_id, is_active) VALUES (?, ?, ?, ?, ?)",
        coupons
    )
    return cursor.rowcount

def seed_sales_and_items(cursor):
    """Create 12 sales over last 7 days with sale_items, purchase_history, and stock adjustments"""
    
    # Get all user IDs (excluding admin - first user)
    cursor.execute("SELECT id FROM users WHERE phone != '9999900001'")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    # Get all products with their current prices
    cursor.execute("SELECT id, price FROM products")
    products = cursor.fetchall()
    
    # Get coupon codes
    cursor.execute("SELECT code, discount_type, discount_value FROM coupons WHERE is_active = 1")
    coupons = cursor.fetchall()
    
    sales_count = 0
    sale_items_count = 0
    purchase_history_count = 0
    stock_adjustments_count = 0
    
    # Create 12 sales over the last 7 days
    for i in range(12):
        # Random date within last 7 days
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        sale_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
        sale_time_str = sale_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Random user
        user_id = random.choice(user_ids)
        
        # Random number of items (2-4)
        num_items = random.randint(2, 4)
        selected_products = random.sample(products, num_items)
        
        # Calculate total
        total_amount = 0.0
        items_data = []
        
        for product_id, price in selected_products:
            quantity = random.randint(1, 5)
            unit_price = price
            item_total = quantity * unit_price
            total_amount += item_total
            items_data.append((product_id, quantity, unit_price))
        
        # Apply coupon randomly (50% chance)
        discount_amount = 0.0
        coupon_code = None
        if random.random() > 0.5 and coupons:
            coupon = random.choice(coupons)
            coupon_code = coupon[0]
            discount_type = coupon[1]
            discount_value = coupon[2]
            
            if discount_type == 'order_wise':
                discount_amount = discount_value
            else:
                # For product_wise, apply to first item only (simplified)
                discount_amount = min(discount_value, items_data[0][1] * items_data[0][2])
        
        final_amount = max(0, total_amount - discount_amount)
        
        # Insert sale
        cursor.execute(
            "INSERT INTO sales (user_id, total_amount, discount_amount, final_amount, coupon_code, sale_time) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, total_amount, discount_amount, final_amount, coupon_code, sale_time_str)
        )
        sale_id = cursor.lastrowid
        sales_count += 1
        
        # Insert sale items
        for product_id, quantity, unit_price in items_data:
            cursor.execute(
                "INSERT INTO sale_items (sale_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (sale_id, product_id, quantity, unit_price)
            )
            sale_items_count += 1
            
            # Insert stock adjustment for sale deduction
            cursor.execute(
                "INSERT INTO stock_adjustments (product_id, adjustment_type, quantity, adjusted_at) VALUES (?, 'sale_deduct', ?, ?)",
                (product_id, quantity, sale_time_str)
            )
            stock_adjustments_count += 1
            
            # Update product stock
            cursor.execute(
                "UPDATE products SET stock_qty = stock_qty - ? WHERE id = ?",
                (quantity, product_id)
            )
        
        # Insert purchase history
        cursor.execute(
            "INSERT INTO purchase_history (user_id, sale_id, recorded_at) VALUES (?, ?, ?)",
            (user_id, sale_id, sale_time_str)
        )
        purchase_history_count += 1
    
    return sales_count, sale_items_count, purchase_history_count, stock_adjustments_count

def seed_initial_stock_adjustments(cursor):
    """Add initial 'set' stock adjustments for all products"""
    cursor.execute("SELECT id, stock_qty FROM products")
    products = cursor.fetchall()
    
    # Create initial stock adjustments (set type) dated 8 days ago
    initial_date = (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S')
    
    adjustments = []
    for product_id, stock_qty in products:
        # Initial stock was higher before sales
        initial_stock = stock_qty + random.randint(20, 50)
        adjustments.append((product_id, 'set', initial_stock, initial_date))
    
    cursor.executemany(
        "INSERT INTO stock_adjustments (product_id, adjustment_type, quantity, adjusted_at) VALUES (?, ?, ?, ?)",
        adjustments
    )
    return cursor.rowcount

def main():
    print("🌾 Seeding Kirana Store Database...")
    print(f"Database: {DB_PATH}\n")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Seed in FK order
        print("👤 Seeding users...")
        users_count = seed_users(cursor)
        print(f"   ✓ {users_count} users inserted")
        
        print("📦 Seeding products...")
        products_count = seed_products(cursor)
        print(f"   ✓ {products_count} products inserted")
        
        print("🎫 Seeding coupons...")
        coupons_count = seed_coupons(cursor)
        print(f"   ✓ {coupons_count} coupons inserted")
        
        print("📊 Seeding initial stock adjustments...")
        initial_adj_count = seed_initial_stock_adjustments(cursor)
        print(f"   ✓ {initial_adj_count} initial stock adjustments inserted")
        
        print("🛒 Seeding sales, sale items, purchase history, and stock adjustments...")
        sales_count, sale_items_count, purchase_history_count, stock_adj_count = seed_sales_and_items(cursor)
        print(f"   ✓ {sales_count} sales inserted")
        print(f"   ✓ {sale_items_count} sale items inserted")
        print(f"   ✓ {purchase_history_count} purchase history entries inserted")
        print(f"   ✓ {stock_adj_count} sale stock adjustments inserted")
        
        conn.commit()
        
        # Print final counts
        print("\n📈 Final Database Counts:")
        tables = ['users', 'products', 'coupons', 'sales', 'sale_items', 'purchase_history', 'stock_adjustments']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table:20s}: {count:3d} rows")
        
        print("\n✅ Database seeding completed successfully!")
        print("🔑 All user passwords: kirana123")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    exit(main())
