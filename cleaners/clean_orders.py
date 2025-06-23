import pandas as pd
import numpy as np
from datetime import datetime
import re
import warnings
import os
warnings.filterwarnings('ignore')

def clean_orders_dataset(df):
    """
    Clean the orders dataset with relational awareness and data consistency.
    """
    cleaned_df = df.copy()
    print("Starting data cleaning process...")
    print(f"Original dataset shape: {cleaned_df.shape}")

    # 1. Handle duplicate columns
    cleaned_df = remove_duplicate_columns(cleaned_df)

    # 2. Standardize date formats
    cleaned_df = standardize_date_formats(cleaned_df)

    # 3. Handle missing values
    cleaned_df = handle_missing_values(cleaned_df)

    # 4. Standardize status columns
    cleaned_df = standardize_status_columns(cleaned_df)

    # 5. Flag quantity conflicts before merging
    cleaned_df = flag_quantity_conflict(cleaned_df)

    # 6. Fix quantity mismatches (merge)
    cleaned_df = fix_quantity_columns(cleaned_df)

    # 7. Recalculate financial columns
    cleaned_df = recalculate_financial_columns(cleaned_df)

    # 8. Handle low-value columns
    cleaned_df = handle_low_value_columns(cleaned_df)

    # 9. Final data validation
    cleaned_df = final_data_validation(cleaned_df)

    print(f"Cleaned dataset shape: {cleaned_df.shape}")
    print("Data cleaning completed successfully!")

    return cleaned_df

def remove_duplicate_columns(df):
    print("Removing duplicate columns...")
    # Keep `customer_id`, drop `cust_id` (reversed logic)
    if 'cust_id' in df.columns:
        df = df.drop('cust_id', axis=1)
        print("  - Removed 'cust_id' column (duplicate of 'customer_id')")

    if 'ord_id' in df.columns:
        df = df.drop('ord_id', axis=1)
        print("  - Removed 'ord_id' column (duplicate of 'order_id')")
    
    return df

