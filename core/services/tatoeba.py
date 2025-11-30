import requests
import time
import logging

logger = logging.getLogger(__name__)

BASE = "https://tatoeba.org/en/api_v0/search"

def _get_text(obj):
    if not isinstance(obj, dict):
        return None
    return obj.get("text") or (obj.get("sentence") or {}).get("text")

def _get_id(obj):
    if not isinstance(obj, dict):
        return None
    return obj.get("id") or (obj.get("sentence") or {}).get("id")

def _iter_english_translations(translations):
    """
    Yield (id, text) cho mọi câu dịch tiếng Anh, chịu được nhiều cấu trúc:
    - list of dicts: [{'lang':'eng','text':...}, ...]
    - list of groups: [{'lang':'eng','sentences':[{'text':...}, ...]}, ...]
    - dict keyed theo ngôn ngữ: {'eng': [ {...}, ... ], ...}
    - list of lists: [[{...}, ...], [...]]
    """
    # dict keyed theo lang
    if isinstance(translations, dict):
        for key, arr in translations.items():
            if str(key).startswith("en"):
                if isinstance(arr, list):
                    for d in arr:
                        txt = _get_text(d)
                        if txt:
                            yield (_get_id(d), txt)
                elif isinstance(arr, dict):
                    txt = _get_text(arr)
                    if txt:
                        yield (_get_id(arr), txt)
        return

    # list
    if isinstance(translations, list):
        for t in translations:
            # group có 'lang' + 'sentences'
            if isinstance(t, dict) and ("sentences" in t):
                lang = t.get("lang") or t.get("language")
                if lang and str(lang).startswith("en"):
                    for s in (t.get("sentences") or []):
                        txt = _get_text(s)
                        if txt:
                            yield (_get_id(s), txt)
                continue
            # phần tử dict đơn
            if isinstance(t, dict):
                lang = t.get("lang") or t.get("language")
                if lang and str(lang).startswith("en"):
                    txt = _get_text(t)
                    if txt:
                        yield (_get_id(t), txt)
                continue
            # phần tử là list lồng
            if isinstance(t, list):
                for u in t:
                    if isinstance(u, dict):
                        lang = u.get("lang") or u.get("language")
                        if lang and str(lang).startswith("en"):
                            txt = _get_text(u)
                            if txt:
                                yield (_get_id(u), txt)

def search_examples(query: str, limit: int = 3) -> list[dict]:
    """
    Trả list [{'id':..., 'jp':..., 'en':...}] cho từ/kanji 'query'.
    """
    start = time.perf_counter()
    params = {
        "from": "jpn", "to": "eng", "query": query,
        "orphans": "no", "unapproved": "no",
        "trans_filter": "limit", "trans_to": "eng",
        "sort": "relevance", "page": 1, "limit": limit * 3  # lấy dư để lọc
    }
    r = requests.get(BASE, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    elapsed = (time.perf_counter() - start) * 1000
    logger.info(f"[TIMING] tatoeba_search('{query}'): {elapsed:.2f}ms")

    out = []
    for item in data.get("results", []):
        jp = _get_text(item)
        if not jp:
            continue

        en = None
        en_id = None
        translations = item.get("translations") or {}
        for tid, en_txt in _iter_english_translations(translations):
            en = en_txt
            en_id = tid
            break  # lấy 1 câu EN đầu tiên là đủ

        if jp and en:
            out.append({"id": en_id, "jp": jp, "en": en})
            if len(out) >= limit:
                break
    return out
