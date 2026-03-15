# actions/llm_provider.py
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from .config import (
    GENAI_API_KEY, 
    GROQ_API_KEY, 
    GENAI_AVAILABLE,
)

# ---------------- Gemini ----------------
try:
    from google import generativeai as genai
except Exception:
    genai = None

# Configure Gemini
if GENAI_API_KEY and GENAI_AVAILABLE and genai:
    try:
        genai.configure(api_key=GENAI_API_KEY)
        logger.info("Gemini configured (via GenAI SDK)")
    except Exception as e:
        logger.warning("Gemini config failed: %s", e)

# ---------------- Groq ----------------
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except Exception:
    Groq = None
    GROQ_AVAILABLE = False

# Configure Groq
_groq_client: Optional[Groq] = None
if GROQ_API_KEY and GROQ_AVAILABLE and Groq:
    try:
        _groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("Groq configured")
    except Exception as e:
        logger.warning("Groq config failed: %s", e)

# Configure Groq
_groq_client: Optional[Groq] = None
if GROQ_API_KEY and GROQ_AVAILABLE:
    try:
        _groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("Groq configured")
    except Exception as e:
        logger.warning("Groq config failed: %s", e)

def _is_quota_error(e: Exception) -> bool:
    msg = str(e).lower()
    return "quota" in msg or "rate" in msg or "429" in msg

def _groq_generate(
    prompt: str,
    system: str,
    model: str = "llama-3.1-8b-instant",  # ✅ UPDATED MODEL
) -> Optional[str]:
    if not _groq_client:
        return None
    try:
        resp = _groq_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.warning("Groq generation failed: %s", e)
        return None

def generate_text(
    prompt: str,
    system: str = "You are a helpful assistant.",
    model: Optional[str] = None,
) -> str:
    # Gemini first
    if GENAI_API_KEY and GENAI_AVAILABLE:
        try:
            # Try latest Gemini
            mdl = genai.GenerativeModel(model or "gemini-1.5-flash")
            resp = mdl.generate_content(prompt)
            if hasattr(resp, "text"):
                return resp.text
        except Exception as e:
            if _is_quota_error(e):
                logger.warning("Gemini quota exceeded → Groq fallback")
            else:
                logger.warning("Gemini error → Groq fallback: %s", e)

    # Groq fallback
    groq_out = _groq_generate(prompt, system)
    if groq_out:
        return groq_out

    return (
        "I am temporarily unable to generate a response. "
        "Please try again later."
    )
