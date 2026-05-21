from bs4 import BeautifulSoup
import os
import pandas as pd
from urllib.parse import urljoin
import requests
import re

base_url = "https://books.toscrape.com/catalogue/"

os.makedirs("./books_scrapper/data/raw", exist_ok=True)
os.makedirs("./books_scrapper/images/raw", exist_ok=True)

books = []
def get_rating(star_rating):
    return ["zero", "one", "two", "three", "four", "five"].index(star_rating.lower())

url = urljoin(base_url, "page-1.html")

page_no = 1

while url and page_no <= 3:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    articles = soup.find_all("article", class_="product_pod")
    
    for article in articles:
        title = article.h3.a["title"]
        price = article.find("p", class_="price_color").text[2:]
        rating_class = article.find("p", class_="star-rating")["class"][1]
        rating = get_rating(rating_class)
        img_url = urljoin(base_url, article.find("img")["src"])
        img_name = img_url.split("/")[-1]
        img_response = requests.get(img_url).content
        image_name = f"{title.split(':')[0][:50].strip()}.jpg"
        with open(f"./books_scrapper/images/raw/{img_name}", "wb") as img_file:
            img_file.write(img_response)
        image_path = os.rename(f"./books_scrapper/images/raw/{img_name}", f"./books_scrapper/images/raw/{image_name}")
        
        try:
            books.append({
                "title": title,
                "price": float(re.sub(r"[^0-9.]", "", price)),
                "rating": rating,
                "image": img_response,
                "image_name": image_name
            })
            print(f"Scraped: {title}")
        except Exception as e:
            print(f"Error occurred while processing article: {e}")
            continue
    print(f"Completed page {page_no}")
    next_button = soup.find("li", class_="next")
    url = urljoin(base_url, next_button.a["href"]) if next_button else None
    page_no += 1
    url = urljoin(base_url, f"page-{page_no}.html")
    
df = pd.DataFrame(books)
df.to_csv("./books_scrapper/data/raw/books.csv", index=False)
print("Scraping completed. Data saved in './books_scrapper/data/raw/books.csv' and images saved in './books_scrapper/images/raw' directory.")
        