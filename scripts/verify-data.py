#!/usr/bin/env python3
"""Quick verification of seeded data"""

import sqlite3

conn = sqlite3.connect('kirana.db')
c = conn.cursor()

print("\n👤 Users:")
c.execute('SELECT name, phone FROM users')
for row in c.fetchall():
    print(f"  - {row[0]:25s} {row[1]}")

print("\n📦 Sample Products:")
c.execute('SELECT name, category, price, stock_qty FROM products LIMIT 8')
for row in c.fetchall():
    print(f"  - {row[0]:30s} {row[1]:12s} ₹{row[2]:6.2f} Stock: {row[3]}")

print("\n🎫 Coupons:")
c.execute('SELECT code, discount_type, discount_value FROM coupons')
for row in c.fetchall():
    print(f"  - {row[0]:15s} {row[1]:15s} ₹{row[2]}")

print("\n🛒 Recent Sales:")
c.execute('''
    SELECT s.id, u.name, s.final_amount, s.coupon_code, date(s.sale_time) as date 
    FROM sales s 
    JOIN users u ON s.user_id = u.id 
    ORDER BY s.sale_time DESC 
    LIMIT 5
''')
for row in c.fetchall():
    coupon = row[3] or "None"
    print(f"  - Sale #{row[0]} by {row[1]:20s} ₹{row[2]:7.2f} Coupon: {coupon:12s} on {row[4]}")

conn.close()
print("\n✅ Database verification complete!")