def standardize_date_formats(df):
    print("Standardizing date formats...")

    def parse_date(date_str):
        if pd.isna(date_str) or date_str == '':
            return pd.NaT
        formats = ['%m/%d/%Y', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']
        for fmt in formats:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except:
                continue
        try:
            return pd.to_datetime(date_str)
        except:
            return pd.NaT

    if 'order_date' in df.columns:
        df['order_date'] = df['order_date'].apply(parse_date)
        print("  - Standardized 'order_date'")
    if 'order_datetime' in df.columns:
        df['order_datetime'] = pd.to_datetime(df['order_datetime'], errors='coerce')
        print("  - Standardized 'order_datetime'")
    return df

def handle_missing_values(df):
    print("Handling missing values...")
    if 'order_date' in df.columns and 'order_datetime' in df.columns:
        mask = df['order_date'].isna() & df['order_datetime'].notna()
        df.loc[mask, 'order_date'] = df.loc[mask, 'order_datetime'].dt.date
        print(f"  - Filled {mask.sum()} missing order_date values from order_datetime")

        mask = df['order_datetime'].isna() & df['order_date'].notna()
        df.loc[mask, 'order_datetime'] = pd.to_datetime(df.loc[mask, 'order_date'].astype(str) + ' 12:00:00')
        print(f"  - Filled {mask.sum()} missing order_datetime values")

    if 'tracking_number' in df.columns and 'status' in df.columns:
        shipped_mask = df['status'].str.upper().isin(['SHIPPED', 'DELIVERED']) & df['tracking_number'].isna()
        df.loc[shipped_mask, 'tracking_number'] = 'TRK' + np.random.randint(100000, 999999, size=shipped_mask.sum()).astype(str)
        print(f"  - Generated {shipped_mask.sum()} tracking numbers for shipped/delivered orders")

    return df

def standardize_status_columns(df):
    print("Standardizing status columns...")
    mapping = {
        'delivered': 'DELIVERED', 'processing': 'PROCESSING',
        'cancelled': 'CANCELLED', 'pending': 'PENDING', 'shipped': 'SHIPPED'
    }

    if 'status' in df.columns:
        df['status'] = df['status'].str.lower().map(mapping).fillna('PENDING')
        print("  - Standardized 'status'")

    if 'order_status' in df.columns:
        df['order_status'] = df['order_status'].str.lower().map(mapping).fillna('PENDING')
        print("  - Standardized 'order_status'")

    if 'status' in df.columns and 'order_status' in df.columns:
        priority = {'DELIVERED': 5, 'SHIPPED': 4, 'CANCELLED': 3, 'PROCESSING': 2, 'PENDING': 1}
        df['status'] = df.apply(
            lambda row: row['status'] if priority.get(row['status'], 0) >= priority.get(row['order_status'], 0)
            else row['order_status'], axis=1
        )
        df.drop('order_status', axis=1, inplace=True)
        print("  - Merged 'status' and 'order_status' into unified 'status'")
    return df

def flag_quantity_conflict(df):
    if 'quantity' in df.columns and 'qty' in df.columns:
        df['quantity_conflict'] = df['quantity'] != df['qty']
        print("  - Flagged quantity conflicts before merging")
    return df

def fix_quantity_columns(df):
    print("Fixing quantity columns...")
    if 'quantity' in df.columns and 'qty' in df.columns:
        df['quantity'] = np.maximum(df['quantity'], df['qty'])
        df.drop('qty', axis=1, inplace=True)
        print("  - Unified 'quantity' column from 'quantity' and 'qty'")
    return df

def recalculate_financial_columns(df):
    print("Recalculating financial columns...")
    required = ['unit_price', 'quantity', 'shipping_cost', 'tax', 'discount']
    if all(col in df.columns for col in required):
        df['expected_total'] = df['unit_price'] * df['quantity'] + df['tax'] + df['shipping_cost'] - df['discount']
        df['total_mismatch'] = ~np.isclose(df['order_total'], df['expected_total'], atol=1.0)

        df['order_total'] = df['expected_total']
        
        df['total_amount'] = df['expected_total']- df['shipping_cost'] - df['tax']
        if 'price' in df.columns:
            df.drop('price', axis=1, inplace=True)
        df.drop(['expected_total'], axis=1, inplace=True)

        print("  - Recalculated totals and added 'total_mismatch' flag")
    return df

def handle_low_value_columns(df):
    print("Handling low-value columns...")
    if 'notes' in df.columns:
        null_pct = df['notes'].isna().sum() / len(df) * 100
        if null_pct > 75 and df['notes'].nunique() <= 2:
            df.drop('notes', axis=1, inplace=True)
            print("  - Dropped low-value 'notes' column")
        else:
            df['notes'] = df['notes'].fillna('')
            print("  - Filled missing notes")
    return df

def final_data_validation(df):
    print("Final data validation...")
    if 'quantity' in df.columns:
        df.loc[df['quantity'] < 0, 'quantity'] = abs(df['quantity'])
    for col in ['unit_price', 'order_total', 'total_amount', 'shipping_cost', 'tax']:
        if col in df.columns:
            df.loc[df[col] < 0, col] = abs(df[col])
    if all(col in df.columns for col in ['discount', 'unit_price', 'quantity']):
        max_discount = df['unit_price'] * df['quantity']
        df.loc[df['discount'] > max_discount, 'discount'] = max_discount * 0.5
    return df

def generate_data_quality_report(df):
    print("\n" + "="*50)
    print("DATA QUALITY REPORT - CLEANED DATASET")
    print("="*50)
    print(f"Dataset Shape: {df.shape}")
    for col in df.columns:
        null_pct = df[col].isna().sum() / len(df) * 100
        print(f"{col:20}: {null_pct:.1f}% null | {df[col].nunique()} unique | {df[col].dtype}")
    print("✓ Ready for joining with customers/products")

def main():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'orders_unstructured_data.csv')
    df = pd.read_csv(file_path)

    cleaned_df = clean_orders_dataset(df)

    generate_data_quality_report(cleaned_df)

    output_path = os.path.join(os.path.dirname(__file__), '..', 'cleaned', 'orders_cleaned_data.csv')
    cleaned_df.to_csv(output_path, index=False)
    print("\n Cleaned orders saved.")

    return cleaned_df

if __name__ == "__main__":
    cleaned_data = main()
