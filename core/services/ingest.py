from __future__ import annotations

from django.db import transaction, IntegrityError
from django.db.models import QuerySet

from .jisho import jisho_search
from .tatoeba import search_examples
from core.models import Word, WordMeaning, ExampleSentence


def _gather_pos(senses: list[dict]) -> str:
    """Gom tất cả parts_of_speech từ các sense, bỏ trùng nhưng giữ thứ tự."""
    pos: list[str] = []
    for s in senses or []:
        pos.extend(s.get("parts_of_speech", []))
    return ", ".join(dict.fromkeys(pos))


def _get_or_create_word(
    kanji: str | None,
    kana: str | None,
    parts: str,
    jlpt_level: str | None,
) -> Word:
    """
    Lấy Word đầu tiên theo (kanji, kana); nếu chưa có thì tạo mới.
    Tránh MultipleObjectsReturned nếu lỡ có trùng trong DB.
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

    # Cập nhật nhẹ nếu trước đó trống
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
    """
    Tạo các WordMeaning nếu chưa tồn tại (so khớp theo 'meaning' text).
    """
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


def _fill_examples_for_word(word: Word, per_meaning: int = 2) -> None:
    """
    Với mỗi meaning của 'word', nếu còn thiếu ví dụ thì nạp tối đa 'per_meaning' câu
    từ Tatoeba và lưu vào ExampleSentence (tránh trùng theo meaning+source+source_id).
    """
    meanings: QuerySet[WordMeaning] = (
        WordMeaning.objects.filter(word=word)
        .order_by("id")
        .prefetch_related("examples")
    )

    need_total = 0
    need_per_meaning: list[tuple[WordMeaning, int]] = []
    for m in meanings:
        lacking = max(0, per_meaning - m.examples.count())
        if lacking > 0:
            need_per_meaning.append((m, lacking))
            need_total += lacking

    if need_total == 0:
        return

    key = word.kanji or word.kana
    if not key:
        return

    try:
        pool = search_examples(key, limit=need_total * 2)
    except Exception:
        pool = []

    for m, lacking in need_per_meaning:
        while lacking > 0 and pool:
            ex = pool.pop(0)

            # Nếu Tatoeba không trả id thì bỏ qua để tránh source_id rỗng bị trùng
            src_id = ex.get("id")
            if not src_id:
                continue

            try:
                # 🔥 Dùng cặp meaning+source+source_id làm key, khớp với UniqueConstraint
                ExampleSentence.objects.get_or_create(
                    meaning=m,
                    source="tatoeba",
                    source_id=str(src_id),
                    defaults={
                        "jp": ex.get("jp", ""),
                        "en": ex.get("en"),
                    },
                )
            except IntegrityError:
                # Nếu vẫn lỡ trùng thì bỏ qua, không cho 500 nữa
                pass

            lacking -= 1


def upsert_from_jisho(keyword: str) -> list[Word]:
    """
    Gọi Jisho, upsert Word + WordMeaning, rồi bơm ví dụ vào ExampleSentence.
    Trả về danh sách Word liên quan tới keyword.
    """
    payload = jisho_search(keyword)
    words: list[Word] = []

    # Tạo/cập nhật word + meanings trong 1 transaction
    with transaction.atomic():
        for item in payload.get("data", []):
            japanese = (item.get("japanese") or [{}])[0]
            senses = item.get("senses") or []

            kanji = japanese.get("word")
            kana = japanese.get("reading")
            parts = _gather_pos(senses)

            # jlpt: ["jlpt-n5", ...] -> "N5"
            jlpt_level = None
            for tag in item.get("jlpt", []) or []:
                if tag.startswith("jlpt-"):
                    jlpt_level = tag.split("-")[-1].upper()
                    break

            w = _get_or_create_word(kanji, kana, parts, jlpt_level)
            _upsert_meanings(w, senses)
            words.append(w)

    # Bơm ví dụ Tatoeba (không đặt trong transaction để đỡ khóa DB lâu)
    for w in words:
        _fill_examples_for_word(w, per_meaning=2)

    return words
