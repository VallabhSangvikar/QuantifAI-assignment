import pandas as pd

def summarize_dataframe(df: pd.DataFrame, dataset_name: str):
    summaries = []

    for col in df.columns:
        # Drop missing values
        col_data = df[col].dropna()

        # Detect types
        types = col_data.map(lambda x: type(x).__name__).value_counts().to_dict()

        # Get sample values
        samples = col_data.unique()[:5].tolist()

        # Null percentage
        null_pct = round(df[col].isnull().mean() * 100, 2)

        # Unique value count
        unique_count = df[col].nunique()

        # Note obvious issues (example: case inconsistencies)
        notes = ""
        if all(isinstance(v, str) for v in col_data[:50]):
            lower = col_data.str.lower().nunique()
            upper = col_data.str.upper().nunique()
            if lower != upper:
                notes += "Possible casing inconsistency. "

        if len(types) > 1:
            notes += f"Multiple types found: {list(types.keys())}. "

        summaries.append({
            "dataset": dataset_name,
            "column": col,
            "types": list(types.keys()),
            "sample_values": samples,
            "unique_count": unique_count,
            "null_percentage": null_pct,
            "notes": notes.strip()
        })

    return summaries

