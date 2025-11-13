from pydantic import BaseModel, HttpUrl
from typing import Optional


class Offer(BaseModel):
    source: str
    title: str
    price: Optional[float] = None
    url: HttpUrl
    image: Optional[HttpUrl] = None


class SearchResponse(BaseModel):
    query: str
    source: str
    results: list[Offer]
    