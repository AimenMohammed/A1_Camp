from fastapi import FastAPI
import csv
from pathlib import Path
import uvicorn
from app.models import Book
from typing import List

app = FastAPI()

DATA_FILE = Path.cwd() / "data" / "books.csv"


def load_data():
    if not DATA_FILE.exists():
        return []

    data = []

    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            row["price"] = float(row["price"])
            row["rating"] = int(row["rating"])
            data.append(row)

    return data


@app.get("/")
def home():
    return {"message": "Books API is running"}


@app.get("/books", response_model=list[Book])
def get_books():
    return load_data()


@app.get("/books/search", response_model=list[Book])
def search_books(name: str):
    data = load_data()
    return [b for b in data if name.lower() in b.get("title", "").lower()]


@app.get("/books/rating/{rate}", response_model=list[Book])
def filter_rating(rate: int):
    data = load_data()
    return [b for b in data if b.get("rating") == rate]


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)