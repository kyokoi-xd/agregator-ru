from typing import List
import httpx
from ..models import Offer
from ..scrapers import wildberries
from .dedupe import group_similar_titles
import asyncio

async def run_all_scrapers(query: str) -> List[Offer]:
    """
    Оркестратор: запускает все скрейперы параллельно и объединяет результаты.
    Сейчас — только wildberries, но легко добавить другие.
    """
    async with httpx.AsyncClient() as client:
        # keep tasks in a list so we can run many scrapers in parallel
        tasks = [asyncio.create_task(wildberries.scrape(query, client))]
        # add other scrapers here: tasks.append(asyncio.create_task(ozon.scrape(...)))
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # collect all successful results and flatten; ignore failing scrapers
    wb_res = []
    for r in results:
        if isinstance(r, Exception):
            # already logged by scraper, skip
            continue
        wb_res.extend(r)

    # now return the combined list
    # позже можно применить dedupe и ранжирование
    return wb_res


def dedupe_offers(offers: List[Offer], threshold: int = 85):
    # простая группировка похожих заголовков
    titles = [o.title for o in offers]
    clusters = group_similar_titles(titles, threshold=threshold)
    # для MVP — оставляем по одному офферу из кластера (например, с минимальной ценой если есть)
    deduped = []
    for cluster in clusters:
        cluster_offers = [offers[i] for i in cluster]
        # выбираем оффер с ненулевой ценой и минимальной ценой; если все None — берем первый
        priced = [o for o in cluster_offers if o.price is not None]
        if priced:
            winner = min(priced, key=lambda x: x.price)
        else:
            winner = cluster_offers[0]
        deduped.append(winner)
    return deduped