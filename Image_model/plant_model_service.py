# image_model/plant_model_service.py
"""
FastAPI service for plant disease image classification.
Uses a PyTorch ResNet model trained on 38 plant disease classes.
"""
import io
import os
from pathlib import Path
from typing import List

import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

# ======================================================
# CONFIG
# ======================================================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Paths — use environment variables with sensible defaults
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = os.environ.get(
    "PLANT_MODEL_PATH",
    str(BASE_DIR / "plant_disease_model.pth")
)
CLASS_NAMES_PATH = os.environ.get(
    "CLASS_NAMES_PATH",
    str(BASE_DIR / "class_names.txt")
)


def load_class_names(path: str) -> List[str]:
    """Load class names from file or return hardcoded defaults."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    # Fallback: hardcoded classes for the 38-class model
    return [
        'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust',
        'Apple___healthy', 'Blueberry___healthy',
        'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
        'Corn_(maize)___Common_rust_', 'Corn_(maize)___Northern_Leaf_Blight',
        'Corn_(maize)___healthy', 'Grape___Black_rot',
        'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
        'Grape___healthy', 'Orange___Haunglongbing_(Citrus_greening)',
        'Peach___Bacterial_spot', 'Peach___healthy',
        'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
        'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
        'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew',
        'Strawberry___Leaf_scorch', 'Strawberry___healthy',
        'Tomato___Bacterial_spot', 'Tomato___Early_blight',
        'Tomato___Late_blight', 'Tomato___Leaf_Mold',
        'Tomato___Septoria_leaf_spot',
        'Tomato___Spider_mites Two-spotted_spider_mite',
        'Tomato___Target_Spot',
        'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
        'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
    ]


CLASS_NAMES = load_class_names(CLASS_NAMES_PATH)

# ======================================================
# IMAGE TRANSFORMS
# ======================================================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

# ======================================================
# LOAD MODEL
# ======================================================
def load_model(path: str):
    """Load the full PyTorch model (architecture + weights)."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found at {path}")

    print(f"Loading model from: {path}")
    model = torch.load(path, map_location=DEVICE, weights_only=False)
    model.to(DEVICE)
    model.eval()
    return model


MODEL = load_model(MODEL_PATH)
print(f"✅ Plant disease model loaded from {MODEL_PATH} on {DEVICE}")

# ======================================================
# FASTAPI APP
# ======================================================
app = FastAPI(title="Plant Disease Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionResponse(BaseModel):
    predicted_index: int
    predicted_label: str
    probabilities: List[float]


@app.get("/")
def root():
    return {"status": "ok", "message": "Plant disease model API running"}


@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": MODEL is not None, "device": str(DEVICE)}


@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    """Accept an image file and return disease prediction."""
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    input_tensor = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        output = MODEL(input_tensor)
        probs = torch.softmax(output, dim=1)[0]
        predicted_idx = int(torch.argmax(probs).item())
        probabilities = probs.cpu().tolist()

    predicted_label = (
        CLASS_NAMES[predicted_idx]
        if 0 <= predicted_idx < len(CLASS_NAMES)
        else f"class_{predicted_idx}"
    )

    return PredictionResponse(
        predicted_index=predicted_idx,
        predicted_label=predicted_label,
        probabilities=probabilities,
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PLANT_API_PORT", 8001))
    uvicorn.run("plant_model_service:app", host="0.0.0.0", port=port, reload=True)
