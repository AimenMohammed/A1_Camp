import pandas as pd
from sqlalchemy import text
from config.db_config import pg_raw, sqlite_engine

def create_table_schema(table_name):
    """
    Reads 1 row from SQLite to clone the schema into PostgreSQL.
    """
    df = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 1", sqlite_engine)
    
    df.head(0).to_sql(
        table_name,
        pg_raw,
        if_exists="replace",
        index=False
    )
    print(f"  ∟ Schema created for: {table_name}")

def run_extraction():
    """
    Main function to extract all tables from SQLite to pg_raw.
    """
    tables = [
        "customers", "orders", "order_items", "order_payments",
        "order_reviews", "products", "sellers", "geolocation",
        "leads_qualified", "leads_closed", "product_category_name_translation"
    ]

    print("Starting Raw Extraction (SQLite -> Postgres)...")

    for table in tables:
        try:
            # 1. Prepare the table structure in Postgres
            create_table_schema(table)

            # 2. Extract full dataset from SQLite
            df = pd.read_sql(f"SELECT * FROM {table}", sqlite_engine)

            # 3. Clean the table (Truncate) to ensure no duplicates if re-run
            with pg_raw.begin() as conn:
                conn.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))

            # 4. Load into Postgres
            df.to_sql(
                table,
                pg_raw,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=10000  # Optimized for speed
            )

            print(f"Loaded {table}: {len(df)} rows")

        except Exception as e:
            print(f"Error extracting {table}: {e}")

    print("Raw Extraction Layer Complete.\n")

if __name__ == "__main__":
    run_extraction()
