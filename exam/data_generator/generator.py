import random
import schedule
import time
from datetime import datetime
import os
print(f"file{os.getcwd()}/data_generator/generator.py")  # Debugging line to check the current working directory
DATA_FOLDER = "./data/incoming"
os.makedirs(DATA_FOLDER, exist_ok=True)

def generate_record():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    device = f"device_{random.randint(1, 5)}"
    metric = "temperature"
    value = round(random.uniform(20, 35), 2)
    
    return f"{timestamp},{device},{metric},{value}"

def create_file():
    record = generate_record()
    
    filename = datetime.now().strftime("data_%Y-%m-%d_%H-%M-%S.txt")
    filepath = os.path.join(DATA_FOLDER, filename)
    
    with open(filepath, "w") as f:
        f.write(record)
        
    print(f"Generated file: {filepath} with record: {record}")
        
schedule.every(1).seconds.do(create_file)

while True:
    schedule.run_pending()
    time.sleep(0.5)