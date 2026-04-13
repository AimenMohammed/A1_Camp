import pandas as pd
import os
import schedule
import time
from db import get_connection

DATA_FOLDER = "./data/incoming"
PROCESSED_FOLDER = "./data/processed"

os.makedirs(PROCESSED_FOLDER, exist_ok=True)

device_counters = {}

def run_pipeline():
    global device_counters
    
    files = os.listdir(DATA_FOLDER)
    if not files:
        return
    
    records = []
    
    for file in files:
        path = os.path.join(DATA_FOLDER, file)
        with open(path) as f:
            line = f.readline().strip()
            records.append(line.split(","))
            
        os.rename(path, os.path.join(PROCESSED_FOLDER, file))
        
    df = pd.DataFrame(records, columns=["timestamp", "device",  "metric", "value"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["value"] = df["value"].astype(float)
    conn = get_connection()
    cur = conn.cursor()
    
    for _, row in df.iterrows():
        cur.execute("""
                    INSERT INTO raw_data(timestamp, device, metric, value) 
                    VALUES (%s, %s, %s, %s)
                    """,
                    (row.timestamp, row.device, row.metric, row.value))
        device_counters[row.device] = device_counters.get(row.device, 0) + 1
    conn.commit()
    print(f"Processed {len(df)} records. Device counts: {device_counters}")
    
schedule.every(10).seconds.do(run_pipeline)
while True:
    schedule.run_pending()
    time.sleep(1)
                       