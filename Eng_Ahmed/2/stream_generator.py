import csv
import os
import random
import time
from datetime import datetime, timedelta

OUTPUT_DIR = "assignment2/stream_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

transaction_types = ["deposit", "withdraw", "transfer", "payment"]
locations = ["Sanaa", "Aden", "Taiz", "Ibb"]

counter = 1000
# Keep track of recently used IDs for cross-file duplicates
recent_ids = []

def random_timestamp():
    now = datetime.now()
    choice = random.randint(1, 6)
    if choice == 1:
        return now.strftime("%Y-%m-%d %H:%M:%S")
    elif choice == 2:
        return now.strftime("%d/%m/%Y %H:%M")
    elif choice == 3:
        return now.isoformat()
    elif choice == 4:
        return str(int(now.timestamp()))
    elif choice == 5:
        # Future timestamp (invalid)
        return (now + timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d %H:%M:%S")
    else:
        # Completely invalid format
        return "invalid-timestamp-999"

while True:
    filename = f"transactions_{int(time.time())}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "transaction_id",
            "customer_id",
            "amount",
            "transaction_type",
            "transaction_time",
            "location"
        ])

        for i in range(200):
            counter += 1
            transaction_id = counter

            # Duplicate from previous files (10% chance)
            if recent_ids and random.random() < 0.1:
                transaction_id = random.choice(recent_ids)
            else:
                recent_ids.append(transaction_id)
                # Keep list size manageable
                if len(recent_ids) > 100:
                    recent_ids.pop(0)

            customer_id = f"CUST{random.randint(1, 50)}"
            
            # Start with a valid amount
            amount = round(random.uniform(10, 10000), 2)
            transaction_type = random.choice(transaction_types)
            location = random.choice(locations)
            transaction_time = random_timestamp()

            # --- Apply corruption to amount (only ONE type per record) ---
            corruption_choice = random.random()
            
            # Missing value (empty string)
            if corruption_choice < 0.07:
                amount = ""
            # Dollar sign prefix
            elif corruption_choice < 0.12:
                amount = f"${amount}"
            # Negative amount
            elif corruption_choice < 0.16:
                amount = -abs(amount)
            # Comma as decimal separator
            elif corruption_choice < 0.19:
                amount = f"{amount:.2f}".replace(".", ",")
            # Invalid string (not numeric)
            elif corruption_choice < 0.22:
                amount = "INVALID_AMOUNT"
            # Keep as valid float for remaining ~78% of records
            
            # --- Missing values for other fields ---
            if random.random() < 0.05:
                customer_id = ""
            if random.random() < 0.03:
                location = None

            # --- Invalid transaction_type (wrong data type) ---
            if random.random() < 0.05:
                transaction_type = 123  # integer instead of string

            row = [
                transaction_id,
                customer_id,
                amount,
                transaction_type,
                transaction_time,
                location
            ]

            # Corrupted rows (completely malformed CSV)
            if random.random() < 0.03:
                # 50% chance: too few fields, 50% chance: garbage line
                if random.random() < 0.5:
                    row = ["only", "one", "field"]
                else:
                    row = ["COMPLETELY CORRUPTED LINE WITH NO STRUCTURE"]

            writer.writerow(row)

            # Duplicate within same file (reuse the same row)
            if random.random() < 0.05:
                writer.writerow(row)

    print(f"Generated: {filepath}")
    time.sleep(5)