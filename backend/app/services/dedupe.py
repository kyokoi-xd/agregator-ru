from typing import List
from rapidfuzz import process, fuzz

def group_similar_titles(titles: List[str], threshold: int = 80):
    """
    Простейшая идея: для списка заголовков возвращаем кластеры (index lists)
    Здесь можно использовать более продвинутую логику; это минимальный набросок.
    """

    clusters = []
    used = set()
    for i, t in enumerate(titles):
        if i in used:
            continue
        group = [i]
        used.add(i)
        # Ищем похожие заголовки
        matches = process.extract(t, titles, scorer=fuzz.token_sort_ratio, limit=None)
        for m_title, score, j in matches:
            if j == i or j in used:
                continue
            if score >= threshold:
                group.append(j)
                used.add(j)
        clusters.append(group)
    return clusters