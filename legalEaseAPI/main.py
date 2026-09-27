import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from legalEaseAPI.routes import router
import config

app = FastAPI(
    title="LegalEase - AI Legal Document Generator",
    description="Backend API powering AI-driven legal document generation with Google Gemini.",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for health and discovery
@app.get("/")
def home():
    return {
        "message": "Welcome to LegalEase AI Legal Document Generator API",
        "docs": "/docs",
        "status": "online"
    }

# Include routes from routes.py module
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "legalEaseAPI.main:app",
        host=config.BACKEND_HOST,
        port=config.BACKEND_PORT,
        reload=True
    )
