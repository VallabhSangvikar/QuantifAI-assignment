import sqlite3
import pandas as pd
import os

def clear_all_tables():
    with sqlite3.connect("ecommerce.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM order_items;")
        cursor.execute("DELETE FROM orders;")
        cursor.execute("DELETE FROM products;")
        cursor.execute("DELETE FROM suppliers;")
        cursor.execute("DELETE FROM customers;")
        conn.commit()

clear_all_tables()

# Assuming df_customers is your cleaned DataFrame
file_path = os.path.join(os.path.dirname(__file__), '..', 'cleaned', 'customers_cleaned_data.json')
df_customers = pd.read_json(file_path)

with sqlite3.connect("ecommerce.db") as conn:
    df_customers.to_sql("customers", conn, if_exists="append", index=False)


file_path = os.path.join(os.path.dirname(__file__), '..', 'cleaned', 'products_cleaned_data.json')
df_products = pd.read_json(file_path)  # or use your DataFrame

# Extract unique suppliers
df_suppliers = df_products[['supplier_id']].dropna().drop_duplicates()

with sqlite3.connect("ecommerce.db") as conn:
    df_suppliers.to_sql("suppliers", conn, if_exists="append", index=False)

# Optional: drop 'item_id' if not required
df_products = df_products.drop(columns=['item_id'], errors='ignore')

with sqlite3.connect("ecommerce.db") as conn:
    df_products.to_sql("products", conn, if_exists="append", index=False)



file_path = os.path.join(os.path.dirname(__file__), '..', 'cleaned', 'orders_cleaned_data.csv')
df_orders_full = pd.read_csv(file_path)  # Or from your pipeline

df_order_items=df_orders_full[['order_id','item_id', 'product_id', 'quantity', 'unit_price', 'total_amount']].drop_duplicates(subset=['order_id', 'item_id'])

df_orders=df_orders_full[['order_id', 'customer_id', 'order_date', 'order_datetime',
    'status', 'payment_method', 'shipping_address', 'tracking_number',
    'shipping_cost', 'tax', 'discount', 'order_total']].drop_duplicates(subset=['order_id'])


with sqlite3.connect("ecommerce.db") as conn:
    df_orders.to_sql("orders", conn, if_exists="append", index=False)
    df_order_items.to_sql("order_items", conn, if_exists="append", index=False)