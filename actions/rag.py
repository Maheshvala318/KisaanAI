# actions/rag.py
"""
RAG utilities with a TF-IDF fallback retriever.
- build/load FAISS index
- embed via Google GenAI SDK if configured
- TF-IDF retriever returned as a third value for fallback and compatibility
"""

import os
import json
import logging
from typing import List, Dict, Optional, Tuple

import numpy as np
import faiss
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import DATA_DIR
from .llm_provider import generate_text

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

GENAI_API_KEY = os.environ.get("GENAI_API_KEY") or os.environ.get("genai_api_key")
EMBED_MODEL = os.environ.get("RAG_EMBED_MODEL", "models/text-embedding-004")

FAISS_INDEX_PATH = os.environ.get("RAG_FAISS_INDEX", str(DATA_DIR / "faiss_disease.index"))
FAISS_METADATA_PATH = os.environ.get("RAG_FAISS_METADATA", str(DATA_DIR / "faiss_metadata.json"))

DEFAULT_TOP_K = 4

# ---------- TF-IDF Retriever ----------
class TfidfRetriever:
    def __init__(self, texts: List[str], metadata: List[Dict]):
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
        self.texts = texts
        self.metadata = metadata
        self.matrix = self.vectorizer.fit_transform(texts) if texts else None

    def retrieve(self, query: str, top_k: int = DEFAULT_TOP_K) -> List[Dict]:
        if self.matrix is None:
            return []
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.matrix)[0]
        idxs = np.argsort(sims)[::-1][:top_k]
        results = []
        for i in idxs:
            if sims[i] > 0:
                item = self.metadata[i].copy()
                item["_score"] = float(sims[i])
                results.append(item)
        return results

# ---------- Retrieval ----------
def retrieve(query: str,
             top_k: int = DEFAULT_TOP_K,
             index: Optional[faiss.Index] = None,
             metadata: Optional[List[Dict]] = None,
             tfidf_retriever: Optional[TfidfRetriever] = None) -> List[Dict]:

    if index is not None and metadata:
        try:
            vec = TfidfVectorizer().fit_transform([query]).toarray().astype("float32")
            _, I = index.search(vec, top_k)
            return [metadata[i] for i in I[0] if i < len(metadata)]
        except Exception:
            pass

    if tfidf_retriever:
        return tfidf_retriever.retrieve(query, top_k)

    return []

# ---------- Prompt Builder ----------
DEFAULT_SYSTEM = (
    "You are an expert agricultural assistant. Answer the user's question using ONLY the provided context. "
    "If the answer is not available in the context, say 'I don't know'."
)

def build_prompt(retrieved: List[Dict], user_query: str, mode: str = "full", history: Optional[str] = None) -> str:
    context_parts = []
    for r in retrieved:
        name = r.get('disease_name', '')
        crop = r.get('crop', '')
        text = r.get('text', '')
        header = f"{crop} - {name}" if crop else name
        context_parts.append(f"### {header}\n{text}")

    context = "\n\n".join(context_parts) or "No relevant agricultural information found in database."

    history_block = f"\nPrevious conversation context:\n{history}\n" if history else ""

    instructions = (
        "Use bullet points. Keep language simple for farmers. If the user is correcting you or asking about the previous topic, acknowledge the context."
        if mode == "full" else
        "Provide only symptoms in bullet points."
    )

    return f"""{DEFAULT_SYSTEM}

{history_block}
Context:
{context}

User question:
{user_query}

Instructions:
{instructions}
"""

# ---------- Generation (UPDATED) ----------
def generate_from_prompt(prompt: str) -> str:
    # ⬇️ ONLY CHANGE: use llm_provider
    return generate_text(prompt)
# ---------- Initialize (RESTORED – REQUIRED BY actions.py) ----------
def initialize_from_dataframe(
    df: pd.DataFrame,
    text_column: str = "description",
    index_path: str = FAISS_INDEX_PATH,
    metadata_path: str = FAISS_METADATA_PATH,
):
    """
    EXACT ORIGINAL BEHAVIOR:
    - Load FAISS index + metadata if exists
    - Else build TF-IDF retriever
    - Return (index, metadata, tfidf_retriever)
    """

    if df is None or df.empty:
        return None, [], None

    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()

    # Build text + disease names
    if text_column not in df.columns:
        df[text_column] = df.astype(str).agg(" ".join, axis=1)

    texts = df[text_column].astype(str).tolist()
    if "disease_name" in df.columns:
        names = df["disease_name"].astype(str).tolist()
    else:
        names = [f"row_{i}" for i in range(len(df))]

    metadata = []
    for i in range(len(df)):
        meta = {"disease_name": names[i], "text": texts[i]}
        if "crop" in df.columns:
            meta["crop"] = str(df.iloc[i].get("crop", ""))
        metadata.append(meta)

    # TF-IDF retriever (ALWAYS BUILT)
    tfidf_retriever = TfidfRetriever(texts, metadata)

    # Try loading FAISS
    if os.path.exists(index_path) and os.path.exists(metadata_path):
        try:
            index = faiss.read_index(index_path)
            with open(metadata_path, "r", encoding="utf-8") as f:
                loaded_meta = json.load(f)
            logger.info("Loaded FAISS index with %d vectors", index.ntotal)
            return index, loaded_meta, tfidf_retriever
        except Exception as e:
            logger.exception("Failed loading FAISS index: %s", e)

    # FAISS not available → return TF-IDF only (ORIGINAL BEHAVIOR)
    logger.info("FAISS not available, using TF-IDF retriever only")
    return None, metadata, tfidf_retriever
