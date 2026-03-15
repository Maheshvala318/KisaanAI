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

### Result
The bot now correctly identifies "Peach Bacterial Spot", maps it to "Bacterial Spot/Blight" in the CSV, and returns fact-based Gujarati reports instead of millet hallucinations.

### Next Steps
- Final verification with USER for Peach image.
- Cleanup of any remaining print/log statements used for debugging.
- **2026-03-15: GSD Live Deployment Ready**
    - Created `Dockerfile.live` to bundle Rasa, Actions, and Image API into one image.
    - Setup `entrypoint.sh` and `nginx_prod.conf` for multi-service orchestration on Port 7860.
    - Created `DEPLOYMENT.md` with step-by-step instructions for GitHub, Hugging Face, and Vercel.
    - Prepared `.dockerignore` to optimize build performance.
    - **Milestone**: Performed first commit for Live Deployment (v0.1.0).
