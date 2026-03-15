# REQUIREMENTS.md — KisaanAI Health Chatbot

## v1.0.0 (Current Milestone: Live Production Deployment)

### Core Functional Requirements
1. **Multilingual Disease Diagnosis**: 
   - Support for English, Hindi, and Gujarati.
   - Text and Image-based identification.
2. **Hallucination Suppression**: 
   - All treatment and symptom advice must be derived from verified CSV datasets.
   - LLMs (Gemini/Groq) must synthesize facts, not invent them.
3. **Robust Retrieval**: 
   - Greedy retrieval of Symptoms, Treatment, and Prevention upon disease identification.
   - Bulletproof history scanner to maintain context of identified diseases.
4. **Computer Vision API**:
   - PyTorch-based service for 38+ plant disease classifications.
5. **Interactive UI**:
   - Responsive React-based chat interface.
   - Support for image uploads.

### Technical Constraints
- **Stack**: Rasa 3.6, Python 3.9, React, Docker Compose.
- **API Dependencies**: Google Gemini, Groq (Llama 3 70B).
- **Security**: Environment variable based configuration (.env).
- **Environment**: Fully dockerized for local and live deployment.

### Production & Operational Requirements
- **Health Monitoring**: Docker health checks for all services.
- **Logging**: Standardized stdout logging for all backend services.
- **Dependency Management**: Explicit versioning in `requirements.txt` and `package.json`.
- **API Resilience**: Graceful degradation if LLM APIs reach rate limits.

### Out of Scope for v1.0.0
- User authentication/profiles (Resume demo focus).
- Real-time video diagnosis.
- Direct marketplace integration for pesticides.
