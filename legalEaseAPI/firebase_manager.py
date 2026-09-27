import os
import json
import time
import requests
from typing import List, Dict, Any, Optional
import config

class FirebaseManager:
    """
    Manages Firebase database operations (Firestore REST API & Realtime Database)
    with automatic multi-service fallback.
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
        Saves a generated legal document record to Firebase (Firestore or Realtime Database).
        """
        if not self.is_configured:
            return {"status": "skipped", "message": "Firebase credentials not configured"}

        # 1. Try Firestore REST API
        firestore_url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/{self.collection_name}?key={self.api_key}"
        firestore_payload = {
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
            res = requests.post(firestore_url, json=firestore_payload, timeout=8)
            if res.status_code in [200, 201]:
                doc_data = res.json()
                doc_id = doc_data.get("name", "").split("/")[-1]
                return {
                    "status": "success",
                    "database": "firestore",
                    "id": doc_id,
                    "message": "Document saved to Firebase Firestore successfully"
                }
        except Exception:
            pass

        # 2. Try Firebase Realtime Database
        rtdb_urls = [
            f"https://{self.project_id}-default-rtdb.firebaseio.com/{self.collection_name}.json?auth={self.api_key}",
            f"https://{self.project_id}.firebaseio.com/{self.collection_name}.json?auth={self.api_key}"
        ]
        
        rtdb_payload = {
            "document_type": str(document_type),
            "parties": str(parties),
            "terms": str(terms),
            "dates": str(dates),
            "document_text": str(document_text),
            "created_at": int(time.time()),
            "created_date": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        for r_url in rtdb_urls:
            try:
                r_res = requests.post(r_url, json=rtdb_payload, timeout=5)
                if r_res.status_code in [200, 201]:
                    r_id = r_res.json().get("name", "saved")
                    return {
                        "status": "success",
                        "database": "realtime_database",
                        "id": r_id,
                        "message": "Document saved to Firebase Realtime Database successfully"
                    }
            except Exception:
                continue

        return {
            "status": "pending_rules",
            "message": "Firebase connected, but Firestore Security Rules require enabling 'Test Mode' in Firebase Console."
        }

    def get_documents(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetches previously generated legal documents from Firebase Firestore or RTDB.
        """
        if not self.is_configured:
            return []

        # Try Firestore
        url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/{self.collection_name}?key={self.api_key}&pageSize={limit}"
        try:
            res = requests.get(url, timeout=6)
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
        except Exception:
            pass

        return []

firebase_manager = FirebaseManager()
