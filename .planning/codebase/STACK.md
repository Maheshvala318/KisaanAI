# Technology Stack

## Languages & Runtimes
- **Python 3.x** — Backend, Rasa actions, ML model serving, RAG pipeline
- **JavaScript (React 19)** — Frontend SPA via Create React App
- **YAML** — Rasa NLU/domain/stories configuration

## Core Frameworks
| Layer | Framework | Version | Purpose |
|-------|-----------|---------|---------|
| Chatbot NLU | Rasa Open Source | 3.x | Intent classification, entity extraction, dialogue management |
| Frontend | React | 19.1.1 | Chat UI, hero landing page |
| ML Serving | FastAPI | latest | Plant disease image classification API |
| LLM | Google Generative AI SDK | latest | Gemini 2.0/2.5 flash for generation & translation |
| LLM Fallback | Groq SDK | latest | Llama 3.1 8B as Gemini fallback |
| Styling | styled-components | 6.1.19 | CSS-in-JS for React components |
| Vector Search | FAISS | latest | Similarity search on disease embeddings |
| Text Retrieval | scikit-learn TF-IDF | latest | Fallback retriever when FAISS unavailable |
| Image Model | PyTorch + torchvision | latest | ResNet-based plant disease classifier (38 classes) |

## Key Dependencies
### Python
- `rasa-sdk` — Custom action server
- `pandas` — CSV/data operations
- `faiss-cpu` — Vector similarity search
- `scikit-learn` — TF-IDF vectorizer, cosine similarity
- `google-generativeai` — Gemini API SDK
- `groq` — Groq Cloud API
- `torch`, `torchvision` — PyTorch for image classification
- `Pillow` — Image processing
- `uvicorn` — ASGI server for FastAPI

### JavaScript
- `axios` — HTTP client (Rasa webhook calls)
- `react-router-dom` 7.x — Client-side routing
- `styled-components` 6.x — CSS-in-JS

## Configuration
- **`.env` file exists** — API keys set via environment variables (Rasa action server uses this).
- **`requirements.txt` exists** — Python dependencies are documented.
- **Rasa configuration** — Pipeline and policies set in `config.yml`.
- **Logic Layers**:
    - `actions/actions.py`: Core routing and LLM logic.
    - `actions/csv_lookup.py`: Fuzzy matching and CSV processing.
    - `actions/rag.py`: Vector search and context retrieval.
