# KisaanAI Health Chatbot 🚀🌾

<div align="center">
  <img src="https://img.shields.io/badge/AI-Computer_Vision-blue?style=for-the-badge&logo=pytorch" alt="Computer Vision">
  <img src="https://img.shields.io/badge/RAG-Fact_Based_Generation-success?style=for-the-badge" alt="RAG">
  <img src="https://img.shields.io/badge/Language-Multilingual-ff69b4?style=for-the-badge&logo=googletranslate" alt="Multilingual">
</div>

<br>

**KisaanAI** is a high-performance, multilingual chatbot designed to empower farmers with instant plant disease identification and treatment advice. By combining **Computer Vision**, **Generative AI**, and **Retrieval Augmented Generation (RAG)**, it provides authenticated, fact-based health consultant services in native languages.

## ✨ Key Features

- 📸 **AI Image Identification**: Instant detection of 38+ plant diseases using deep learning patterns.
- 🧠 **Fact-Based RAG Architecture**: Overcomes LLM hallucinations. Treatment advice is strictly pulled from verified, structured datasets.
- 🗣️ **Multilingual Support**: Real-time conversation support in **English, Hindi, and Gujarati**.
- 🛡️ **Contextual Memory**: Robust conversation history scanning maintains context across image analysis sessions and subsequent questions.
- 🚀 **Cloud-Native Deployment**: Fully dockerized environment configured for streamlined local routing and public deployment (Nginx).

## 🛠️ Technology Stack

- **Machine Learning & AI Core**: PyTorch (ResNet for CV), Rasa 3.6 (NLU & Conversation Flow).
- **Large Language Models**: Google Gemini Pro / Groq (Llama 3 70B).
- **Frontend App**: React.js with beautiful Tailwind-inspired UI.
- **Backend Orchestration**: Docker, Nginx Reverse Proxy, Python Action Server.
- **Data Engineering**: Vector Search logic, Data parsing, Fuzzy matching.

## ⚙️ How It Works

1. **User Interaction**: Users can type questions or upload pictures of diseased crops via the robust React UI.
2. **Vision Analysis**: The image goes through the specialized PyTorch model container, which identifies the specific disease present.
3. **Fact Retrieval (RAG)**: Based on the classified disease and user prompt, the system queries its comprehensive offline knowledge base for exact symptoms, treatments, and preventative actions.
4. **Natural Language Generation**: The LLM synthesizes the retrieved facts into a natural, easy-to-understand response native to the user's selected language.

## 🚀 Quick Start & Usage

This system is configured to run locally via Docker Compose for easy deployment.

### Prerequisites
- Docker and Docker Compose installed.
- Valid API keys for LLMs (configured in `.env`).

### Running the Application

1. Clone the repository and navigate into the project directory.
2. Ensure you have the `.env` file correctly configured using `.env.example` as a template.
3. Build and launch the services:

```bash
# Start all integrated containers
docker-compose up --build -d
```

4. The frontend will be accessible at `http://localhost:3000`.

### Example Usage Scenario
* **Farmer**: "What is wrong with my Apple tree?" *(Uploads image of apple leaf with black spots)*
* **KisaanAI**: "Our system has identified Apple Scab. To treat this, you should ensure proper spacing around the tree for increased airflow and apply a specialized fungicide early in the season..." 

## 👨‍💻 Team & Contributors

- **Mahesh Vala**

---
*Developed as a sophisticated attempt to merge professional healthcare awareness workflows with agricultural empowerment.*
