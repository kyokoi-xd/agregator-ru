from typing import List
import logging
from ..models import Offer
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import httpx
from ..utils import extract_price
from ..config import USER_AGENT, MAX_SCRAPE_RESULTS

WB_CARD_SELECTORS = [
    ".product-card",
    ".product-card-wrapper",
    ".product-card_inner",
    "figure"
]

async def scrape(query:str, client:httpx.AsyncClient) -> List[Offer]:
    q = quote_plus(query)
    url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={q}"
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = await client.get(url, headers=headers, timeout=15.0)
        resp.raise_for_status()
    except Exception as exc:  # httpx.RequestError, httpx.HTTPStatusError, etc.
        logging.debug("Wildberries scraper request failed: %s %s", url, exc)
        # Return an empty list when a remote scraper fails so the whole request doesn't 500
        return []

    try:
        soup = BeautifulSoup(resp.text, "lxml")
    except Exception as exc:  # parsing errors should not crash the app
        logging.debug("Wildberries parsing failed: %s", exc)
        return []

    cards = []
    for sel in WB_CARD_SELECTORS:
        found = soup.select(sel)
        if found:
            cards = found
            break
    
    results: List[Offer] = []
    for c in cards[:MAX_SCRAPE_RESULTS]:
        title_el = c.select_one(".product-card__name") or c.select_one(".name") or c.select_one("a")
        price_el = c.select_one(".product-card__price") or c.select_one(".price")
        link_el = c.select_one("a")
        img_el = c.select_one("img")

        title = title_el.get_text(strip=True) if title_el else ""
        price = extract_price(price_el.get_text(" ", strip=True)) if price_el else None
        href = link_el.get("href") if link_el else None
        url_final = f"https://www.wildberries.ru{href}" if href and href.startswith("/") else href or ""
        img = img_el.get("src") if img_el else None

        if not title and not url_final:
            continue
        results.append(Offer(source="wildberries", title=title or url_final, price=price, url=url_final, image=img))
    return results