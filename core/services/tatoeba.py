import requests
import time
import logging

logger = logging.getLogger(__name__)

BASE = "https://tatoeba.org/en/api_v0/search"


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def _get_text(obj):
    if not isinstance(obj, dict):
        return None
    return obj.get("text") or (obj.get("sentence") or {}).get("text")


def _get_id(obj):
    if not isinstance(obj, dict):
        return None
    return obj.get("id") or (obj.get("sentence") or {}).get("id")


def _iter_english_translations(translations):
    """Yield (id, text) của mọi câu dịch tiếng Anh từ nhiều format khác nhau."""

    # dict keyed by lang
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
            # group dạng { lang, sentences: [...] }
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

            # phần tử list lồng
            if isinstance(t, list):
                for u in t:
                    if isinstance(u, dict):
                        lang = u.get("lang") or u.get("language")
                        if lang and str(lang).startswith("en"):
                            txt = _get_text(u)
                            if txt:
                                yield (_get_id(u), txt)


# ---------------------------------------------------------
# Main search function (strict → fallback)
# ---------------------------------------------------------

def search_examples(query: str, limit: int = 3) -> list[dict]:
    """
    1) Strict mode: query JP→EN (ưu tiên câu có dịch tiếng Anh)
    2) Nếu strict = 0 → fallback mode: JP-only search
    """

    def fetch(params):
        try:
            r = requests.get(BASE, params=params, timeout=10)
            r.raise_for_status()
            return r.json().get("results", [])
        except Exception:
            return []

    # -----------------------------------------------------
    # STEP 1 — STRICT MODE (JP→ENG)
    # -----------------------------------------------------
    strict_params = {
        "query": query,
        "from": "jpn",
        "to": "eng",
        "orphans": "no",
        "unapproved": "no",
        "trans_filter": "limit",
        "trans_to": "eng",
        "sort": "relevance",
        "page": 1,
        "limit": limit * 3,
    }

    strict_results = fetch(strict_params)

    if strict_results:
        logger.info(f"[TATOEBA] STRICT mode used for '{query}'")
        parsed = _parse_results(strict_results, limit)
        if parsed:
            return parsed

    # -----------------------------------------------------
    # STEP 2 — FALLBACK MODE (JP-ONLY)
    # -----------------------------------------------------
    fallback_params = {
        "query": query,
        "sort": "relevance",
        "page": 1,
        "limit": limit * 3,
    }

    fallback_results = fetch(fallback_params)

    logger.info(f"[TATOEBA] FALLBACK mode used for '{query}'")

    return _parse_results(fallback_results, limit)


# ---------------------------------------------------------
# Parsing helper
# ---------------------------------------------------------

def _parse_results(results, limit):
    out = []

    for item in results:
        jp = _get_text(item)
        if not jp:
            continue

        # tìm EN nếu có
        en = None
        translations = item.get("translations") or {}
        for tid, en_txt in _iter_english_translations(translations):
            en = en_txt
            break

        out.append({
            "id": item.get("id"),
            "jp": jp,
            "en": en,
        })

        if len(out) >= limit:
            break

    return out
