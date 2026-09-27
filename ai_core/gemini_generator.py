import os
import config

class GeminiDocumentGenerator:
    """
    Core AI Generator using Google GenAI / Google Generative AI (Gemini 2.5 Flash / 1.5 Pro)
    to draft structured, professional legal documents.
    """
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or config.GEMINI_MODEL_NAME or "gemini-2.5-flash"
        self.client = None
        self.legacy_model = None
        self._init_model()

    def _init_model(self):
        if self.api_key:
            # 1. Try modern google-genai SDK first
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                return
            except Exception:
                self.client = None

            # 2. Try google.generativeai fallback
            try:
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=self.api_key)
                self.legacy_model = legacy_genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=(
                        "You are an expert legal counsel and document drafting AI for LegalEase. "
                        "Draft formal, legally sound, and comprehensive legal documents following standard legal formatting. "
                        "Structure the document with clear titles, recitals (WITNESSETH), defined parties, numbered clauses, "
                        "standard boilerplate (Severability, Governing Law, Entire Agreement), and formal signature execution blocks."
                    )
                )
            except Exception:
                self.legacy_model = None

    def generate_document(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        current_key = os.getenv("GEMINI_API_KEY", self.api_key)
        if current_key and not self.client and not self.legacy_model:
            self.api_key = current_key
            self._init_model()

        prompt = (
            f"Generate a comprehensive legal document titled '{document_type}'\n\n"
            f"Involved parties: {parties}\n"
            f"Effective Date: {dates}\n"
            f"Terms and conditions: {terms}\n\n"
            "Ensure formal legal structure with multiple numbered sections and legal clauses, including:\n"
            "1. Title and Preamble with Parties\n"
            "2. Recitals / WITNESSETH\n"
            "3. Core Operational Terms & Obligations\n"
            "4. Payment / Consideration (if applicable)\n"
            "5. Term and Termination\n"
            "6. Confidentiality and Intellectual Property Rights\n"
            "7. Governing Law and Dispute Resolution\n"
            "8. Severability & Entire Agreement\n"
            "9. Execution & Formal Signature Blocks with date lines for all parties.\n"
            "Do not include conversational preamble or markdown code fences like ```markdown. Return only the clean legal text."
        )

        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text.strip()
            except Exception:
                try:
                    response = self.client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=prompt
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception:
                    pass

        if self.legacy_model:
            try:
                response = self.legacy_model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception:
                pass
        
        return self._generate_template_fallback(document_type, parties, terms, dates)

    def _generate_template_fallback(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        doc_title = document_type.strip() if document_type else "Legal Agreement"
        eff_date = dates.strip() if dates else "the date of execution"
        
        parties_list = [p.strip() for p in parties.split(",") if p.strip()] if parties else ["Party A", "Party B"]
        if len(parties_list) < 2:
            parties_list = [parties.strip(), "the Counterparty"] if parties.strip() else ["Party A", "Party B"]

        party_1 = parties_list[0]
        party_2 = parties_list[1] if len(parties_list) > 1 else "Second Party"

        terms_items = [t.strip() for t in terms.split(";") if t.strip()] if terms else [
            "The parties agree to perform the services and obligations described herein faithfully.",
            "All terms, specifications, and milestones must be mutually agreed in writing.",
            "Payment shall be made within 30 days of receipt of a valid invoice.",
            "Confidentiality must be maintained at all times regarding proprietary data.",
            "Either party may terminate this agreement with 15 days written notice."
        ]

        formatted_terms = ""
        for i, term in enumerate(terms_items, start=1):
            formatted_terms += f"{i}. **Obligation & Term {i}:**\n{term}\n\n"

        template = f"""## {doc_title}

Agreement made this {eff_date}.

**Between:**
{party_1} (hereinafter referred to as the "First Party"),

**And:**
{party_2} (hereinafter referred to as the "Second Party").

### WITNESSETH:
WHEREAS, the parties desire to enter into this {doc_title} to define their respective rights, duties, and covenants; and
WHEREAS, the parties have agreed to the terms and conditions hereinafter set forth;

NOW, THEREFORE, in consideration of the mutual covenants and promises contained herein, the parties agree as follows:

### 1. Scope and Core Terms:
{formatted_terms}
### 2. Term and Termination:
This Agreement shall commence on the Effective Date ({eff_date}) and shall continue in full force and effect until terminated by either party upon fifteen (15) days prior written notice, or upon completion of all obligations specified herein.

### 3. Confidentiality:
Each party agrees that all confidential information disclosed by one party to the other shall be treated with the highest degree of care, shall not be disclosed to any third party without prior written consent, and shall be used solely for the purposes of this Agreement.

### 4. Intellectual Property Rights:
Unless otherwise agreed in writing, all work product, intellectual property, and deliverables created under this Agreement shall be the exclusive property of the commissioning party upon full settlement of consideration.

### 5. Governing Law:
This Agreement shall be governed by, and construed in accordance with, the laws of the jurisdiction agreed upon by the parties.

### 6. Severability & Entire Agreement:
If any provision of this Agreement is held to be invalid or unenforceable, the remaining provisions shall continue in full force and effect. This document represents the entire understanding between the parties and supersedes all prior agreements.

### IN WITNESS WHEREOF:
The parties hereto have executed this {doc_title} as of the Effective Date written above.

___________________________________
**{party_1}**
Authorized Signature & Date:

___________________________________
**{party_2}**
Authorized Signature & Date:
"""
        return template.strip()

