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
    pos: list[str] = []
    for s in senses or []:
        pos.extend(s.get("parts_of_speech", []))
    return ", ".join(dict.fromkeys(pos))


def _get_or_create_word(kanji, kana, parts, jlpt_level):
    w = Word.objects.filter(kanji=kanji, kana=kana).order_by("id").first()
    if w is None:
        return Word.objects.create(
            kanji=kanji,
            kana=kana,
            parts_of_speech=parts or "",
            jlpt_level=jlpt_level,
            is_cached=True,
        )

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


def _upsert_meanings(word: Word, senses: list[dict]):
    created_or_existing = []
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
#  FILL EXAMPLES — VERSION B + JP PRIORITY
# ---------------------------------------------------------

def _fill_examples_for_word(word: Word, per_meaning: int = 3) -> None:
    """
    Logic mới:
    1) Ưu tiên example JP theo kanji/kana
    2) Nếu không có → fallback theo English meaning
    3) Mỗi meaning gọi riêng (Option B)
    """

    t_start = time.perf_counter()

    meanings: QuerySet[WordMeaning] = (
        WordMeaning.objects.filter(word=word)
        .order_by("id")
        .prefetch_related("examples")
    )

    kanji = word.kanji
    kana = word.kana

    # Nếu từ không có gì để search
    if not kanji and not kana:
        return

    for meaning in meanings:
        lacking = per_meaning - meaning.examples.count()
        if lacking <= 0:
            continue

        final_examples = []

        # ================================
        # 1) TRY JP: kanji + kana
        # ================================
        raw_jp = []

        try:
            if kanji:
                raw_jp += search_examples(kanji, limit=8)
            if kana and kana != kanji:
                raw_jp += search_examples(kana, limit=8)
        except Exception:
            pass

        # Lọc đúng sentence chứa từ
        filtered_jp = [
            ex for ex in raw_jp
            if ((kanji and kanji in ex["jp"]) or (kana and kana in ex["jp"]))
        ]

        if filtered_jp:
            final_examples = filtered_jp

        # ================================
        # 2) FALLBACK: search theo meaning EN
        # ================================
        if not final_examples:
            meaning_keywords = [m.strip() for m in meaning.meaning.split(";")]

            raw_en = []

            for kw in meaning_keywords:
                if not kw:
                    continue
                try:
                    raw_en += search_examples(kw, limit=5)
                except Exception:
                    pass

            # Không filter theo JP vì fallback theo EN meaning
            final_examples = raw_en

        # Không tìm thấy gì
        if not final_examples:
            continue

        # ================================
        # 3) Insert vào DB
        # ================================
        for ex in final_examples[:lacking]:
            ExampleSentence.objects.get_or_create(
                meaning=meaning,
                source="tatoeba",
                source_id=str(ex["id"]),
                defaults={
                    "jp": ex["jp"],
                    "en": ex["en"],
                },
            )

    logger.info(
        f"[TIMING] _fill_examples_for_word DONE: {(time.perf_counter() - t_start)*1000:.2f}ms"
    )


# ---------------------------------------------------------
#  MAIN INGEST (SEARCH ONLY)
# ---------------------------------------------------------

def upsert_from_jisho(keyword: str) -> list[Word]:
    total_start = time.perf_counter()

    payload = jisho_search(keyword)

    words: list[Word] = []

    with transaction.atomic():
        for item in payload.get("data", []):
            japanese = (item.get("japanese") or [{}])[0]
            senses = item.get("senses") or []

            kanji = japanese.get("word")
            kana = japanese.get("reading")
            parts = _gather_pos(senses)

            jlpt_level = None
            for tag in item.get("jlpt", []) or []:
                if tag.startswith("jlpt-"):
                    jlpt_level = tag.split("-")[-1].upper()
                    break

            w = _get_or_create_word(kanji, kana, parts, jlpt_level)
            _upsert_meanings(w, senses)
            words.append(w)

    return words
