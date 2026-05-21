import pandas as pd
from sqlalchemy import text
from datetime import datetime
from config.db_config import pg_raw, pg_dw

def clean_and_strip(df):
    """تنظيف النصوص وإزالة المسافات الزائدة من جميع المعرفات"""
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
    return df

# =====================================================
# 1. DIM PRODUCTS (SCD2)
# =====================================================
def load_dim_products():
    print("⏳ Processing dim_products...")
    
    # جلب البيانات من المصدر والمستودع
    source = pd.read_sql("SELECT * FROM products", pg_raw)
    source = clean_and_strip(source).drop_duplicates(subset=["product_id"])
    
    existing = pd.read_sql("SELECT * FROM dim_products WHERE is_current = TRUE", pg_dw)
    existing = clean_and_strip(existing)

    # المقارنة باستخدام Left Merge
    compare = source.merge(existing, on="product_id", how="left", suffixes=("_new", "_old"))
    
    # تحديد السجلات الجديدة والمتغيرة
    new_rows = compare[compare["product_sk"].isna()].copy()
    
    # التحقق من وجود الأعمدة القديمة لتجنب الـ KeyError في أول تشغيل
    if "product_category_name_old" in compare.columns:
        changed_rows = compare[
            compare["product_sk"].notna() & 
            (compare["product_category_name_new"].fillna("") != compare["product_category_name_old"].fillna(""))
        ].copy()
    else:
        changed_rows = pd.DataFrame()

    effective_now = datetime.now()

    # تحديث السجلات التي تغيرت (SCD2 Update)
    if not changed_rows.empty:
        with pg_dw.begin() as conn:
            conn.execute(text("""
                UPDATE dim_products SET end_date = :now, is_current = FALSE 
                WHERE product_id = ANY(:ids) AND is_current = TRUE
            """), {"now": effective_now, "ids": changed_rows["product_id"].tolist()})

    # تحضير البيانات الجديدة للإدخال
    to_insert = pd.concat([new_rows, changed_rows], ignore_index=True)
    
    if not to_insert.empty:
        # إعادة تسمية الأعمدة
        cols_to_rename = {col: col.replace('_new', '') for col in to_insert.columns if col.endswith('_new')}
        to_insert = to_insert.rename(columns=cols_to_rename)
        
        # معالجة رقم الإصدار (Version Control)
        if "version_old" in to_insert.columns:
            to_insert["version"] = to_insert["version_old"].fillna(0).astype(int) + 1
        else:
            to_insert["version"] = 1
            
        to_insert["start_date"] = effective_now
        to_insert["end_date"] = None
        to_insert["is_current"] = True

        final_cols = [
            'product_id', 'product_category_name', 'product_weight_g', 
            'product_length_cm', 'product_height_cm', 'product_width_cm',
            'start_date', 'end_date', 'is_current', 'version'
        ]
        
        to_insert_final = to_insert[final_cols].where(pd.notnull(to_insert), None)
        to_insert_final.to_sql("dim_products", pg_dw, if_exists="append", index=False, method="multi")
        print(f"✅ dim_products: {len(to_insert_final)} rows inserted.")
    else:
        print("ℹ️ No new or changed products found.")

