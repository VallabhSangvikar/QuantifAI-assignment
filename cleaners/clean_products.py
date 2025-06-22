# import pandas as pd
# import numpy as np
# from datetime import datetime
# import re
# import os

# def clean_product_dataset(df):
#     """
#     Comprehensive function to clean product dataset addressing all identified data quality issues.
    
#     Args:
#         df (pandas.DataFrame): Raw product dataset
        
#     Returns:
#         pandas.DataFrame: Cleaned dataset
#     """
#     # Create a copy to avoid modifying original data
#     cleaned_df = df.copy()
    
#     print("Starting data cleaning process...")
#     print(f"Initial dataset shape: {cleaned_df.shape}")
    
#     # 1. Handle missing values represented as empty strings and convert to NaN
#     print("\n1. Converting empty strings to NaN...")
#     string_columns = ['description', 'brand', 'manufacturer', 'color', 'size', 
#                      'supplier_id', 'created_date', 'last_updated', 'dimensions']
    
#     for col in string_columns:
#         if col in cleaned_df.columns:
#             cleaned_df[col] = cleaned_df[col].replace('', np.nan)
    
#     # 2. Fix data types - Convert price columns from string to float
#     print("\n2. Converting price columns to proper numeric types...")
#     price_columns = ['price', 'list_price', 'cost', 'weight']
    
#     for col in price_columns:
#         if col in cleaned_df.columns:
#             # Convert to numeric, handling any non-numeric values
#             cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
    
#     # 3. Standardize categorical columns - Fix inconsistent casing
#     print("\n3. Standardizing categorical columns...")
    
#     # Standardize category column
#     if 'category' in cleaned_df.columns:
#         category_mapping = {
#             'clothing': 'Clothing',
#             'CLOTHING': 'Clothing',
#             'electronics': 'Electronics',
#             'ELECTRONICS': 'Electronics',
#             'sports': 'Sports',
#             'SPORTS': 'Sports',
#             'toys': 'Toys',
#             'TOYS': 'Toys',
#             'books': 'Books',
#             'BOOKS': 'Books',
#             'home & garden': 'Home & Garden',
#             'HOME & GARDEN': 'Home & Garden'
#         }
#         cleaned_df['category'] = cleaned_df['category'].str.strip().str.lower().map(
#             lambda x: category_mapping.get(x, x.title() if isinstance(x, str) else x)
#         )
    
#     # Standardize product_category column
#     if 'product_category' in cleaned_df.columns:
#         cleaned_df['product_category'] = cleaned_df['product_category'].str.strip().str.lower().map(
#             lambda x: category_mapping.get(x, x.title() if isinstance(x, str) else x)
#         )
    
#     # 4. Standardize brand and manufacturer names
#     print("\n4. Standardizing brand and manufacturer names...")
    
#     def standardize_brand_name(brand_name):
#         """Standardize brand name format"""
#         if pd.isna(brand_name) or brand_name == '':
#             return np.nan
        
#         # Remove special characters and standardize format
#         brand_name = str(brand_name).strip()
#         brand_name = re.sub(r'[_-]', ' ', brand_name)  # Replace underscores and hyphens with spaces
        
#         # Convert to title case for consistency
#         brand_name = ' '.join([word.capitalize() for word in brand_name.split()])
        
#         return brand_name
    
#     if 'brand' in cleaned_df.columns:
#         cleaned_df['brand'] = cleaned_df['brand'].apply(standardize_brand_name)
    
#     if 'manufacturer' in cleaned_df.columns:
#         cleaned_df['manufacturer'] = cleaned_df['manufacturer'].apply(standardize_brand_name)
    
#     # 5. Standardize is_active column to boolean
#     print("\n5. Standardizing is_active column...")
#     if 'is_active' in cleaned_df.columns:
#         def standardize_boolean(value):
#             if pd.isna(value):
#                 return np.nan
            
#             value_str = str(value).lower().strip()
#             if value_str in ['true', 'yes', '1', 'active']:
#                 return True
#             elif value_str in ['false', 'no', '0', 'inactive']:
#                 return False
#             else:
#                 return np.nan
        
#         cleaned_df['is_active'] = cleaned_df['is_active'].apply(standardize_boolean)
    
#     # 6. Standardize color names
#     print("\n6. Standardizing color names...")
#     if 'color' in cleaned_df.columns:
#         color_mapping = {
#             'black': 'Black',
#             'white': 'White',
#             'red': 'Red',
#             'blue': 'Blue',
#             'green': 'Green',
#             'yellow': 'Yellow',
#             'purple': 'Purple',
#             'orange': 'Orange',
#             'pink': 'Pink',
#             'brown': 'Brown',
#             'gray': 'Gray',
#             'grey': 'Gray'
#         }
        
#         cleaned_df['color'] = cleaned_df['color'].str.strip().str.lower().map(
#             lambda x: color_mapping.get(x, x.title() if isinstance(x, str) else x)
#         )
    
#     # 7. Standardize size values
#     print("\n7. Standardizing size values...")
#     if 'size' in cleaned_df.columns:
#         size_mapping = {
#             'xs': 'XS',
#             'XS': 'XS',
#             's': 'S',
#             'S': 'S',
#             'm': 'M',
#             'M': 'M',
#             'l': 'L',
#             'L': 'L',
#             'xl': 'XL',
#             'XL': 'XL',
#             'xxl': 'XXL',
#             'XXL': 'XXL',
#             'one size': 'One Size',
#             'ONE SIZE': 'One Size',
#             'onesize': 'One Size'
#         }
        
#         cleaned_df['size'] = cleaned_df['size'].str.strip().map(
#             lambda x: size_mapping.get(x, x if isinstance(x, str) else x)
#         )
    
