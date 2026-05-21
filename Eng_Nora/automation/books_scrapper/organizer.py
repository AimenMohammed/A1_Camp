import pandas as pd
import os
import shutil

cleaned_books_path = "./books_scrapper/data/processed/cleaned_books.csv"

if os.path.exists(cleaned_books_path):
    df = pd.read_csv(cleaned_books_path)
else:
    print(f"File not found: {cleaned_books_path}")
    df = pd.DataFrame() 
    
summary_path = "./books_scrapper/data/processed/summary.csv"

if os.path.exists(summary_path):
    summary = pd.read_csv(summary_path)
else:
    print(f"File not found: {summary_path}")
    summary = pd.DataFrame()
    
base_target_folder = './images/'
source_folder = './books_scrapper/images/processed/'
if os.path.exists(source_folder) and len(os.listdir(source_folder)) > 0:
    print(f"Found {len(os.listdir(source_folder))} images in '{source_folder}' directory.")
    for idx, row in df.iterrows():
        image = row['image']
        rate = int(row['rating'])  # Use the value from the current row, not the whole column
        image_name = row['image_name']  # If your image column contains the filename
        src_path = os.path.join(source_folder, image_name)
        target_folder = os.path.join(base_target_folder, f'{rate}_star')
        os.makedirs(target_folder, exist_ok=True)
        dst_path = os.path.join(target_folder, image_name)
        if os.path.exists(src_path):
            shutil.move(src_path, dst_path)
            print(f"Moved {image_name} to {target_folder}")
        else:
            print(f"File not found: {src_path}")
            
elif os.path.exists(source_folder) and len(os.listdir(source_folder)) == 0:
    print(f"No images found in '{source_folder}' directory.")
    
else:
    print(f"Directory '{source_folder}' does not exist.")
