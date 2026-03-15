# actions/translation.py
"""
Translation utilities for KisaanAI.
Uses Google Gemini for text translation between supported languages.
"""
import logging
from typing import Optional, List, Tuple

from .config import GENAI_API_KEY, GENAI_AVAILABLE

logger = logging.getLogger(__name__)

# Language name mapping
LANG_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "gu": "Gujarati",
}


def translate_to_english(text: str) -> str:
    """Translate text to English using centralized LLM provider."""
    if not text:
        return text
    
    from .llm_provider import generate_text
    prompt = (
        "Translate the following agricultural query into clear English. "
        "Return ONLY the translation, nothing else.\n\n" + text
    )
    # Using the centralized function handles both Gemini and Groq fallback
    result = generate_text(prompt, system="You are a professional translator.")
    return result.strip() if result else text


def generate_response_with_gemini(
    context_pieces: List[Tuple[str, str]],
    user_query_en: str,
    target_lang: str,
    intent: Optional[str] = None,
    max_tokens: int = 256,
) -> str:
    """
    Generate a response using Gemini with provided context.

    Args:
        context_pieces: List of (section_key, text) tuples for context.
        user_query_en: The English user question.
        target_lang: Target language code ('en', 'hi', 'gu').
        intent: Optional best-matching intent name for tailoring prompt.
        max_tokens: Maximum tokens for generation.
    """
    # Build context block
    ctx_lines = []
    for key, txt in context_pieces:
        snippet = txt.strip()
        if len(snippet) > 800:
            snippet = snippet[:800] + "..."
        ctx_lines.append(f"{key}:\n{snippet}")
    ctx = "\n\n".join(ctx_lines) if ctx_lines else "No structured context available."

    lang_name = LANG_NAMES.get(target_lang, target_lang)
    instructions = (
        f'You are an expert agricultural assistant. The user asked: "{user_query_en}". '
        f"Use ONLY the context below to answer. Keep it simple, address a farmer, "
        f"use short bullet points (2-6 bullets), and be practical. "
        f'Answer in {lang_name}. If context doesn\'t contain the answer, say "I don\'t know from my sources.".\n'
    )
    if intent:
        instructions += f"Interpret the user's intent as '{intent}'.\n"

    prompt = f"{instructions}\nContext:\n{ctx}\n\nAnswer now:"

    prompt = f"{instructions}\nContext:\n{ctx}\n\nAnswer now:"

    from .llm_provider import generate_text
    # Using centralized provider ensures 1.5-flash and Groq fallback
    result = generate_text(prompt, system="You are an agricultural expert.")
    return result.strip() if result else ""
