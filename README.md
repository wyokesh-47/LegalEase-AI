# LegalEase: AI-Powered Legal Document Generator ⚖️

LegalEase is an AI-powered legal document generation platform built with **FastAPI**, **Streamlit**, and **Google Gemini Generative AI**. It enables users to quickly draft, customize, preview, inline-edit, and export formal legal agreements (NDAs, Freelance Contracts, Lease Agreements, Employment Offer Letters, etc.) into **.PDF**, **.DOCX**, and **.TXT** formats.

---

## 🚀 Key Features

1. **AI-Powered Legal Drafting**:
   - Integrated with Google's **Gemini 2.5 Flash / 1.5 Pro** model for context-aware, structured legal clause drafting.
   - Built-in legal template engine for reliable fallback execution.
2. **FastAPI Microservice Backend**:
   - `/generate` POST endpoint with Pydantic schema validation.
   - High-throughput asynchronous routing.
3. **Interactive Streamlit Web UI**:
   - Sleek dark theme matching professional modern legal suites.
   - Branded header logo and dynamic preview card.
4. **Live Inline Document Editor**:
   - One-click inline editing to tailor clauses and specific wording before downloading.
5. **Multi-Format Document Export**:
   - **.TXT**: Clean UTF-8 plain text document.
   - **.DOCX**: Formatted Microsoft Word document with embedded branding, Times New Roman typography, and signature sections.
   - **.PDF**: Branded PDF with centered company logo, styled headings, and multi-page footers.

---

## 📁 Project Architecture

```
LEGALEASE
├── ai_core/
│   ├── __init__.py
│   ├── gemini_generator.py      # Google Gemini API integration
│   └── generator.py             # PDF, DOCX, TXT formatting & sanitization
├── docs/                        # Project documentation & sample exports
├── frontend/
│   └── app.py                   # Streamlit web user interface
├── image/
│   ├── Logo.png                 # App logo
│   ├── inverseLogo.png          # Inverse print logo
│   └── generate_logos.py        # Asset generation script
├── legalEaseAPI/
│   ├── __init__.py
│   ├── main.py                  # FastAPI initialization & server
│   └── routes.py                # POST /generate endpoint & request models
├── .env                         # API keys & environment variables
├── .env.example                 # Environment configuration template
├── config.py                    # Centralized settings & asset paths
├── requirements.txt             # Python dependencies
├── run.bat                      # Windows one-click start launcher
└── run.sh                       # Linux / Mac launcher
```

---

## 🛠️ Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Gemini API Key
Create or edit `.env` in the root folder:
```env
GEMINI_API_KEY=your_google_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

---

## ⚡ Running the Application

### Option A: One-Click Launcher (Windows)
Double-click `run.bat` or run:
```cmd
run.bat
```

### Option B: Manual Execution

1. **Start the FastAPI Backend**:
   ```bash
   py -3.13 -m uvicorn legalEaseAPI.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   *Swagger API Documentation available at: [http://localhost:8000/docs](http://localhost:8000/docs)*

2. **Start the Streamlit Frontend**:
   ```bash
   py -3.13 -m streamlit run frontend/app.py
   ```
   *Web application opens automatically at: [http://localhost:8501](http://localhost:8501)*
