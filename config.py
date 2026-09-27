import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# ==========================================
# Google Gemini API Configuration
# ==========================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip('"\'')
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip('"\'')

# ==========================================
# Backend Server Configuration
# ==========================================
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0").strip('"\'')
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
BACKEND_URL = os.getenv("BACKEND_URL", f"http://localhost:{BACKEND_PORT}").strip('"\'')

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
