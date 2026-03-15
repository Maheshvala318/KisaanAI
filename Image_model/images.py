import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from kaggle.api.kaggle_api_extended import KaggleApi
import uvicorn

# -----------------------
# CONFIG
# -----------------------
DATASET_SLUG = "vipoooool/new-plant-diseases-dataset"
LOCAL_DATA_ROOT = Path("data")  # wherever you want to store dataset locally

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# 1. DOWNLOAD DATASET VIA KAGGLE API (ONCE)
# -----------------------
def ensure_dataset_downloaded() -> Path:
    """
    Uses Kaggle API to download & unzip the dataset if not already present.
    Returns the path to the unzipped dataset root.
    """
    LOCAL_DATA_ROOT.mkdir(parents=True, exist_ok=True)

    # We’ll download into data/new-plant-diseases-dataset/
    target_dir = LOCAL_DATA_ROOT / "new-plant-diseases-dataset"

    # Check if we already have the 'train' folder
    train_folder = target_dir / "New Plant Diseases Dataset(Augmented)" / "New Plant Diseases Dataset(Augmented)" / "train"
    if train_folder.exists():
        print("✅ Dataset already downloaded at:", target_dir)
        return target_dir

    print("📥 Downloading Kaggle dataset:", DATASET_SLUG)
    api = KaggleApi()
    api.authenticate()

    # Download and unzip
    api.dataset_download_files(
        DATASET_SLUG,
        path=str(target_dir),
        unzip=True
    )

    print("✅ Dataset downloaded & unzipped at:", target_dir)
    return target_dir


dataset_root = ensure_dataset_downloaded()

# This is the folder that contains class subfolders (Apple___..., Tomato___...)
TRAIN_ROOT = dataset_root / "New Plant Diseases Dataset(Augmented)" / "New Plant Diseases Dataset(Augmented)" / "train"

if not TRAIN_ROOT.exists():
    raise RuntimeError(f"Train folder not found at: {TRAIN_ROOT}")

print("📂 Using TRAIN_ROOT:", TRAIN_ROOT)

# -----------------------
# 2. SERVE IMAGES & LIST ENDPOINT
# -----------------------

# Serve static images from TRAIN_ROOT on /images
app.mount("/images", StaticFiles(directory=str(TRAIN_ROOT)), name="images")


@app.get("/list")
def list_images():
    """
    Returns a list of all images and their labels.

    Response example:
    [
      {
        "image": "/images/Apple___Apple_scab/0a0f18fd-0f3a-4c6a....JPG",
        "label": "Apple___Apple_scab"
      },
      ...
    ]
    """
    items = []
    for label in os.listdir(TRAIN_ROOT):
        label_path = TRAIN_ROOT / label
        if not label_path.is_dir():
            continue

        for img in os.listdir(label_path):
            if img.lower().endswith((".jpg", ".jpeg", ".png")):
                items.append({
                    "image": f"/images/{label}/{img}",
                    "label": label
                })

    return items


@app.get("/")
def root():
    return {"message": "Plant disease dataset API is running."}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
