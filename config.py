import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# ==========================================
# API Configuration
# ==========================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip('"\'')
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip('"\'')

# ==========================================
# Server Configuration
# ==========================================
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0").strip('"\'')
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
BACKEND_URL = os.getenv("BACKEND_URL", f"http://localhost:{BACKEND_PORT}").strip('"\'')

# ==========================================
# Firebase Web App Configuration
# ==========================================
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "").strip('"\'')
FIREBASE_AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN", "").strip('"\'')
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "").strip('"\'')
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "").strip('"\'')
FIREBASE_MESSAGING_SENDER_ID = os.getenv("FIREBASE_MESSAGING_SENDER_ID", "").strip('"\'')
FIREBASE_APP_ID = os.getenv("FIREBASE_APP_ID", "").strip('"\'')
FIREBASE_MEASUREMENT_ID = os.getenv("FIREBASE_MEASUREMENT_ID", "").strip('"\'')
FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip('"\'')

# Helper dictionary for Firebase Client SDK config
FIREBASE_CONFIG = {
    "apiKey": FIREBASE_API_KEY,
    "authDomain": FIREBASE_AUTH_DOMAIN,
    "projectId": FIREBASE_PROJECT_ID,
    "storageBucket": FIREBASE_STORAGE_BUCKET,
    "messagingSenderId": FIREBASE_MESSAGING_SENDER_ID,
    "appId": FIREBASE_APP_ID,
    "measurementId": FIREBASE_MEASUREMENT_ID
}

# ==========================================
# Asset Paths
# ==========================================
IMAGE_DIR = BASE_DIR / "image"
LOGO_PATH = IMAGE_DIR / "Logo.png"
INVERSE_LOGO_PATH = IMAGE_DIR / "inverseLogo.png"
WEB_LOGO_PATH = str(LOGO_PATH if LOGO_PATH.exists() else INVERSE_LOGO_PATH)

# Company Branding defaults
COMPANY_NAME = "LegalEase Inc."
COMPANY_CONTACT = "contact@legalease.com"
COMPANY_FOOTER = f"{COMPANY_NAME} | {COMPANY_CONTACT} | All Rights Reserved."
