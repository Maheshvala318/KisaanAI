# Architecture

## Pattern
**Service-Oriented Architecture** with 4 loosely-coupled services:
1. **Rasa Server** — NLU + Dialogue Management (port 5005)
2. **Rasa Action Server** — Custom Python actions (port 5055)
3. **Plant Model API** — FastAPI image classification (port 8001)
4. **React Frontend** — SPA chat interface (port 3000)

## Data Flow
```
User (Browser)
    ↓ HTTP POST (text/image)
React Frontend (Chat.jsx)
    ├── Text → Rasa Webhook (POST /webhooks/rest/webhook)
    │       ↓
    │   Rasa NLU (intent classification + entity extraction)
    │       ↓
    │   Rasa Core (dialogue policy → triggers custom action)
    │       ↓
    │   Action Server (actions.py / kisaan_disease_actions.py)
    │       ├── CSV Lookup (disease_data DataFrame)
    │       ├── RAG Pipeline (FAISS/TF-IDF → Gemini/Groq generation)
    │       └── Translation (Gemini-based)
    │       ↓
    │   Response → Frontend
    │
    └── Image → Plant Model API (POST /predict)
            ↓
        PyTorch ResNet → predicted_label
            ↓
        Label sent as metadata to Rasa webhook
```

## Key Components
| Component | File(s) | Responsibility |
|-----------|---------|---------------|
| Disease Info Action | `actions/actions.py` | Main Rasa action: disease lookup, RAG, CSV fallback |
| Smart Disease Action | `actions/kisaan_disease_actions.py` | Enhanced action with image detection, HTML generation, localization |
| RAG Pipeline | `actions/rag.py` | FAISS index, TF-IDF retriever, prompt building, LLM generation |
| LLM Provider | `actions/llm_provider.py` | Gemini-first with Groq fallback abstraction |
| Plant Classifier | `Image_model/plant_model_service.py` | FastAPI + PyTorch inference endpoint |
| Chat UI | `frontend/src/Chat.jsx` | React chat interface with voice, image upload, translation |
| Landing Page | `frontend/src/Home.jsx` | Hero page with background slideshow |

## Entry Points
- `rasa run` — Starts Rasa server
- `rasa run actions` — Starts action server
- `python Image_model/plant_model_service.py` — Starts plant model API
- `cd frontend && npm start` — Starts React dev server
