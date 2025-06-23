import pandas as pd
import numpy as np
from datetime import datetime
import re
import os

def clean_product_dataset(df):
    """
    Clean the product dataset by addressing missing values, formatting issues,
    and standardizing categorical/numerical values. Includes improvements based
    on relational analysis (e.g., category conflicts, is_active checks).
    """
    cleaned_df = df.copy()
    print("Starting data cleaning process...")
    print(f"Initial dataset shape: {cleaned_df.shape}")

    # 1. Convert empty strings to NaN
    print("\n1. Converting empty strings to NaN...")
    string_columns = ['description', 'brand', 'manufacturer', 'color', 'size',
                      'supplier_id', 'created_date', 'last_updated', 'dimensions']
    for col in string_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].replace('', np.nan)

    # 2. Convert price-related fields to numeric
    print("\n2. Converting price columns to proper numeric types...")
    price_columns = ['price', 'list_price', 'cost', 'weight']
    for col in price_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')

    # 3. Standardize category and product_category
    print("\n3. Standardizing category and product_category...")
    category_mapping = {
        'clothing': 'Clothing', 'CLOTHING': 'Clothing',
        'electronics': 'Electronics', 'ELECTRONICS': 'Electronics',
        'sports': 'Sports', 'SPORTS': 'Sports',
        'toys': 'Toys', 'TOYS': 'Toys',
        'books': 'Books', 'BOOKS': 'Books',
        'home & garden': 'Home & Garden', 'HOME & GARDEN': 'Home & Garden'
    }

    def standardize_category(val):
        val = str(val).strip().lower() if isinstance(val, str) else val
        return category_mapping.get(val, str(val).title() if isinstance(val, str) else val)

    cleaned_df['category'] = cleaned_df['category'].apply(standardize_category)
    cleaned_df['product_category'] = cleaned_df['product_category'].apply(standardize_category)

    # 🔧 New: Resolve into single unified category
    cleaned_df['final_category'] = cleaned_df.apply(
        lambda row: row['category'] if pd.notna(row['category']) else row['product_category'],
        axis=1
    )

    # 4. Standardize brand and manufacturer names
    print("\n4. Standardizing brand and manufacturer names...")
    def standardize_brand_name(name):
        if pd.isna(name) or name == '':
            return np.nan
        name = re.sub(r'[_-]', ' ', str(name).strip())
        return ' '.join(word.capitalize() for word in name.split())

    cleaned_df['brand'] = cleaned_df['brand'].apply(standardize_brand_name)
    cleaned_df['manufacturer'] = cleaned_df['manufacturer'].apply(standardize_brand_name)

    # 5. Standardize is_active to boolean
    print("\n5. Standardizing is_active column...")
    def standardize_boolean(value):
        if pd.isna(value): return np.nan
        value_str = str(value).lower().strip()
        if value_str in ['true', 'yes', '1', 'active']: return True
        elif value_str in ['false', 'no', '0', 'inactive']: return False
        return np.nan

    cleaned_df['is_active'] = cleaned_df['is_active'].apply(standardize_boolean)

    # 🔧 New: Flag rows where is_active is True but price or stock missing
    cleaned_df['is_active_flag_issue'] = cleaned_df.apply(
        lambda row: True if row['is_active'] is True and (pd.isna(row['price']) or pd.isna(row['stock_quantity']))
        else False, axis=1
    )

    # 6. Standardize color
    print("\n6. Standardizing color names...")
    color_mapping = {
        'black': 'Black', 'white': 'White', 'red': 'Red',
        'blue': 'Blue', 'green': 'Green', 'yellow': 'Yellow',
        'purple': 'Purple', 'orange': 'Orange', 'pink': 'Pink',
        'brown': 'Brown', 'gray': 'Gray', 'grey': 'Gray'
    }
    cleaned_df['color'] = cleaned_df['color'].str.strip().str.lower().map(
        lambda x: color_mapping.get(x, x.title() if isinstance(x, str) else x)
    )

    # 7. Standardize sizes
    print("\n7. Standardizing size values...")
    size_mapping = {
        'xs': 'XS', 's': 'S', 'm': 'M', 'l': 'L', 'xl': 'XL', 'xxl': 'XXL',
        'one size': 'One Size', 'onesize': 'One Size'
    }
    cleaned_df['size'] = cleaned_df['size'].str.strip().str.lower().map(
        lambda x: size_mapping.get(x, x.upper() if isinstance(x, str) else x)
    )

    # 8. Parse date columns
    print("\n8. Cleaning date columns...")
    def parse_date(val):
        if pd.isna(val) or val == '':
            return np.nan
        try:
            if 'T' in str(val):
                return pd.to_datetime(val, format='%Y-%m-%dT%H:%M:%S.%fZ')
            return pd.to_datetime(val, format='%Y-%m-%d')
        except:
            return np.nan

    cleaned_df['created_date'] = cleaned_df['created_date'].apply(parse_date)
    cleaned_df['last_updated'] = cleaned_df['last_updated'].apply(parse_date)

    # 9. Validate dimensions
    print("\n9. Validating dimensions format...")
    def validate_dimensions(dim_str):
        if pd.isna(dim_str) or dim_str == '':
            return np.nan
        if re.match(r'^\d+x\d+x\d+$', str(dim_str)):
            return dim_str
        return np.nan
    cleaned_df['dimensions'] = cleaned_df['dimensions'].apply(validate_dimensions)

    # 10. Compare category vs product_category
    print("\n10. Checking category consistency...")
    cleaned_df['category_mismatch'] = (
        cleaned_df['category'] != cleaned_df['product_category']
    ) & cleaned_df['category'].notna() & cleaned_df['product_category'].notna()

    # 11. Validate numeric ranges
    print("\n11. Validating numeric ranges...")
    for col in ['price', 'list_price', 'cost']:
        cleaned_df.loc[cleaned_df[col] < 0, col] = np.nan

    for col in ['stock_quantity', 'stock_level', 'reorder_level']:
        cleaned_df.loc[cleaned_df[col] < 0, col] = 0

    if 'rating' in cleaned_df.columns:
        cleaned_df['rating'] = pd.to_numeric(cleaned_df['rating'], errors='coerce')
        cleaned_df.loc[(cleaned_df['rating'] < 0) | (cleaned_df['rating'] > 5), 'rating'] = np.nan

    # 12. Handle item_id vs product_id (keep both for now)
    print("\n12. Checking item_id vs product_id mapping...")

    # 🔧 Future: validate if item_id is always consistent with product_id via cross-dataset

    # 13. Cleaning Summary
    print("\n13. Creating data quality summary...")
    missing_summary = (cleaned_df.isnull().sum() / len(cleaned_df) * 100).round(2)
    missing_summary = missing_summary[missing_summary > 0].sort_values(ascending=False)

    print(f"\nCleaning completed!")
    print(f"Final dataset shape: {cleaned_df.shape}")
    print(f"\nRemaining missing values by column:")
    for col, pct in missing_summary.items():
        print(f"  {col}: {pct}%")

    return cleaned_df

def generate_cleaning_report(original_df, cleaned_df):
    return {
        'dataset_info': {
            'original_shape': original_df.shape,
            'cleaned_shape': cleaned_df.shape,
        },
        'missing_values': {
            'before': (original_df.isnull().sum() / len(original_df) * 100).round(2).to_dict(),
            'after': (cleaned_df.isnull().sum() / len(cleaned_df) * 100).round(2).to_dict()
        },
        'data_types': {
            'before': original_df.dtypes.to_dict(),
            'after': cleaned_df.dtypes.to_dict()
        }
    }

# Example usage:
if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'products_inconsistent_data.json')
    df = pd.read_json(file_path)

    cleaned_df = clean_product_dataset(df)

    report = generate_cleaning_report(df, cleaned_df)

    save_path = os.path.join(os.path.dirname(__file__), '..', 'cleaned', 'products_cleaned_data.json')
    cleaned_df.to_json(save_path, orient='records', indent=2)

    print("\n Cleaned product data saved.")
