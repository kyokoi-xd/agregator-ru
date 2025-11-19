import re

def extract_price(text: str) -> float | None:
    """
    Extracts the first occurrence of a price from the given text."""

    if not text:
        return None

    m = re.search(r"([\d\s]+[.,]?\d*)", text)
    if not m:
        return None
    raw = m.group(1).replace(" ", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None
    
def normalize_str(s: str) -> str:
    return (s or "").strip().lower()