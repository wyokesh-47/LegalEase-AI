from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from ai_core.gemini_generator import GeminiDocumentGenerator
from legalEaseAPI.firebase_manager import firebase_manager

router = APIRouter()
gemini_generator = GeminiDocumentGenerator()

class DocumentRequest(BaseModel):
    document_type: str = Field(..., example="Freelance Work Contract", description="Type of legal document")
    parties: str = Field(..., example="Jane Doe (Service Provider), TechNova Inc. (Client)", description="Parties involved")
    terms: str = Field(..., example="Payment to be made within 30 days of invoice; Confidentiality must be maintained", description="Semicolon separated terms")
    dates: str = Field(..., example="April 15, 2025", description="Effective date")
    save_to_firebase: Optional[bool] = Field(default=True, description="Whether to store document in Firebase Firestore")

class SaveDocumentRequest(BaseModel):
    document_type: str
    parties: str
    terms: str
    dates: str
    document_text: str

@router.post("/generate")
def generate_legal_document(request: DocumentRequest):
    """
    Receives legal document parameters, prompts the Gemini AI model,
    and stores generated document in Firebase Firestore if configured.
    """
    try:
        response = gemini_generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates
        )
        
        firebase_result = None
        if request.save_to_firebase and firebase_manager.is_configured:
            firebase_result = firebase_manager.save_document(
                document_type=request.document_type,
                parties=request.parties,
                terms=request.terms,
                dates=request.dates,
                document_text=response
            )

        return {
            "document": response,
            "status": "success",
            "firebase": firebase_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")

@router.get("/documents")
def get_saved_documents(limit: int = Query(20, ge=1, le=100)):
    """
    Retrieves history of legal documents saved in Firebase Firestore.
    """
    if not firebase_manager.is_configured:
        return {"documents": [], "status": "firebase_not_configured"}
    
    docs = firebase_manager.get_documents(limit=limit)
    return {"documents": docs, "status": "success"}

@router.post("/documents/save")
def save_custom_document(request: SaveDocumentRequest):
    """
    Saves or updates custom edited document text into Firebase Firestore.
    """
    result = firebase_manager.save_document(
        document_type=request.document_type,
        parties=request.parties,
        terms=request.terms,
        dates=request.dates,
        document_text=request.document_text
    )
    return result

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "LegalEase API",
        "firebase_connected": firebase_manager.is_configured
    }
