import pandas as pd
import os

os.makedirs("./books_scrapper/data/processed", exist_ok=True)
os.makedirs("./books_scrapper/images/processed", exist_ok=True)


if os.path.exists("./books_scrapper/data/raw/books.csv"):
    df = pd.read_csv("./books_scrapper/data/raw/books.csv")
    df = df.drop_duplicates()
    df["price"] = df["price"].fillna(df["price"].mean())

    summary = df.groupby("rating")["price"].agg(["count", "mean"])

    df.to_csv("./books_scrapper/data/processed/cleaned_books.csv", index=False)
    summary.to_csv("./books_scrapper/data/processed/summary.csv")

    print("Data processing completed. Cleaned data and summary saved in './books_scrapper/data/processed/' directory.")
else:
    print("Raw data file not found.")
    df = pd.DataFrame()




image_path = "./books_scrapper/images/raw/"
new_image_path = "./books_scrapper/images/processed/"

if os.path.exists(image_path) and len(os.listdir(image_path)) > 0:
    images = os.listdir(image_path)
    print(f"Found {len(images)} images in '{image_path}' directory.")
    for image in images:
        old_path = os.path.join(image_path, image)
        new_path = os.path.join(new_image_path, image)
        os.rename(old_path, new_path)
        
    print(f"Images moved to {new_image_path} directory.")
elif os.path.exists(image_path) and len(os.listdir(image_path)) == 0:
    print(f"No images found in '{image_path}' directory.")
    
else:
    print(f"Directory '{image_path}' does not exist.")