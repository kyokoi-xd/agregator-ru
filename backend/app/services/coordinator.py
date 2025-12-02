from typing import List
import httpx
from app.models import Offer
from app.scrappers import wildberries
from app.services.dedupe import group_similar_titles
import asyncio

async def run_all_scrappers(query: str) -> List[Offer]:
    """
    Оркестратор: запускает все скрейперы параллельно и объединяет результаты.
    Сейчас — только wildberries, но легко добавить другие.
    """
    async with httpx.AsyncClient() as client:
        # если будет больше парсеров — используем gather
        wb_task = asyncio.create_task(wildberries.scrape(query, client))
        # добавляй тут другие: ozon.scrape(...), etc.
        wb_res = await wb_task

    # сейчас просто возвращаем объединённый список
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