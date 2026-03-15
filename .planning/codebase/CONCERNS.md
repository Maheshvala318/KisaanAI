# Concerns & Technical Debt

## 🔴 CRITICAL

### 1. Hardcoded API Key (SECURITY)
- **File:** `gemini_api.py` line 11
- **Issue:** Google API key `AIzaSyAp9dLnPea_-vvlcshsH_ikhaCenW2qgKA` committed to git
- **Impact:** Key is in git history even if file is deleted
- **Fix:** Rotate key, delete file, use environment variables

### 2. Hardcoded Windows Paths
- **File:** `actions/actions.py` line 77 — `C:\Users\LENOVO\Documents\DCS\health_chatbot\data\...`
- **File:** `Image_model/plant_model_service.py` lines 25, 28 — `C:\Users\LENOVO\Documents\DCS\health_chatbot\Image_model\...`
- **Impact:** App won't run on any other machine or in containers
- **Fix:** Use relative paths + environment variables

### 3. XSS Vulnerability
- **File:** `frontend/src/Chat.jsx` line 501
- **Issue:** `dangerouslySetInnerHTML={{ __html: msg.text }}` renders bot HTML responses unsanitized
- **Impact:** Malicious HTML/JS could execute in user's browser
- **Fix:** Use DOMPurify to sanitize HTML before rendering

## 🟠 HIGH

### 4. Monolithic actions.py (726 lines)
- Single file handles: config, CSV loading, FAISS init, text normalization, disease matching, NLU vectorization, translation, Rasa action, response generation
- Duplicate `import os` (lines 2, 46)
- Duplicate `logger = logging.getLogger(...)` (lines 49-50, 70-71)
- `importlib.metadata` compatibility shim (lines 25-45) — no longer needed

### 5. No requirements.txt or dependency management
- No way to reproduce the Python environment
- No version pinning

### 6. Model files tracked in git (~500MB)
- `models/` contains 19 `.tar.gz` Rasa model archives
- `Image_model/plant_disease_model.pth` is 94MB
- `.gitignore` only has 1 line: `node_modules`

### 7. Entirely dead language_utils.py
- `actions/language_utils.py` is 100% commented-out code (78 lines of comments)
- Contains 3 different attempted implementations, all commented out

## 🟡 MEDIUM

### 8. Dead code files at root
- `gemini_api.py` — Old QA loop with deprecated API, replaced by `llm_provider.py`
- `inspect_genai.py` — Debug script
- `demo.py` — Empty file
- `backend_translate.py` — Flask server depending on deleted `gemini_api.py`

### 9. Rasa config issues
- `config.yml`: `pipeline: null` and `policies: null` — using silent defaults
- `data/nlu.yml`: Duplicate `describe_symptoms` intent (lines 122, 149)
- `domain.yml`: Missing `action_get_disease_info` registration (only has `action_get_disease_info_smart`)

### 10. Root-level package.json confusion
- Root `package.json` has `axios` and `react-icons` (frontend deps)
- Scripts reference nonexistent `scripts/start_rasa.ps1`
- Creates confusion with `frontend/package.json`

### 11. Inconsistent naming
- `Image_model/` (PascalCase with underscore) vs Python convention (`image_model/`)
- Mixed `KisaanAI` vs `KrishiAI` branding in frontend

### 12. No `.env` configuration
- API keys only via `os.environ.get()` with no documentation of required env vars
- No `.env.example` template