#     # 8. Validate and clean date columns
#     print("\n8. Cleaning date columns...")
    
#     def clean_date_column(date_series):
#         """Clean and standardize date format"""
#         cleaned_dates = []
#         for date_val in date_series:
#             if pd.isna(date_val) or date_val == '':
#                 cleaned_dates.append(np.nan)
#             else:
#                 try:
#                     # Try to parse the date
#                     if 'T' in str(date_val):  # ISO format
#                         parsed_date = pd.to_datetime(date_val, format='%Y-%m-%dT%H:%M:%S.%fZ')
#                     else:  # Simple date format
#                         parsed_date = pd.to_datetime(date_val, format='%Y-%m-%d')
#                     cleaned_dates.append(parsed_date)
#                 except:
#                     cleaned_dates.append(np.nan)
#         return cleaned_dates
    
#     if 'created_date' in cleaned_df.columns:
#         cleaned_df['created_date'] = clean_date_column(cleaned_df['created_date'])
    
#     if 'last_updated' in cleaned_df.columns:
#         cleaned_df['last_updated'] = clean_date_column(cleaned_df['last_updated'])
    
#     # 9. Validate dimensions format
#     print("\n9. Validating dimensions format...")
#     if 'dimensions' in cleaned_df.columns:
#         def validate_dimensions(dim_str):
#             if pd.isna(dim_str) or dim_str == '':
#                 return np.nan
            
#             # Check if dimensions follow the pattern NxNxN
#             if re.match(r'^\d+x\d+x\d+$', str(dim_str)):
#                 return dim_str
#             else:
#                 return np.nan
        
#         cleaned_df['dimensions'] = cleaned_df['dimensions'].apply(validate_dimensions)
    
#     # 10. Handle potential redundancy between category and product_category
#     print("\n10. Checking category consistency...")
#     if 'category' in cleaned_df.columns and 'product_category' in cleaned_df.columns:
#         # Create a flag to identify inconsistent categorization
#         cleaned_df['category_mismatch'] = (
#             cleaned_df['category'] != cleaned_df['product_category']
#         ) & (
#             ~cleaned_df['category'].isna() & ~cleaned_df['product_category'].isna()
#         )
    
#     # 11. Validate numeric ranges
#     print("\n11. Validating numeric ranges...")
    
#     # Ensure prices are positive
#     price_cols = ['price', 'list_price', 'cost']
#     for col in price_cols:
#         if col in cleaned_df.columns:
#             cleaned_df.loc[cleaned_df[col] < 0, col] = np.nan
    
#     # Ensure stock quantities are non-negative
#     stock_cols = ['stock_quantity', 'stock_level', 'reorder_level']
#     for col in stock_cols:
#         if col in cleaned_df.columns:
#             cleaned_df.loc[cleaned_df[col] < 0, col] = 0
    
#     # Ensure rating is between 0 and 5
#     if 'rating' in cleaned_df.columns:
#         cleaned_df['rating'] = pd.to_numeric(cleaned_df['rating'], errors='coerce')
#         cleaned_df.loc[(cleaned_df['rating'] < 0) | (cleaned_df['rating'] > 5), 'rating'] = np.nan
    
#     # 12. Remove potential duplicate item_id if it's truly redundant with product_id
#     print("\n12. Checking for redundant columns...")
#     if 'item_id' in cleaned_df.columns and 'product_id' in cleaned_df.columns:
#         # If item_id is just sequential and doesn't add value, we could drop it
#         # But keeping it for now as it might be used elsewhere
#         pass
    
#     # 13. Create data quality summary
#     print("\n13. Creating data quality summary...")
    
#     # Calculate missing value percentages after cleaning
#     missing_summary = (cleaned_df.isnull().sum() / len(cleaned_df) * 100).round(2)
#     missing_summary = missing_summary[missing_summary > 0].sort_values(ascending=False)
    
#     print(f"\nCleaning completed!")
#     print(f"Final dataset shape: {cleaned_df.shape}")
#     print(f"\nRemaining missing values by column:")
#     for col, pct in missing_summary.items():
#         print(f"  {col}: {pct}%")
    
#     return cleaned_df

# def generate_cleaning_report(original_df, cleaned_df):
#     """
#     Generate a detailed report comparing original and cleaned datasets.
    
#     Args:
#         original_df (pandas.DataFrame): Original dataset
#         cleaned_df (pandas.DataFrame): Cleaned dataset
    
#     Returns:
#         dict: Cleaning report with before/after statistics
#     """
    
#     report = {
#         'dataset_info': {
#             'original_shape': original_df.shape,
#             'cleaned_shape': cleaned_df.shape,
#         },
#         'missing_values': {
#             'before': (original_df.isnull().sum() / len(original_df) * 100).round(2).to_dict(),
#             'after': (cleaned_df.isnull().sum() / len(cleaned_df) * 100).round(2).to_dict()
#         },
#         'data_types': {
#             'before': original_df.dtypes.to_dict(),
#             'after': cleaned_df.dtypes.to_dict()
#         }
#     }
    
#     return report

# # Example usage:

# # Load your dataset
# file_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'products_inconsistent_data.json')
# df = pd.read_json(file_path)
# # Clean the dataset
# cleaned_df = clean_product_dataset(df)

# # Generate cleaning report
# report = generate_cleaning_report(df, cleaned_df)
# file_path = os.path.join(os.path.dirname(__file__), '..', 'cleaned', 'products_cleaned_data.json')
# # Save cleaned dataset
# cleaned_df.to_json(file_path, orient='records', indent=2)

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

    print("\n✅ Cleaned product data saved.")
