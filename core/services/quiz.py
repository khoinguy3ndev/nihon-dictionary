import os
import json
import time
import random
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBUBHSuNO8j1lqrXoqJcEgGj2Qfa3_kZq8")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("[WARN] GEMINI_API_KEY not set!")


LEVEL_INFO = {
    "N5": "basic Japanese",
    "N4": "everyday Japanese",
    "N3": "intermediate Japanese",
    "N2": "advanced everyday Japanese",
    "N1": "very advanced formal Japanese"
}


def retry_call(fn, retries=5):
    for i in range(retries):
        try:
            return fn()
        except Exception as e:
            if "429" in str(e):
                wait = (2 ** i) + random.random()
                print(f"[429] Retry after {wait:.1f}s...")
                time.sleep(wait)
            else:
                raise e
    raise RuntimeError("Too many retries")


def clean_gemini_text(text: str) -> str:
    """
    Loại bỏ ```json, ``` và các ký tự markdown.
    """
    cleaned = text.strip()

    # Remove code blocks if exist
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "")
        cleaned = cleaned.replace("```", "")

    # Remove other garbage
    cleaned = cleaned.strip()

    return cleaned


def build_jlpt_prompt(level, count):
    level = level.upper()
    if not level.startswith("N"):
        level = "N" + level

    desc = LEVEL_INFO.get(level, "JLPT Japanese")

    return f"""
Create EXACTLY {count} JLPT {level} grammar questions.

Format:
- A Japanese sentence with ONE blank: ＿＿＿
- 4 Japanese choices
- Only 1 correct answer
- MUST be returned as pure JSON (not markdown, not codeblock)

Example:
[
  {{
    "sentence": "試験の結果＿＿＿クラスが決まります。",
    "choices": ["いかんとも", "いかんによらず", "いかに", "いかんでは"],
    "correct_index": 3
  }}
]

Return ONLY JSON array.
Difficulty: {desc}
"""


def generate_jlpt_quiz(level="N5", count=10):
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY")

    prompt = build_jlpt_prompt(level, count)

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")

        response = retry_call(lambda: model.generate_content(prompt))

        raw_text = response.text or ""
        print("========== RAW GEMINI ==========")
        print(raw_text)
        print("================================")

        cleaned = clean_gemini_text(raw_text)

        # Must start with [
        if not cleaned.startswith("["):
            raise RuntimeError("Gemini output not JSON")

        data = json.loads(cleaned)

        # Validate
        questions = []
        for q in data:
            if (
                isinstance(q, dict)
                and "sentence" in q
                and isinstance(q.get("choices"), list)
                and len(q["choices"]) == 4
                and isinstance(q.get("correct_index"), int)
            ):
                questions.append(q)

        if not questions:
            raise RuntimeError("Gemini JSON structure invalid")

        return questions[:count]

    except Exception as e:
        raise RuntimeError(f"Failed to generate quiz: {e}")
