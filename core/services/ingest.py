from __future__ import annotations

import time
import logging

from django.db import transaction
from django.db.models import QuerySet

from .jisho import jisho_search
from .tatoeba import search_examples
from core.models import Word, WordMeaning, ExampleSentence

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
#  HELPERS
# ---------------------------------------------------------

def _gather_pos(senses: list[dict]) -> str:
    """Gom tất cả parts_of_speech từ senses, bỏ trùng nhưng giữ thứ tự."""
    pos: list[str] = []
    for s in senses or []:
        pos.extend(s.get("parts_of_speech", []))
    # Dùng dict.fromkeys để remove duplicates và giữ thứ tự
    return ", ".join(dict.fromkeys(pos))


def _get_or_create_word(
    kanji: str | None,
    kana: str | None,
    parts: str,
    jlpt_level: str | None,
) -> Word:
    """
    Tìm Word bằng (kanji + kana).
    Nếu chưa có thì tạo mới.
    """
    w = (
        Word.objects.filter(kanji=kanji, kana=kana)
        .order_by("id")
        .first()
    )

    if w is None:
        return Word.objects.create(
            kanji=kanji,
            kana=kana,
            parts_of_speech=parts or "",
            jlpt_level=jlpt_level,
            is_cached=True,
        )

    # Nếu tồn tại, update nhẹ nhàng cho đủ dữ liệu
    changed = False
    if parts and not w.parts_of_speech:
        w.parts_of_speech = parts
        changed = True
    if jlpt_level and not w.jlpt_level:
        w.jlpt_level = jlpt_level
        changed = True
    if not w.is_cached:
        w.is_cached = True
        changed = True

    if changed:
        w.save(update_fields=["parts_of_speech", "jlpt_level", "is_cached"])

    return w


def _upsert_meanings(word: Word, senses: list[dict]) -> list[WordMeaning]:
    """Tạo/cập nhật meanings theo english_definitions."""
    created_or_existing: list[WordMeaning] = []

    for s in senses or []:
        meaning_text = "; ".join(s.get("english_definitions", []))
        if not meaning_text:
            continue

        wm, _ = WordMeaning.objects.get_or_create(
            word=word,
            meaning=meaning_text,
        )
        created_or_existing.append(wm)

    return created_or_existing


# ---------------------------------------------------------
#  FILL EXAMPLES — dùng trong word detail page
# ---------------------------------------------------------

def _fill_examples_for_word(word: Word, per_meaning: int = 3) -> None:
    """
    Chỉ dùng khi user xem detail của 1 từ.
    Search sẽ dùng ingest nhưng KHÔNG gọi Tatoeba.
    """
    t0 = time.perf_counter()
    meanings: QuerySet[WordMeaning] = (
        WordMeaning.objects.filter(word=word)
        .order_by("id")
        .prefetch_related("examples")
    )

    # Xác định meanings cần fetch example
    need_total = 0
    need_per_meaning: list[tuple[WordMeaning, int]] = []

    for m in meanings:
        lacking = max(0, per_meaning - m.examples.count())
        if lacking > 0:
            need_per_meaning.append((m, lacking))
            need_total += lacking

    logger.info(
        f"[TIMING] _fill_examples - check needs: {(time.perf_counter() - t0)*1000:.2f}ms, need_total={need_total}"
    )

    # Nếu đủ example rồi → không gọi API
    if need_total == 0:
        return

    # Query Tatoeba với từ kanji hoặc kana
    key = word.kanji or word.kana
    if not key:
        return

    # Call API Tatoeba
    t1 = time.perf_counter()
    try:
        pool = search_examples(key, limit=need_total * 2)
    except Exception:
        pool = []

    logger.info(
        f"[TIMING] _fill_examples - tatoeba API call: {(time.perf_counter() - t1)*1000:.2f}ms, got {len(pool)} examples"
    )

    # Gán example cho meanings
    for m, lacking in need_per_meaning:
        while lacking > 0 and pool:
            ex = pool.pop(0)

            src_id = ex.get("id")
            if not src_id:
                continue

            ExampleSentence.objects.get_or_create(
                meaning=m,
                source="tatoeba",
                source_id=str(src_id),
                defaults={
                    "jp": ex.get("jp", ""),
                    "en": ex.get("en"),
                },
            )

            lacking -= 1


# ---------------------------------------------------------
#  MAIN INGEST (JISHO ONLY) — dùng trong /api/search
# ---------------------------------------------------------

def upsert_from_jisho(keyword: str) -> list[Word]:
    """
    Gọi Jisho, upsert Word + Meaning.
    KHÔNG gọi Tatoeba tại đây để tránh chậm search.
    """
    total_start = time.perf_counter()

    # 1) Fetch Jisho API
    t0 = time.perf_counter()
    payload = jisho_search(keyword)
    logger.info(
        f"[TIMING] upsert_from_jisho - jisho_search: {(time.perf_counter() - t0)*1000:.2f}ms"
    )

    words: list[Word] = []

    # 2) Insert/update DB
    t1 = time.perf_counter()
    with transaction.atomic():
        for item in payload.get("data", []):
            japanese = (item.get("japanese") or [{}])[0]
            senses = item.get("senses") or []

            kanji = japanese.get("word")
            kana = japanese.get("reading")
            parts = _gather_pos(senses)

            # Parse JLPT
            jlpt_level = None
            for tag in item.get("jlpt", []) or []:
                if tag.startswith("jlpt-"):
                    jlpt_level = tag.split("-")[-1].upper()
                    break

            w = _get_or_create_word(kanji, kana, parts, jlpt_level)
            _upsert_meanings(w, senses)
            words.append(w)

    logger.info(
        f"[TIMING] upsert_from_jisho - DB upsert ({len(words)} words): {(time.perf_counter() - t1)*1000:.2f}ms"
    )

    # ❗❗❗ Không gọi Tatoeba tại đây (để search nhanh)
    logger.info(
        f"[TIMING] upsert_from_jisho TOTAL: {(time.perf_counter() - total_start)*1000:.2f}ms"
    )

    return words
