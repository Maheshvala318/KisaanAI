# GSD Journal — Health Chatbot

## 2026-03-15: The "Millet Hallucination" Cure

### Context
User reported that the bot was failing to identify "Peach Bacterial Spot" and instead hallucinating generic advice about "millets" and harvesting and was returning Gujarati translations that were entirely made up by the LLM.

### Actions Taken
- **Diagnostic Logging**: Added raw tracker logging to `actions.py` to confirm that the `image_metadata` slot was being lost between the frontend and action server.
- **Bulletproof Parser**: Implemented a regex-based scanner in `actions.py` that reads the entire conversation history to find the `Image Analysis:` label, ensuring the bot never "forgets" the identified disease.
- **Hallucination Shields**: 
    - Updated `csv_lookup.py` with stricter matching thresholds (0.45) to prevent vague queries matching random diseases.
    - Updated `_translate_response` in `actions.py` to use a strict `LANG_LABELS` lookup for UI errors, forbidding LLM "improvisation".
- **Greedy Retrieval**: Forced the Action Server to automatically fetch Symptoms, Treatment, and Prevention whenever an image label is detected.
- **Server Stabilization**: Resolved Port 5055 conflicts to ensure latest code changes were actually running.
- **Task Orchestration**: Initialized GSD-compliant task list, `REQUIREMENTS.md`, and `ROADMAP.md`.
- **Phase Planning**: Created `6-PLAN.md` for controlled system startup.
### 2026-03-15: Chat Failure & Endpoint Fix

### Context
User reported a "Couldn't generate a text response" error when asking about Late Blight symptoms.

### Actions Taken
- **Log Diagnosis**: Analyzed `rasa_log.txt` and found `aiohttp.client_exceptions.ClientConnectorError: Cannot connect to host action_server:5055`.
- **Root Cause**: Rasa was configured to use Docker hostnames (`action_server`) in a manual local execution environment.
- **Endpoint Update**: Modified `endpoints.yml` to point to `localhost:5055/webhook`.
- **Process Cleanup**: Killed the stale Rasa process (PID 8780) and performed a clean restart with Twilio environment variables injected.

### Result
Rasa Server is successfully loading with the correct local endpoint. Communication between Rasa and the Action Server is restored.

### Next Steps
- User to verify "Late Blight" symptoms query.
- Cleanup of any remaining print/log statements used for debugging.
- **2026-03-15: GSD Live Deployment Ready**
    - Created `Dockerfile.live` to bundle Rasa, Actions, and Image API into one image.
    - Setup `entrypoint.sh` and `nginx_prod.conf` for multi-service orchestration on Port 7860.
    - Created `DEPLOYMENT.md` with step-by-step instructions for GitHub, Hugging Face, and Vercel.
    - Prepared `.dockerignore` to optimize build performance.
    - **Milestone**: Performed first commit for Live Deployment (v0.1.0).
