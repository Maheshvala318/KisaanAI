# ROADMAP.md — KisaanAI Health Chatbot

## Milestone: Live Production Deployment (Resume Link)

### Phase 1: Security & Config Fixes (COMPLETED)
- Cleaned up hardcoded keys and stabilized `.env` usage.

### Phase 2: Backend Modular Restructure (COMPLETED)
- Organized actions and utilities into logical modules.

### Phase 3: Identification Hardening (COMPLETED)
- Improved Rasa NLU and intent classification.

### Phase 4: Greedy Image Retrieval & Hallucination Suppression (COMPLETED)
- Forced CSV lookups for all identified diseases.
- Implemented strict translation lookups for UI errors.

### Phase 5: Deep Diagnosis & Bulletproof Parser (COMPLETED)
- Regex-based history scanner to prevent context loss.

### Phase 6: Project Deployment (COMPLETED)
- [x] Stabilized local startup via manual Wave Execution.
- [x] Verified health of all 4 major services (Rasa, Actions, Plant API, Frontend).
- [x] Demonstrated functional end-to-end flow locally.

### Phase 7: Live Deployment (PENDING)
- [ ] Deploy multi-service backend to Hugging Face Spaces.
- [ ] Deploy frontend to Cloudflare/Vercel.

### Phase 8: Final User Verification (PENDING)
- [ ] User acceptance testing for Peach image identification and Gujarati translation.
