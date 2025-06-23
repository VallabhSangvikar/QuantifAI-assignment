import os

import pandas as pd
import numpy as np
import re
from datetime import datetime

def clean_customer_data(df):
    """
    Cleans customer data with improved support for downstream joins and formatting.
    """
    df_clean = df.copy()

    # 🔧 Keep customer_id intact; drop cust_id instead
    print("Step 1: Resolving duplicate columns...")
    df_clean.drop('cust_id', axis=1, inplace=True)

    # Merge customer_name and full_name
    df_clean['customer_name'] = df_clean.apply(
        lambda row: _merge_names(row['customer_name'], row['full_name']), axis=1
    )
    df_clean.drop('full_name', axis=1, inplace=True)

    # Merge email columns
    df_clean['email'] = df_clean.apply(
        lambda row: _merge_emails(row['email'], row['email_address']), axis=1
    )
    df_clean.drop('email_address', axis=1, inplace=True)

    # Merge phone columns
    df_clean['phone'] = df_clean.apply(
        lambda row: _merge_phones(row['phone'], row['phone_number']), axis=1
    )
    df_clean.drop('phone_number', axis=1, inplace=True)

    # Merge zip code columns
    df_clean['zip_code'] = df_clean.apply(
        lambda row: _merge_zip_codes(row['zip_code'], row['postal_code']), axis=1
    )
    df_clean.drop('postal_code', axis=1, inplace=True)

    # Merge registration date columns
    df_clean['registration_date'] = df_clean.apply(
        lambda row: _merge_dates(row['registration_date'], row['reg_date']), axis=1
    )
    df_clean.drop('reg_date', axis=1, inplace=True)

    # Merge status columns
    df_clean['status'] = df_clean.apply(
        lambda row: _merge_status(row['status'], row['customer_status']), axis=1
    )
    df_clean.drop('customer_status', axis=1, inplace=True)

    print("Step 2: Standardizing data formats...")
    df_clean['phone'] = df_clean['phone'].apply(_standardize_phone)
    df_clean['registration_date'] = df_clean['registration_date'].apply(_standardize_date)
    df_clean['birth_date'] = df_clean['birth_date'].apply(_standardize_date)
    df_clean['city'] = df_clean['city'].apply(_standardize_city)
    df_clean['state'] = df_clean['state'].apply(_standardize_state)
    df_clean['status'] = df_clean['status'].apply(_standardize_status)
    df_clean['gender'] = df_clean['gender'].apply(_standardize_gender)

    print("Step 3: Handling missing values...")
    null_values = ['', 'null', 'NULL', 'None', 'nan', 'NaN']
    df_clean = df_clean.replace(null_values, np.nan)
    df_clean = df_clean.replace(r'^\s*$', np.nan, regex=True)

    print("Step 4: Correcting data types...")
    df_clean['total_orders'] = pd.to_numeric(df_clean['total_orders'], errors='coerce')
    df_clean['total_spent'] = pd.to_numeric(df_clean['total_spent'], errors='coerce')
    df_clean['loyalty_points'] = pd.to_numeric(df_clean['loyalty_points'], errors='coerce')
    df_clean['age'] = pd.to_numeric(df_clean['age'], errors='coerce')

    # 🔧 Zip code stays string, remove .0 from floats
    df_clean['zip_code'] = df_clean['zip_code'].astype(str).str.replace(r'\.0$', '', regex=True)
    df_clean['zip_code'] = df_clean['zip_code'].replace('nan', np.nan)

    df_clean['registration_date'] = pd.to_datetime(df_clean['registration_date'], errors='coerce')
    df_clean['birth_date'] = pd.to_datetime(df_clean['birth_date'], errors='coerce')

    print("Step 5: Performing data validation...")
    df_clean['email'] = df_clean['email'].apply(_validate_email)
    df_clean = _validate_age_consistency(df_clean)
    df_clean = df_clean.drop_duplicates(subset=['customer_id'], keep='first')


    print("Step 6: Generating cleaning summary...")
    _generate_cleaning_summary(df, df_clean)

    return df_clean
# Helper functions
def _merge_names(name1, name2):
    """Merge customer name columns, prioritizing more complete names."""
    if pd.isna(name1) and pd.isna(name2):
        return np.nan
    if pd.isna(name1):
        return name2
    if pd.isna(name2):
        return name1
    
    # If both exist, choose the one that looks more like a full name
    if ' ' in str(name2) and ' ' not in str(name1):
        return name2
    return name1

def _merge_emails(email1, email2):
    """Merge email columns, prioritizing valid email addresses."""
    if pd.isna(email1) and pd.isna(email2):
        return np.nan
    if pd.isna(email1):
        return email2
    if pd.isna(email2):
        return email1
    
    # If both exist, prioritize the one that looks more valid
    if '@' in str(email1) and '@' in str(email2):
        return email1  # Default to first column
    elif '@' in str(email1):
        return email1
    elif '@' in str(email2):
        return email2
    return email1

def _merge_phones(phone1, phone2):
    """Merge phone columns, prioritizing non-empty values."""
    if pd.isna(phone1) and pd.isna(phone2):
        return np.nan
    if pd.isna(phone1) or str(phone1).strip() == '':
        return phone2
    if pd.isna(phone2) or str(phone2).strip() == '':
        return phone1
    
    # If both exist, choose the longer one (likely more complete)
    if len(str(phone1)) >= len(str(phone2)):
        return phone1
    return phone2

def _merge_zip_codes(zip1, zip2):
    """Merge zip code columns, handling different formats."""
    if pd.isna(zip1) and pd.isna(zip2):
        return np.nan
    if pd.isna(zip1):
        return str(zip2).split('-')[0]  # Extract main zip from postal code
    if pd.isna(zip2):
        return str(zip1)
    
    # If both exist, prefer the simpler format
    return str(zip1)

