from sqlalchemy import text
from config.db_config import pg_raw

def initialize_raw_tables():
    """
    Creates the raw_data schema and empty tables to act as a landing zone.
    Using TEXT for all columns ensures a 'no-fail' load from the source.
    """
    
    # List of SQL commands to build the landing zone
    commands = [
        "CREATE SCHEMA IF NOT EXISTS raw_data;",
        
        # Products Table
        """
        CREATE TABLE IF NOT EXISTS raw_data.products (
            product_id TEXT, product_category_name TEXT, product_name_lenght TEXT,
            product_description_lenght TEXT, product_photos_qty TEXT, product_weight_g TEXT,
            product_length_cm TEXT, product_height_cm TEXT, product_width_cm TEXT
        );
        """,
        
        # Customers Table
        """
        CREATE TABLE IF NOT EXISTS raw_data.customers (
            customer_id TEXT, customer_unique_id TEXT, 
            customer_zip_code_prefix TEXT, customer_city TEXT, customer_state TEXT
        );
        """,
        
        # Sellers Table
        """
        CREATE TABLE IF NOT EXISTS raw_data.sellers (
            seller_id TEXT, seller_zip_code_prefix TEXT, 
            seller_city TEXT, seller_state TEXT
        );
        """,
        
        # Orders Table
        """
        CREATE TABLE IF NOT EXISTS raw_data.orders (
            order_id TEXT, customer_id TEXT, order_status TEXT,
            order_purchase_timestamp TEXT, order_approved_at TEXT,
            order_delivered_carrier_date TEXT, order_delivered_customer_date TEXT,
            order_estimated_delivery_date TEXT
        );
        """,
        
        # Order Items Table
        """
        CREATE TABLE IF NOT EXISTS raw_data.order_items (
            order_id TEXT, order_item_id TEXT, product_id TEXT, seller_id TEXT,
            shipping_limit_date TEXT, price TEXT, freight_value TEXT
        );
        """,
        
        # Order Payments Table
        """
        CREATE TABLE IF NOT EXISTS raw_data.order_payments (
            order_id TEXT, payment_sequential TEXT, payment_type TEXT,
            payment_installments TEXT, payment_value TEXT
        );
        """,
        
        # Order Reviews Table
        """
        CREATE TABLE IF NOT EXISTS raw_data.order_reviews (
            review_id TEXT, order_id TEXT, review_score TEXT,
            review_comment_title TEXT, review_comment_message TEXT,
            review_creation_date TEXT, review_answer_timestamp TEXT
        );
        """
    ]

    print("Initializing Raw Landing Zone (PostgreSQL)...")
    try:
        with pg_raw.begin() as conn:
            for cmd in commands:
                conn.execute(text(cmd))
        print("Raw tables created or already exist.")
    except Exception as e:
        print(f"Failed to initialize Raw DB: {e}")

if __name__ == "__main__":
    initialize_raw_tables()
