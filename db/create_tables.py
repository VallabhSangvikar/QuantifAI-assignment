import sqlite3

def reset_database():
    with sqlite3.connect("ecommerce.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS order_items;")
        cursor.execute("DROP TABLE IF EXISTS orders;")
        cursor.execute("DROP TABLE IF EXISTS products;")
        cursor.execute("DROP TABLE IF EXISTS suppliers;")
        cursor.execute("DROP TABLE IF EXISTS customers;")
        conn.commit()
reset_database()

conn = sqlite3.connect("ecommerce.db")
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    registration_date INTEGER,
    status TEXT,
    total_orders INTEGER,
    total_spent REAL,
    loyalty_points INTEGER,
    preferred_payment TEXT,
    age REAL,
    birth_date TEXT,
    gender TEXT,
    segment TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id TEXT PRIMARY KEY
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT,
    item_name TEXT,
    description TEXT,
    category TEXT,
    product_category TEXT,
    final_category TEXT,
    brand TEXT,
    manufacturer TEXT,
    price REAL,
    list_price REAL,
    cost REAL,
    weight REAL,
    dimensions TEXT,
    color TEXT,
    size TEXT,
    stock_quantity INTEGER,
    stock_level INTEGER,
    reorder_level INTEGER,
    supplier_id TEXT,
    created_date INTEGER,
    last_updated INTEGER,
    is_active BOOLEAN,
    rating REAL,
    is_active_flag_issue BOOLEAN,
    category_mismatch BOOLEAN,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    order_datetime TEXT,
    status TEXT,
    payment_method TEXT,
    shipping_address TEXT,
    tracking_number TEXT,
    shipping_cost REAL,
    tax REAL,
    discount REAL,
    order_total REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    order_id TEXT,
    item_id INTEGER,
    product_id TEXT,
    quantity INTEGER,
    unit_price REAL,
    total_amount REAL,
    PRIMARY KEY (order_id, item_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
""")

conn.commit()
conn.close()
