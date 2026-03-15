import os
import sys
from dotenv import load_dotenv

def check_env():
    load_dotenv()
    required_keys = [
        "GENAI_API_KEY",
        "GROQ_API_KEY",
        "DATA_DIR",
        "MODEL_DIR"
    ]
    
    missing = []
    for key in required_keys:
        val = os.getenv(key)
        if not val or val.strip() == "" or val.startswith("dummy"):
            missing.append(key)
    
    if missing:
        print(f"ERROR: Missing or dummy environment variables: {', '.join(missing)}")
        print("Please configure .env before proceeding.")
        sys.exit(1)
        
    print("Environment validation successful.")

if __name__ == "__main__":
    check_env()
