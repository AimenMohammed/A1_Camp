from sqlalchemy import create_engine

# Connection Strings
RAW_URL = "postgresql://postgres:aimen@localhost:5432/raw_data"
DW_URL = "postgresql://postgres:aimen@localhost:5432/data_warehouse"
SQLITE_URL = "sqlite:///olist.sqlite"

# Engines
pg_raw = create_engine(RAW_URL)
pg_dw = create_engine(DW_URL)
sqlite_engine = create_engine(SQLITE_URL)
