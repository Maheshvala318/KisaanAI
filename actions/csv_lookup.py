import logging
import difflib
import re
from typing import Optional, List, Tuple
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import disease_data
from .utils import normalize_text

logger = logging.getLogger(__name__)

def get_info_from_csv(disease_name: str, column: str, crop: Optional[str] = None) -> str:
    """Look up a specific column value for a disease/crop combination."""
    if disease_data.empty:
        return ""
    try:
        df = disease_data
        # Filter by disease name (canonical is best)
        mask = df["disease_name"].astype(str).str.lower() == disease_name.lower()
        
        # If crop is provided, try to narrow it down
        if crop and "crop" in df.columns:
            crop_mask = df["crop"].astype(str).str.lower() == crop.lower()
            if (mask & crop_mask).any():
                mask = mask & crop_mask
        
        if mask.any() and column in df.columns:
            val = df.loc[mask, column].iloc[0]
            return "" if pd.isna(val) else str(val)
            
    except Exception as e:
        logger.exception("Error in get_info_from_csv: %s", e)
    return ""

def get_all_crops_for_disease(disease_name: str) -> List[str]:
    """Get all unique crops associated with a disease."""
    if disease_data.empty or "crop" not in disease_data.columns:
        return []
    mask = disease_data["disease_name"].astype(str).str.lower() == disease_name.lower()
    if mask.any():
        return disease_data.loc[mask, "crop"].dropna().unique().tolist()
    return []

def get_token_overlap_score(query: str, target: str) -> float:
    """Calculate how many tokens from query exist in target."""
    q_tokens = set(re.findall(r'\w+', query.lower()))
    t_tokens = set(re.findall(r'\w+', target.lower()))
    if not q_tokens: return 0.0
    overlap = q_tokens.intersection(t_tokens)
    return len(overlap) / len(q_tokens)

def find_best_match(query: str, candidates: List[str], threshold: float = 0.35) -> Tuple[Optional[str], float]:
    """Generic TF-IDF + Token Overlap fuzzy matcher."""
    if not query or not candidates:
        return None, 0.0
    try:
        q_clean = query.lower()
        
        # 1. Check for Perfect Token Overlap first (e.g. "Bacterial Spot" in "Bacterial Spot/Blight")
        best_overlap_match = None
        max_overlap = 0.0
        for cand in candidates:
            score = get_token_overlap_score(q_clean, cand)
            if score > max_overlap:
                max_overlap = score
                best_overlap_match = cand
        
        if max_overlap >= 0.8: # If 80%+ of query words are in the candidate
            return best_overlap_match, max_overlap

        # 2. Fallback to TF-IDF
        vec = TfidfVectorizer(analyzer="char", ngram_range=(2, 4))
        X = vec.fit_transform(candidates)
        q_vec = vec.transform([q_clean])
        sims = cosine_similarity(q_vec, X).flatten()
        idx = sims.argmax()
        score = sims[idx]
        
        # Boost score if there's partial word overlap
        if max_overlap > 0.5:
             score = max(score, max_overlap)

        return (candidates[idx], score) if score >= threshold else (None, score)
    except Exception:
        matches = difflib.get_close_matches(q_clean, [c.lower() for c in candidates], n=1, cutoff=threshold)
        if matches:
            for c in candidates:
                if c.lower() == matches[0]: return c, 0.5
        return None, 0.0

def find_disease_smart(user_text: str, detected_crop: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Find best (disease, crop) match from user text or image label.
    Specifically optimized for labels like "Peach___Bacterial_spot".
    """
    if disease_data.empty:
        return None, None

    df = disease_data
    user_lower = user_text.lower()
    
    # --- Step 1: Resolve Crop ---
    crop = detected_crop
    unique_crops = df["crop"].dropna().unique().tolist()
    
    if not crop:
        for c in unique_crops:
            if c.lower() in user_lower:
                crop = c
                break
        if not crop:
            match, score = find_best_match(user_text, unique_crops, threshold=0.6)
            if match: crop = match

    crop_exists = any(c.lower() == str(crop).lower() for c in unique_crops) if crop else False

    # --- Step 2: Resolve Disease ---
    unique_diseases = df["disease_name"].dropna().unique().tolist()
    
    # Clean text: remove "Peach" from "Peach Bacterial Spot" to search for the disease part better
    search_text = user_lower
    if crop:
        search_text = search_text.replace(crop.lower(), "").strip()
    if not search_text: search_text = user_lower

    # 1. Search Within Crop (Primary)
    if crop and crop_exists:
        crop_diseases = df[df["crop"].astype(str).str.lower() == crop.lower()]["disease_name"].unique().tolist()
        match, score = find_best_match(search_text, crop_diseases, threshold=0.35)
        if match: return match.lower(), crop

    # 2. Search Globally (Resilient Fallback)
    # Stricter threshold for global search to prevent random "millets" hallucinations
    vague_words = ["disease", "problem", "crop", "leaf", "plant", "what", "is"]
    search_tokens = re.findall(r'\w+', search_text.lower())
    is_vague = all(t in vague_words for t in search_tokens)
    
    if is_vague and len(search_tokens) < 4:
        return None, crop if crop_exists else None

    match, score = find_best_match(search_text, unique_diseases, threshold=0.45)
    if match:
        final_crop = crop if crop_exists else df[df["disease_name"] == match]["crop"].iloc[0]
        return match.lower(), final_crop

    return None, crop if crop_exists else None

def get_canonical_disease_name(disease: str) -> str:
    """Return pretty/canonical disease name from CSV."""
    if not disease or disease_data.empty:
        return disease or "this disease"
    mask = disease_data["disease_name"].astype(str).str.lower() == disease.lower()
    if mask.any():
        return str(disease_data.loc[mask, "disease_name"].iloc[0])
    return disease

