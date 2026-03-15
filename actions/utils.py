# actions/utils.py
"""
Text normalization and formatting utilities for KisaanAI.
"""
import re
from typing import List


def normalize_text(s: str) -> str:
    """Lower, remove non-alphanum, collapse whitespace."""
    if s is None:
        return ""
    s = str(s).lower()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def token_candidates(text: str, min_len: int = 3) -> List[str]:
    """Extract tokens of minimum length from normalized text."""
    text = normalize_text(text)
    return [t for t in text.split() if len(t) >= min_len]


def text_to_bullets(text: str, max_items: int = 6) -> str:
    """Convert raw text to bullet points, limited to max_items."""
    if not text:
        return ""

    lines = [ln.strip("•- \t") for ln in text.splitlines() if ln.strip()]
    if not lines:
        parts = re.split(r"(?<=[.!?])\s+", text)
        lines = [p.strip("•- \t") for p in parts if p.strip()]

    lines = lines[:max_items]
    return "\n".join(f"• {ln}" for ln in lines)
