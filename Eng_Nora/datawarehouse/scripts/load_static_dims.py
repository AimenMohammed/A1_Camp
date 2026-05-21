import pandas as pd
from sqlalchemy import text
from config.db_config import pg_raw, pg_dw

def load_dim_date():
    print("Checking dim_date...")
    
    # Check if data already exists to avoid duplicates
    try:
        existing_count = pd.read_sql("SELECT count(*) FROM dim_date", pg_dw).iloc[0, 0]
        if existing_count > 0:
            print("dim_date already has data. Skipping generation.")
            return
    except:
        pass 

    print("Generating date range (2010-2030)...")
    start_date = "2010-01-01"
    end_date = "2030-12-31"
    date_range = pd.date_range(start=start_date, end=end_date)
    
    dim_date = pd.DataFrame({"full_date": date_range})
    
    dim_date["date_key"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["year"] = dim_date["full_date"].dt.year
    dim_date["month"] = dim_date["full_date"].dt.month
    dim_date["day"] = dim_date["full_date"].dt.day
    dim_date["week"] = dim_date["full_date"].dt.isocalendar().week.astype(int)
    dim_date["quarter"] = dim_date["full_date"].dt.quarter
    dim_date["day_name"] = dim_date["full_date"].dt.day_name()
    dim_date["month_name"] = dim_date["full_date"].dt.month_name()
    dim_date["is_weekend"] = dim_date["full_date"].dt.weekday >= 5

    dim_date.to_sql("dim_date", pg_dw, if_exists="append", index=False, method="multi")
    print(f"dim_date loaded: {len(dim_date)} rows.")

def load_dim_payment_type():
    print("Loading dim_payment_type...")
    
    # 1. Extract unique types from Raw Data
    try:
        # We look at the order_payments table in your raw schema
        query = "SELECT DISTINCT payment_type FROM raw_data.order_payments"
        df_types = pd.read_sql(query, pg_raw)
    except Exception as e:
        print(f"Error reading raw payments: {e}")
        return

    if df_types.empty:
        print("No payment types found in raw data.")
        return

    # 2. Prepare for Data Warehouse
    df_types = df_types.dropna()
    
    # 3. Load to Warehouse
    try:
        # We truncate and restart identity so the IDs (1, 2, 3...) are clean every time
        with pg_dw.begin() as conn:
            conn.execute(text("TRUNCATE TABLE dim_payment_type RESTART IDENTITY CASCADE"))
            
        df_types.to_sql(
            "dim_payment_type", 
            pg_dw, 
            if_exists="append", 
            index=False
        )
        print(f"dim_payment_type loaded: {list(df_types['payment_type'].values)}")
    except Exception as e:
        print(f"Error loading dim_payment_type: {e}")
