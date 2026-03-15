# actions/language_utils.py
"""
Language detection and translation utilities for KisaanAI.
Supports English, Hindi, and Gujarati.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """
    Detect language from text using Unicode character ranges.

    Returns:
        'gu' for Gujarati, 'hi' for Hindi, 'en' for English (default).
    """
    for ch in text:
        if "\u0A80" <= ch <= "\u0AFF":
            return "gu"
        if "\u0900" <= ch <= "\u097F":
            return "hi"
    return "en"


def translate_text(text: str, src_lang: str, tgt_lang: str) -> str:
    """
    Translate text between languages using Gemini LLM.

    Falls back to returning original text if translation fails.
    """
    if not text or src_lang == tgt_lang:
        return text

    try:
        from .llm_provider import generate_text

        lang_names = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}
        tgt_name = lang_names.get(tgt_lang, tgt_lang)
        src_name = lang_names.get(src_lang, src_lang)

        prompt = (
            f"Translate the following text from {src_name} to {tgt_name}. "
            f"Return ONLY the translation, nothing else.\n\n{text}"
        )
        result = generate_text(prompt)
        return result.strip() if result else text
    except Exception as e:
        logger.warning("Translation failed (%s->%s): %s", src_lang, tgt_lang, e)
        return text
