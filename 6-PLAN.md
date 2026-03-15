# 6-PLAN.md — Phase 6: Manual Local Deployment

## Goals
Run the KisaanAI project locally without Docker dependencies due to infrastructure constraints.

## Proposed Changes

### 1. Environment Verification
- **Python**: Ensure `rasa` and `uvicorn` are installed in the local environment.
- **Node**: Ensure `npm` dependencies are installed in `frontend`.

### 2. Manual Startup Sequence (Wave Execution)
- **Wave 1**: Start Action Server (`rasa run actions`).
- **Wave 2**: Start Plant Model API (`uvicorn plant_model_service:app`).
- **Wave 3**: Start Rasa Server (`rasa run --enable-api`).
- **Wave 4**: Start Frontend React App (`npm start`).

## Verification Plan
1. Check port 5055 (Actions).
2. Check port 8001 (Plant API).
3. Check port 5005 (Rasa).
4. Check port 3000 (Frontend).
