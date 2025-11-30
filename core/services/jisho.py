import requests
import time
import logging

logger = logging.getLogger(__name__)

BASE = "https://jisho.org/api/v1/search/words"

def jisho_search(keyword: str) -> dict:
    start = time.perf_counter()
    r = requests.get(BASE, params={"keyword": keyword}, timeout=10)
    r.raise_for_status()
    result = r.json()
    elapsed = (time.perf_counter() - start) * 1000
    logger.info(f"[TIMING] jisho_search('{keyword}'): {elapsed:.2f}ms")
    return result
