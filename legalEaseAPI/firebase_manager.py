import os
import json
import time
import requests
from typing import List, Dict, Any, Optional
import config

class FirebaseManager:
    """
    Manages Firebase Firestore database operations (Save documents, list history, fetch docs)
    using Firestore REST API safely.
    """
    def __init__(self):
        self.api_key = config.FIREBASE_API_KEY
        self.project_id = config.FIREBASE_PROJECT_ID
        self.collection_name = "legal_documents"

    @property
    def is_configured(self) -> bool:
        """Checks if valid Firebase project credentials are provided."""
        return bool(self.api_key and self.project_id and self.api_key != "" and self.project_id != "")

    def save_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
        document_text: str
    ) -> Dict[str, Any]:
        """
        Saves a generated legal document record to Firebase Firestore.
        """
        if not self.is_configured:
            return {"status": "skipped", "message": "Firebase credentials not configured"}

        url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/{self.collection_name}?key={self.api_key}"
        
        payload = {
            "fields": {
                "document_type": {"stringValue": str(document_type)},
                "parties": {"stringValue": str(parties)},
                "terms": {"stringValue": str(terms)},
                "dates": {"stringValue": str(dates)},
                "document_text": {"stringValue": str(document_text)},
                "created_at": {"integerValue": str(int(time.time()))},
                "created_date": {"stringValue": time.strftime("%Y-%m-%d %H:%M:%S")}
            }
        }

        try:
            res = requests.post(url, json=payload, timeout=8)
            if res.status_code in [200, 201]:
                doc_data = res.json()
                doc_id = doc_data.get("name", "").split("/")[-1]
                return {
                    "status": "success",
                    "id": doc_id,
                    "message": "Document saved to Firebase Firestore successfully"
                }
            else:
                return {
                    "status": "error",
                    "code": res.status_code,
                    "message": f"Firestore API returned: {res.text}"
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_documents(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetches previously generated legal documents from Firebase Firestore.
        """
        if not self.is_configured:
            return []

        url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/{self.collection_name}?key={self.api_key}&pageSize={limit}"
        
        try:
            res = requests.get(url, timeout=8)
            if res.status_code == 200:
                data = res.json()
                raw_docs = data.get("documents", [])
                documents = []
                for d in raw_docs:
                    name = d.get("name", "")
                    doc_id = name.split("/")[-1]
                    fields = d.get("fields", {})
                    documents.append({
                        "id": doc_id,
                        "document_type": fields.get("document_type", {}).get("stringValue", "Untitled"),
                        "parties": fields.get("parties", {}).get("stringValue", ""),
                        "terms": fields.get("terms", {}).get("stringValue", ""),
                        "dates": fields.get("dates", {}).get("stringValue", ""),
                        "document_text": fields.get("document_text", {}).get("stringValue", ""),
                        "created_date": fields.get("created_date", {}).get("stringValue", "")
                    })
                return documents
            return []
        except Exception as e:
            print(f"Error fetching from Firebase: {e}")
            return []

firebase_manager = FirebaseManager()