def _merge_dates(date1, date2):
    """Merge date columns, prioritizing non-empty values."""
    if pd.isna(date1) and pd.isna(date2):
        return np.nan
    if pd.isna(date1) or str(date1).strip() == '':
        return date2
    if pd.isna(date2) or str(date2).strip() == '':
        return date1
    return date1

def _merge_status(status1, status2):
    """Merge status columns, prioritizing non-empty values."""
    if pd.isna(status1) and pd.isna(status2):
        return np.nan
    if pd.isna(status1) or str(status1).strip() == '':
        return status2
    if pd.isna(status2) or str(status2).strip() == '':
        return status1
    return status1

def _standardize_phone(phone):
    """Standardize phone number format."""
    if pd.isna(phone):
        return np.nan
    
    # Remove all non-digit characters
    phone_digits = re.sub(r'\D', '', str(phone))
    
    # Format as (XXX) XXX-XXXX for 10-digit numbers
    if len(phone_digits) == 10:
        return f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
    elif len(phone_digits) == 11 and phone_digits[0] == '1':
        # Handle 11-digit numbers starting with 1
        return f"({phone_digits[1:4]}) {phone_digits[4:7]}-{phone_digits[7:]}"
    else:
        return phone  # Return original if format is unclear

def _standardize_date(date_str):
    """Standardize date format to YYYY-MM-DD."""
    if pd.isna(date_str) or str(date_str).strip() == '':
        return np.nan
    
    try:
        # Try different date formats
        for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
            try:
                return datetime.strptime(str(date_str), fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        return date_str  # Return original if no format matches
    except:
        return np.nan

def _standardize_city(city):
    """Standardize city names."""
    if pd.isna(city):
        return np.nan
    
    city_mapping = {
        'nyc': 'New York',
        'la': 'Los Angeles',
        'chi': 'Chicago',
        'houston': 'Houston',
        'phoenix': 'Phoenix'
    }
    
    city_clean = str(city).strip().lower()
    return city_mapping.get(city_clean, str(city).title())

def _standardize_state(state):
    """Standardize state names to abbreviations."""
    if pd.isna(state):
        return np.nan
    
    state_mapping = {
        'california': 'CA',
        'new york': 'NY',
        'texas': 'TX',
        'illinois': 'IL',
        'arizona': 'AZ',
        'pennsylvania': 'PA',
        'florida': 'FL'
    }
    
    state_clean = str(state).strip().lower()
    return state_mapping.get(state_clean, str(state).upper())

def _standardize_status(status):
    """Standardize status values."""
    if pd.isna(status):
        return np.nan
    
    status_mapping = {
        'active': 'Active',
        'inactive': 'Inactive',
        'suspended': 'Suspended',
        'pending': 'Pending'
    }
    
    status_clean = str(status).strip().lower()
    return status_mapping.get(status_clean, str(status).title())

def _standardize_gender(gender):
    """Standardize gender values."""
    if pd.isna(gender):
        return np.nan
    
    gender_mapping = {
        'f': 'Female',
        'female': 'Female',
        'm': 'Male',
        'male': 'Male',
        'other': 'Other'
    }
    
    gender_clean = str(gender).strip().lower()
    return gender_mapping.get(gender_clean, str(gender).title())

def _validate_email(email):
    """Validate email format."""
    if pd.isna(email):
        return np.nan
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, str(email)):
        return email
    return np.nan  # Invalid email becomes null

def _validate_age_consistency(df):
    """Validate age consistency with birth_date."""
    current_year = datetime.now().year
    
    for idx, row in df.iterrows():
        if pd.notna(row['birth_date']) and pd.notna(row['age']):
            birth_year = pd.to_datetime(row['birth_date']).year
            calculated_age = current_year - birth_year
            
            # If ages differ by more than 1 year, prioritize calculated age
            if abs(calculated_age - row['age']) > 1:
                df.loc[idx, 'age'] = calculated_age
        
        elif pd.notna(row['birth_date']) and pd.isna(row['age']):
            # Calculate age from birth_date
            birth_year = pd.to_datetime(row['birth_date']).year
            df.loc[idx, 'age'] = current_year - birth_year
    
    return df

def _generate_cleaning_summary(df_original, df_clean):
    """Generate a summary of the cleaning process."""
    print("\n" + "="*50)
    print("DATA CLEANING SUMMARY")
    print("="*50)
    
    print(f"Original dataset shape: {df_original.shape}")
    print(f"Cleaned dataset shape: {df_clean.shape}")
    print(f"Rows removed: {df_original.shape[0] - df_clean.shape[0]}")
    print(f"Columns removed: {df_original.shape[1] - df_clean.shape[1]}")
    
    print("\nColumns in cleaned dataset:")
    for col in df_clean.columns:
        null_pct = (df_clean[col].isna().sum() / len(df_clean)) * 100
        print(f"  {col}: {null_pct:.1f}% missing")
    
    print("\nData types in cleaned dataset:")
    print(df_clean.dtypes)
    
    print("\nCleaning completed successfully!")

# Example usage
if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'customers_messy_data.json')
    df = pd.read_json(file_path)
    df_cleaned = clean_customer_data(df)
    file_path = os.path.join(os.path.dirname(__file__), '..', 'cleaned', 'customers_cleaned_data.json')
    df_cleaned.to_json(file_path, orient='records', indent=2)

    print("\n Cleaned data saved to 'customers_cleaned_data.json'")
    print(df_cleaned.head())

