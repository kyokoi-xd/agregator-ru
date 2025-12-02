from fastapi import FastAPI, Query
from typing import Dict, Any
from .config import CACHE_TTL
from .cache import InMemoryCache
from .services.coordinator import run_all_scrapers, dedupe_offers
from .models import SearchResponse, Offer


app = FastAPI(title="Price Aggregator (modular)")

cache = InMemoryCache()

@app.get("/search", response_model=Dict[str, Any])
async def search(q: str = Query(..., min_length=1), sort: str = Query("none")):
    q_norm = q.strip()
    cache_key = f"search:{q_norm}:{sort}"
    cached = cache.get(cache_key)
    if cached:
        return {"query": q_norm,"source": "cache", "results": cached}
    
    offers = await run_all_scrapers(q_norm)
    offers = dedupe_offers(offers, threshold=85)


    if sort in ("price_asc", "price_desc"):
        offers = [o for o in offers if o.price is not None]
        offers.sort(key=lambda x: x.price, reverse=(sort == "price_desc"))
    

    out = [o.dict() for o in offers]
    cache.set(cache_key, out, ttl=CACHE_TTL)
    return {"query": q_norm, "source": "live", "results": out}