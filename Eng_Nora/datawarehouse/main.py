import sys
from sqlalchemy import text, inspect
from config.db_config import pg_dw

# استيراد الوظائف
from scripts.create_schema import create_warehouse_schema
from scripts.init_raw_db import initialize_raw_tables
from extract_raw import run_extraction
from scripts.load_static_dims import load_dim_date
from scripts.load_dimensions import load_dim_products, load_dim_customers, load_dim_sellers
from scripts.load_facts import load_fact_orders, load_fact_payments, load_fact_order_items

def show_menu():
    print("\n" + "="*40)
    print("      E-COMMERCE DWH CONTROL CENTER")
    print("="*40)
    print("1. 🚀 Run Full ETL Pipeline (Load All Data)")
    print("2. 📈 Trend Analysis: Sales Over Time")
    print("3. 🏆 Customer Analysis: Most Valuable Customers")
    print("4. 🚚 Logistics: Delivery Performance Factors")
    print("5. 💰 Product Analysis: Revenue by Category")
    print("0. 🚪 Exit")
    print("="*40)

def run_full_etl():
    print("\n--- Starting Full ETL Pipeline ---")
    # 1. تهيئة جداول البيانات الخام
    initialize_raw_tables()
    
    # 2. بناء المخطط إذا لم يكن موجوداً
    inspector = inspect(pg_dw)
    if not inspector.has_table("dim_products"):
        print("Building Warehouse Schema...")
        create_warehouse_schema()
        
    # 3. استخراج البيانات من المصادر
    run_extraction()
    
    # 4. تحميل جداول الأبعاد
    load_dim_date()
    load_dim_products()
    load_dim_customers()
    load_dim_sellers()
    
    # 5. تحميل جداول الحقائق
    load_fact_orders()
    load_fact_payments() # سيعمل الآن بنظام النص المباشر
    load_fact_order_items()
    
    print("\n✅ ETL Process Finished Successfully!")

def run_query(query_title, sql_code):
    print(f"\n--- {query_title} ---")
    try:
        with pg_dw.connect() as conn:
            result = conn.execute(text(sql_code))
            rows = result.fetchall()
            
            if rows:
                header = result.keys()
                # تنسيق العرض كجدول بسيط
                print(f"{' | '.join(header)}")
                print("-" * 60)
                for row in rows:
                    print(' | '.join(str(val) for val in row))
            else:
                print("No records found.")
    except Exception as e:
        print(f"❌ Error executing analysis: {e}")

def main():
    while True:
        show_menu()
        choice = input("Enter your choice (0-5): ")

        if choice == '1':
            run_full_etl()
        elif choice == '2':
            # استعلام المبيعات عبر الزمن مع الترتيب الصحيح
            sql = """
                SELECT year, month_name, SUM(actual_amount_paid) as total_revenue 
                FROM reporting_sales_master 
                GROUP BY year, month_name 
                ORDER BY year DESC;
            """
            run_query("Sales Trending Over Time", sql)
        elif choice == '3':
            # استعلام أكثر العملاء قيمة
            sql = """
                SELECT customer_unique_id, SUM(actual_amount_paid) as total_spent 
                FROM reporting_sales_master 
                GROUP BY customer_unique_id 
                ORDER BY total_spent DESC 
                LIMIT 10;
            """
            run_query("Most Valuable Customers", sql)
        elif choice == '4':
            # استعلام متوسط قيمة الطلب لكل ولاية (كمؤشر أداء)
            sql = """
                SELECT customer_state, ROUND(AVG(actual_amount_paid), 2) as avg_order_value 
                FROM reporting_sales_master 
                GROUP BY customer_state 
                ORDER BY avg_order_value DESC;
            """
            run_query("Regional Performance Insights", sql)
        elif choice == '5':
            # استعلام الإيرادات حسب الفئة
            sql = """
                SELECT product_category_name, SUM(actual_amount_paid) as revenue 
                FROM reporting_sales_master 
                WHERE product_category_name IS NOT NULL
                GROUP BY product_category_name 
                ORDER BY revenue DESC 
                LIMIT 10;
            """
            run_query("Top Revenue Driving Categories", sql)
        elif choice == '0':
            print("Exiting... Goodbye Aimen!")
            sys.exit()
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
