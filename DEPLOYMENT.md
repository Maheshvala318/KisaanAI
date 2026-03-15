# Deployment Guide: KisaanAI Health Chatbot 🚀🌐

Build this project once and make it live for your resume!

## Phase 1: GitHub Preparation
1. **Initialize Git**:
   ```powershell
   git init
   git add .
   git commit -m "Initialize KisaanAI Production Build"
   ```
2. **Create Repository**: Create a new repository on GitHub (e.g., `health-chatbot`).
3. **Push Code**:
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/health-chatbot.git
   git branch -M main
   git push -u origin main
   ```

## Phase 2: Deploy Backend (Hugging Face Spaces)
1. **Create Space**: Go to [Hugging Face Spaces](https://huggingface.co/spaces) -> **New Space**.
2. **Settings**:
   - **Name**: `kisaan-backend`
   - **SDK**: **Docker** (Blank template)
   - **Privacy**: Public (for resume link)
3. **Upload/Link**: Use the "Files" tab to upload your files OR link the GitHub repo.
4. **Environment Variables**: Go to **Settings** -> **Variables and Secrets**:
   - `GENAI_API_KEY`: [Your Google Key]
   - `GROQ_API_KEY`: [Your Groq Key]

## Phase 3: Deploy Frontend (Cloudflare Pages)
1. **Login**: Go to [Cloudflare Dashboard](https://dash.cloudflare.com/) -> **Workers & Pages**.
2. **Create Application**: Click **Create Application** -> **Pages** -> **Connect to Git**.
3. **Link Repo**: Select your `health-chatbot` repository.
4. **Build Settings**:
   - **Project Name**: `kisaan-ai`
   - **Framework Preset**: `Create React App`
   - **Build Command**: `npm run build`
   - **Build Output Directory**: `frontend/build`
   - **Root Directory**: `/frontend`
5. **Environment Variables**:
   - Go to **Settings** -> **Functions** (or **Environment Variables** for Pages).
   - Add `REACT_APP_RASA_URL`: `https://YOUR_HF_UID-kisaan-backend.hf.space/rasa/webhooks/rest/webhook`
   - Add `REACT_APP_PLANT_API_URL`: `https://YOUR_HF_UID-kisaan-backend.hf.space/image/predict`
6. **Save and Deploy**.

## Phase 4: Final Verification
- Access your Cloudflare URL (e.g., `kisaan-ai.pages.dev`).
- Upload a plant image and verify the "Bacterial Spot" identification works!
