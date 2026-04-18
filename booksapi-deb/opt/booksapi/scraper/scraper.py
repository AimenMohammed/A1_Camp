import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
import re
from urllib.parse import urljoin
import os

os.makedirs("./images/raw", exist_ok=True)

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
BASE_SITE = "https://books.toscrape.com/catalogue/"

BASE_DIR = Path.cwd()
DATA_PATH = BASE_DIR / "data" / "books.csv"


def get_rating(star_class):
    ratings = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    return ratings.get(star_class, 0)


def scrape_page(page):
    url = BASE_URL.format(page)
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    books = []

    for book in soup.select(".product_pod"):
        title = book.h3.a["title"]

        price = book.select_one(".price_color").text
        price = re.sub(r"[^\d.]", "", price)
        price = float(price)

        rating_class = book.select_one(".star-rating")["class"][1]
        rating = get_rating(rating_class)

        img_url = urljoin(BASE_SITE, book.find("img")["src"])

        image_name = f"{title.split(':')[0][:50].strip()}.jpg"
        image_path = f"./images/{image_name}"

        if not os.path.exists(image_path):
            try:
                img_response = requests.get(img_url, timeout=10).content

                with open(image_path, "wb") as img_file:
                    img_file.write(img_response)

                print(f"Downloaded: {image_name}")

            except Exception as e:
                print(f"Error downloading image: {e}")
        else:
            print(f"Skipped (exists): {image_name}")

        link = book.h3.a["href"]
        full_link = BASE_SITE + link

        books.append({
            "title": title,
            "price": price,
            "rating": rating,
            "image_name": image_name,
            "link": full_link,
            "image_url": image_path
        })

        print(f"Scraped: {title}")

    return books


def scrape_all():
    all_books = []

    for i in range(1, 4):
        try:
            print(f"Scraping page {i}")
            all_books.extend(scrape_page(i))
        except Exception as e:
            print(f"Error occurred while scraping page {i}: {e}")

    return all_books


def save_data(data):
    DATA_PATH.parent.mkdir(exist_ok=True)

    with open(DATA_PATH, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "title",
            "price",
            "rating",
            "image_name",
            "link",
            "image_url"
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    data = scrape_all()
    save_data(data)
    print(f"Saved {len(data)} books!")