# =====================================================
# 2. DIM CUSTOMERS (SCD2)
# =====================================================
def load_dim_customers():
    print("⏳ Processing dim_customers with first purchase dates...")
    
    # 1. جلب بيانات العملاء والطلبات من المصدر الخام
    source = pd.read_sql("SELECT * FROM customers", pg_raw)
    orders = pd.read_sql("SELECT customer_id, order_purchase_timestamp FROM orders", pg_raw)
    
    # 2. تنظيف المعرفات
    source = clean_and_strip(source).drop_duplicates(subset=["customer_id"])
    orders = clean_and_strip(orders)
    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])

    # 3. حساب تاريخ أول عملية شراء لكل customer_id
    first_purchases = orders.groupby("customer_id")["order_purchase_timestamp"].min().reset_index()
    first_purchases.columns = ["customer_id", "first_purchase_date"]

    # 4. دمج تاريخ الشراء مع بيانات العميل
    source = source.merge(first_purchases, on="customer_id", how="left")
    
    # إذا لم يكن للعميل طلب (حالة نادرة)، نستخدم تاريخ اليوم كاحتياطي
    source["first_purchase_date"] = source["first_purchase_date"].fillna(datetime.now())

    # 5. جلب البيانات الموجودة حالياً في المستودع للمقارنة (SCD2)
    existing = pd.read_sql("SELECT * FROM dim_customers WHERE is_current = TRUE", pg_dw)
    existing = clean_and_strip(existing)

    compare = source.merge(existing, on="customer_id", how="left", suffixes=("_new", "_old"))
    
    # تحديد السجلات الجديدة والمتغيرة (مثلاً تغير المدينة)
    new_rows = compare[compare["customer_sk"].isna()].copy()
    
    if "customer_city_old" in compare.columns:
        changed_rows = compare[
            compare["customer_sk"].notna() & 
            (compare["customer_city_new"] != compare["customer_city_old"])
        ].copy()
    else:
        changed_rows = pd.DataFrame()

    effective_now = datetime.now()

    # تحديث السجلات القديمة إذا تغيرت البيانات
    if not changed_rows.empty:
        with pg_dw.begin() as conn:
            conn.execute(text("""
                UPDATE dim_customers SET end_date = :now, is_current = FALSE 
                WHERE customer_id = ANY(:ids) AND is_current = TRUE
            """), {"now": effective_now, "ids": changed_rows["customer_id"].tolist()})

    # تحضير السجلات الجديدة للإدخال
    to_insert = pd.concat([new_rows, changed_rows], ignore_index=True)
    
    if not to_insert.empty:
        cols_to_rename = {col: col.replace('_new', '') for col in to_insert.columns if col.endswith('_new')}
        to_insert = to_insert.rename(columns=cols_to_rename)
        
        # استخدام تاريخ أول شراء كـ start_date
        to_insert["start_date"] = to_insert["first_purchase_date"]
        to_insert["is_current"] = True
        
        final_cols = ['customer_id', 'customer_unique_id', 'customer_zip_code_prefix', 
                      'customer_city', 'customer_state', 'start_date', 'is_current']
        
        to_insert_final = to_insert[final_cols].where(pd.notnull(to_insert), None)
        to_insert_final.to_sql("dim_customers", pg_dw, if_exists="append", index=False, method="multi")
        print(f"✅ dim_customers: {len(to_insert_final)} rows inserted with purchase timestamps.")


# =====================================================
# 3. DIM SELLERS (SCD2)
# =====================================================
def load_dim_sellers():
    print("⏳ Processing dim_sellers...")
    source = pd.read_sql("SELECT * FROM sellers", pg_raw)
    source = clean_and_strip(source).drop_duplicates(subset=["seller_id"])
    
    existing = pd.read_sql("SELECT * FROM dim_sellers WHERE is_current = TRUE", pg_dw)
    existing = clean_and_strip(existing)

    compare = source.merge(existing, on="seller_id", how="left", suffixes=("_new", "_old"))
    
    new_rows = compare[compare["seller_sk"].isna()].copy()
    effective_now = datetime.now()
    
    if not new_rows.empty:
        cols_to_rename = {col: col.replace('_new', '') for col in new_rows.columns if col.endswith('_new')}
        new_rows = new_rows.rename(columns=cols_to_rename)
        new_rows["start_date"] = effective_now
        new_rows["is_current"] = True
        
        final_cols = ['seller_id', 'seller_zip_code_prefix', 'seller_city', 'seller_state', 'start_date', 'is_current']
        
        new_rows[final_cols].to_sql("dim_sellers", pg_dw, if_exists="append", index=False, method="multi")
        print(f"✅ dim_sellers: {len(new_rows)} rows inserted.")
