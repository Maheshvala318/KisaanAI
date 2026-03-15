# actions/config.py
"""
Centralized configuration for the KisaanAI action server.
All paths, API keys, and data loading happen here.
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

import pandas as pd

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# ----- API Keys -----
GENAI_API_KEY = os.environ.get("GENAI_API_KEY") or os.environ.get("genai_api_key")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or os.environ.get("groq_api_key")

# ----- Paths -----
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("DATA_DIR", PROJECT_ROOT / "data"))
MODEL_DIR = Path(os.environ.get("MODEL_DIR", PROJECT_ROOT / "image_model"))

# Disease CSV — use environment variable or default
DISEASE_CSV_PATH = os.environ.get(
    "DISEASE_CSV_PATH",
    str(DATA_DIR / "combined_data.csv")
)

# ----- Configure Gemini SDK -----
try:
    from google import generativeai as genai
    GENAI_AVAILABLE = True
    if GENAI_API_KEY:
        genai.configure(api_key=GENAI_API_KEY)
        logger.info("Configured Google GenAI SDK.")
    else:
        logger.warning("GENAI_API_KEY not set; Gemini features disabled.")
except ImportError:
    genai = None
    GENAI_AVAILABLE = False
    logger.warning("google-generativeai not installed.")

# ----- Load Disease Data -----
def load_disease_data(csv_path: str = DISEASE_CSV_PATH) -> pd.DataFrame:
    """Load and normalize disease CSV data."""
    try:
        if not os.path.exists(csv_path):
            logger.error("Disease CSV not found at %s", csv_path)
            return pd.DataFrame()

        df = pd.read_csv(csv_path)
        # Normalize columns for internal use
        orig_cols = df.columns.tolist()
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Map 'disease' to 'disease_name' if that's what's in combined_data.csv
        if "disease" in df.columns and "disease_name" not in df.columns:
            df = df.rename(columns={"disease": "disease_name"})

        logger.info(
            "Loaded disease CSV with %d rows, columns: %s",
            len(df), df.columns.tolist()
        )

        # Create description column if missing - used for RAG
        if "description" not in df.columns:
            # For combined_data.csv, we want a rich description
            desc_cols = [c for c in df.columns if c not in ["disease_name", "crop"]]
            if desc_cols:
                df["description"] = df[desc_cols].astype(str).agg(" ".join, axis=1)
            else:
                df["description"] = df.astype(str).agg(" ".join, axis=1)

        return df
    except Exception as e:
        logger.exception("Failed to read disease CSV at %s: %s", csv_path, e)
        return pd.DataFrame()


# Module-level data (loaded once at import time)
disease_data = load_disease_data()

# Precompute normalized disease names
NORMALIZED_DISEASE_NAMES: List[str] = []
if not disease_data.empty and "disease_name" in disease_data.columns:
    from .utils import normalize_text
    NORMALIZED_DISEASE_NAMES = [
        normalize_text(str(x)) for x in disease_data["disease_name"].tolist()
    ]
