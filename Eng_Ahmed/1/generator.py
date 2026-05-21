#!/usr/bin/env python3
import os
import time
import random
import json
from faker import Faker
import psycopg2
from datetime import datetime, timedelta


# Initialize Faker
fake = Faker()

# --- WSL Host Volume Mount Alignment ---
# Matches your docker-compose setting: ./assignment1 -> /assignment1/nifi_input_data
OUTPUT_DIR = "./assignment1/nifi_input_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"Current working directory: {os.getcwd()}")
# --- Database Configuration ---
try:
    conn = psycopg2.connect(
        host="localhost",       # Running natively from WSL Terminal to exposed container port
        port=6432,              # Port mapped in your docker-compose
        database="nifi1",
        user="postgres",
        password="aimen"
    )
    cursor = conn.cursor()
    
    # Pre-create the table to avoid pipeline bootstrap crashes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulated_data (
            id INT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255),
            address TEXT,
            date VARCHAR(50)
        );
    """)
    conn.commit()
    print("✅ Successfully connected to PostgreSQL and validated table schema.")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit()

# Define your date range here
DATE_START = datetime(2020, 1, 1)  # Start date
DATE_END = datetime(2024, 12, 31)  # End date
DATE_RANGE_DAYS = (DATE_END - DATE_START).days

def generate_random_date_in_range():
    """Generate random date between DATE_START and DATE_END"""
    random_days = random.randint(0, DATE_RANGE_DAYS)
    random_date = DATE_START + timedelta(days=random_days)
    return random_date

def generate_record(record_id):
    """Generates a single record with intentional flaws."""
    record = {
        "id": record_id,
        "name": fake.name(),
        "email": fake.email(),
        "address": fake.address().replace("\n", ", "), # Flatten address strings
        "date": None
    }

    # Flaw 1: Missing values (20% chance)
    if random.random() < 0.2:
        record["email"] = None

    # Flaw 2: Inconsistent date formats with date range
    random_date = generate_random_date_in_range()
    if random.random() < 0.5:
        record["date"] = random_date.strftime("%Y-%m-%d")  # YYYY-MM-DD
    return record

print("🚀 Starting Data Simulation (Files + Database)...")
print(f"📅 Date range: {DATE_START.strftime('%Y-%m-%d')} to {DATE_END.strftime('%Y-%m-%d')}")

global_record_id = 1

try:
    while True:
        # 1. Generate a batch of 10 records
        current_batch = [generate_record(global_record_id + i) for i in range(10)]

        # 2. Flaw 3: Intentional Duplicates (30% chance)
        if random.random() < 0.3:
            current_batch.append(current_batch[0])

        # --- PART A: Write to JSON File (For ListFile -> FetchFile) ---
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"file_{timestamp}_{global_record_id}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(current_batch, f, ensure_ascii=False, indent=2)
        
        print(f"📄 File created: {filename}")

        # --- PART B: Insert into PostgreSQL with Conflict Handling ---
        inserted_count = 0
        for r in current_batch:
            try:
                # 'ON CONFLICT DO NOTHING' prevents duplicate records from crashing the loop execution
                cursor.execute("""
                    INSERT INTO simulated_data (id, name, email, address, date) 
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (r["id"], r["name"], r["email"], r["address"], r["date"]))
                inserted_count += 1
            except Exception as e:
                print(f"⚠️ Error processing database record {r['id']}: {e}")
                conn.rollback()
                continue
        
        conn.commit()
        print(f"🗄️ Batch completed. Database sync finalized.")

        # Increment global ID based on the uniquely generated instances (10 per loop cycle)
        global_record_id += 10
        print("-" * 40)
        time.sleep(1) 

except KeyboardInterrupt:
    print("\n🛑 Simulation stopped by user.")
finally:
    cursor.close()
    conn.close()