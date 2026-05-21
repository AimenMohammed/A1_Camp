from sqlalchemy import text
from config.db_config import pg_dw

def create_warehouse_schema():
    commands = [
        # 1. إعادة ضبط المخطط (حذف وإنشاء من جديد)
        "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;",

        # 2. جدول أبعاد التاريخ (Static)
        """
        CREATE TABLE dim_date (
            date_key INTEGER PRIMARY KEY,
            full_date DATE,
            year INTEGER,
            month INTEGER,
            day INTEGER,
            week INTEGER,
            quarter INTEGER,
            day_name VARCHAR(10),
            month_name VARCHAR(10),
            is_weekend BOOLEAN
        );
        """,

        # 3. جدول أبعاد العملاء (SCD Type 2)
        """
        CREATE TABLE dim_customers (
            customer_sk SERIAL PRIMARY KEY,
            customer_id TEXT, 
            customer_unique_id TEXT,
            customer_zip_code_prefix INTEGER,
            customer_city TEXT,
            customer_state TEXT,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            is_current BOOLEAN DEFAULT TRUE,
            version INTEGER DEFAULT 1
        );
        CREATE INDEX idx_cust_id ON dim_customers(customer_id);
        """,

        # 4. جدول أبعاد المنتجات (SCD Type 2)
        """
        CREATE TABLE dim_products (
            product_sk SERIAL PRIMARY KEY,
            product_id TEXT,
            product_category_name TEXT,
            product_weight_g BIGINT,
            product_length_cm BIGINT,
            product_height_cm BIGINT,
            product_width_cm BIGINT,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            is_current BOOLEAN DEFAULT TRUE,
            version INTEGER DEFAULT 1
        );
        CREATE INDEX idx_prod_id ON dim_products(product_id);
        """,

        # 5. جدول أبعاد البائعين
        """
        CREATE TABLE dim_sellers (
            seller_sk SERIAL PRIMARY KEY,
            seller_id TEXT,
            seller_zip_code_prefix INTEGER,
            seller_city TEXT,
            seller_state TEXT,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            is_current BOOLEAN DEFAULT TRUE,
            version INTEGER DEFAULT 1
        );
        """,

        # 6. جدول حقائق الطلبات (Fact Orders)
        """
        CREATE TABLE fact_orders (
            order_sk SERIAL PRIMARY KEY, 
            order_id TEXT UNIQUE, 
            customer_sk INTEGER REFERENCES dim_customers(customer_sk),
            order_status TEXT,
            purchase_date_key INTEGER REFERENCES dim_date(date_key),
            order_purchase_timestamp TIMESTAMP,
            order_approved_at TIMESTAMP,
            order_delivered_carrier_date TIMESTAMP,
            order_delivered_customer_date TIMESTAMP,
            order_estimated_delivery_date TIMESTAMP,
            load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_fact_orders_sk ON fact_orders(order_sk);
        CREATE INDEX idx_fact_orders_id ON fact_orders(order_id);
        """,

        # 7. جدول حقائق عناصر الطلب (Fact Order Items)
        """
        CREATE TABLE fact_order_items (
            fact_item_id SERIAL PRIMARY KEY,
            order_sk INTEGER REFERENCES fact_orders(order_sk),
            product_sk INTEGER REFERENCES dim_products(product_sk),
            seller_sk INTEGER REFERENCES dim_sellers(seller_sk),
            shipping_limit_date TIMESTAMP,
            price NUMERIC(10, 2),
            freight_value NUMERIC(10, 2),
            shipping_date_key INTEGER REFERENCES dim_date(date_key)
        );
        """,

        # 8. جدول حقائق المدفوعات (Fact Payments)
        # تم استبدال المفتاح الأجنبي بعمود نصي مباشر (payment_type)
        """
        CREATE TABLE fact_payments (
            payment_id SERIAL PRIMARY KEY,
            order_sk INTEGER REFERENCES fact_orders(order_sk),
            payment_sequential INTEGER,
            payment_type TEXT, 
            payment_installments INTEGER,
            payment_value NUMERIC(10, 2)
        );
        """,

        # 9. جدول حقائق التقييمات (Fact Reviews)
        """
        CREATE TABLE fact_reviews (
            review_sk SERIAL PRIMARY KEY,
            review_id TEXT,
            order_sk INTEGER REFERENCES fact_orders(order_sk),
            review_score INTEGER,
            review_comment_title TEXT,
            review_comment_message TEXT,
            review_creation_date TIMESTAMP,
            review_answer_timestamp TIMESTAMP,
            review_date_key INTEGER REFERENCES dim_date(date_key)
        );
        """,
        
        # 10. REPORTING VIEW (The Gold Layer)
        # تم تعديل الربط ليأخذ payment_type مباشرة من جدول الحقائق
        """
        CREATE OR REPLACE VIEW reporting_sales_master AS
        SELECT 
            o.order_id,
            d.full_date,
            d.year,
            d.month_name,
            c.customer_unique_id,
            c.customer_city,
            c.customer_state,
            p.product_category_name,
            s.seller_city AS seller_location,
            pay.payment_type, 
            i.price,
            i.freight_value,
            (i.price + i.freight_value) AS item_total_cost,
            pay.payment_value AS actual_amount_paid
        FROM fact_orders o
        JOIN dim_date d ON o.purchase_date_key = d.date_key
        JOIN dim_customers c ON o.customer_sk = c.customer_sk
        JOIN fact_order_items i ON o.order_sk = i.order_sk
        JOIN dim_products p ON i.product_sk = p.product_sk
        JOIN dim_sellers s ON i.seller_sk = s.seller_sk
        JOIN fact_payments pay ON o.order_sk = pay.order_sk;
        """
    ]

    print("Building Data Warehouse Schema (Denormalized Payment Mode)...")
    with pg_dw.begin() as conn:
        for cmd in commands:
            conn.execute(text(cmd))
    print("Schema built successfully. Payment types are now stored directly in fact_payments.")

if __name__ == "__main__":
    create_warehouse_schema()
