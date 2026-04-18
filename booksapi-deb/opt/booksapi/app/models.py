from pydantic import BaseModel

class Book(BaseModel):
    title: str
    price: float
    rating: int
    image_name: str
    link: str
    image_url: str