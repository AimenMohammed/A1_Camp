import pandas as pd

def clean_strings(df):
    df = df.copy()
    str_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip().replace({"nan": None, "None": None})
    return df

def create_date_key(series):
    return pd.to_datetime(series, errors='coerce').dt.strftime("%Y%m%d").astype("Int64")
