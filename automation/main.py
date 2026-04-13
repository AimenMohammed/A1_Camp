import os
from books_scrapper import scrapper, organizer, processor
print("step 1: scrapping...")
os.system("python3 scrapper.py")

print("step 2: organizing images...")
os.system("python3 organizer.py")

print("step 3: processing data...")
os.system("python3 processor.py")

print("all steps completed successfully!")