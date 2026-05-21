import pandas as pd
from sqlalchemy import text
from config.db_config import pg_raw, pg_dw

def clean_ids(df, column_list):
    """تنظيف المعرفات النصية لضمان مطابقة الـ Merge"""
    for col in column_list:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df

# =====================================================
# 1. FACT ORDERS
# =====================================================
def load_fact_orders():
    print("⏳ Loading fact_orders...")
    orders = pd.read_sql("SELECT * FROM orders", pg_raw)
    dim_cust = pd.read_sql("SELECT customer_sk, customer_id FROM dim_customers WHERE is_current = TRUE", pg_dw)

    orders = clean_ids(orders, ['customer_id', 'order_id'])
    dim_cust = clean_ids(dim_cust, ['customer_id'])

    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"], errors="coerce")
    orders["purchase_date_key"] = orders["order_purchase_timestamp"].dt.strftime("%Y%m%d").astype("Int64")
    
    fact_orders = orders.merge(dim_cust, on="customer_id", how="left")
    
    cols = ["order_id", "customer_sk", "order_status", "purchase_date_key", "order_purchase_timestamp"]
    final_df = fact_orders[cols].copy()
    final_df = final_df.where(pd.notnull(final_df), None).drop_duplicates(subset=["order_id"])

    with pg_dw.begin() as conn:
        conn.execute(text("TRUNCATE TABLE fact_orders CASCADE"))
        final_df.to_sql("fact_orders", conn, if_exists="append", index=False, method="multi")
    
    print(f"✅ fact_orders loaded: {len(final_df)} rows.")

# =====================================================
# 2. FACT PAYMENTS (Updated: Direct Text Mode)
# =====================================================
def load_fact_payments():
    print("⏳ Loading fact_payments (Direct Text Mode)...")
    
    # 1. جلب البيانات من المصدر وخريطة الطلبات فقط
    payments = pd.read_sql("SELECT * FROM order_payments", pg_raw)
    orders_map = pd.read_sql("SELECT order_sk, order_id FROM fact_orders", pg_dw)

    # 2. تنظيف البيانات
    payments = clean_ids(payments, ['order_id', 'payment_type'])
    orders_map = clean_ids(orders_map, ['order_id'])

    # 3. الربط مع خريطة الطلبات للحصول على المفتاح الرقمي للطلب order_sk
    df = payments.merge(orders_map, on="order_id", how="inner")
    
    # 4. اختيار الأعمدة (استخدام payment_type النصي مباشرة كما في الـ Schema الجديد)
    cols_for_db = [
        "order_sk", 
        "payment_sequential", 
        "payment_type", 
        "payment_installments", 
        "payment_value"
    ]
    
    final_df = df[cols_for_db].copy()
    final_df = final_df.where(pd.notnull(final_df), None)

    # 5. الإدخال في المستودع
    with pg_dw.begin() as conn:
        conn.execute(text("TRUNCATE TABLE fact_payments CASCADE"))
        final_df.to_sql("fact_payments", conn, if_exists="append", index=False, method="multi")
    
    print(f"✅ fact_payments loaded: {len(final_df)} rows.")

# =====================================================
# 3. FACT ORDER ITEMS
# =====================================================
def load_fact_order_items():
    print("⏳ Loading fact_order_items...")
    items = pd.read_sql("SELECT * FROM order_items", pg_raw)
    dim_prod = pd.read_sql("SELECT product_sk, product_id FROM dim_products WHERE is_current = TRUE", pg_dw)
    dim_sell = pd.read_sql("SELECT seller_sk, seller_id FROM dim_sellers WHERE is_current = TRUE", pg_dw)
    orders_map = pd.read_sql("SELECT order_sk, order_id FROM fact_orders", pg_dw)

    items = clean_ids(items, ['order_id', 'product_id', 'seller_id'])
    dim_prod = clean_ids(dim_prod, ['product_id'])
    dim_sell = clean_ids(dim_sell, ['seller_id'])
    orders_map = clean_ids(orders_map, ['order_id'])

    df = items.merge(dim_prod, on="product_id", how="left")
    df = df.merge(dim_sell, on="seller_id", how="left")
    df = df.merge(orders_map, on="order_id", how="inner") 
    
    cols = ["order_sk", "product_sk", "seller_sk", "price", "freight_value"]
    final_df = df[cols].copy()
    final_df = final_df.where(pd.notnull(final_df), None)

    with pg_dw.begin() as conn:
        conn.execute(text("TRUNCATE TABLE fact_order_items CASCADE"))
        final_df.to_sql("fact_order_items", conn, if_exists="append", index=False, method="multi")
    
    print(f"✅ fact_order_items loaded.")
