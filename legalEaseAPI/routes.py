from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter()
gemini_generator = GeminiDocumentGenerator()

class DocumentRequest(BaseModel):
    document_type: str = Field(..., example="Freelance Work Contract", description="Type of legal document")
    parties: str = Field(..., example="Jane Doe (Service Provider), TechNova Inc. (Client)", description="Parties involved")
    terms: str = Field(..., example="Payment to be made within 30 days of invoice; Confidentiality must be maintained", description="Semicolon separated terms")
    dates: str = Field(..., example="April 15, 2025", description="Effective date")

@router.post("/generate")
def generate_legal_document(request: DocumentRequest):
    """
    Receives legal document parameters, prompts the Gemini AI model,
    and returns structured legal document text.
    """
    try:
        response = gemini_generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates
        )
        return {"document": response, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")

@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "LegalEase API"}
