import os
import sys
from pathlib import Path
import streamlit as st
import requests

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config
from ai_core.generator import sanitize_text, format_docx, format_pdf, format_html_preview

# Milestone 4: Page Configuration and Layout Setup
st.set_page_config(page_title="LegalEase", layout="centered")

# Custom Dark Theme CSS matching the video and project screenshots
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    .preview-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 22px;
        margin-top: 15px;
        margin-bottom: 20px;
        max-height: 480px;
        overflow-y: auto;
        color: #C9D1D9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .stDownloadButton button, .stButton button {
        border-radius: 6px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Step 1: Center-aligned company logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    logo_file = config.LOGO_PATH if config.LOGO_PATH.exists() else config.INVERSE_LOGO_PATH
    if logo_file.exists():
        st.image(str(logo_file), use_container_width=True)

# Step 2: Header and Title
st.markdown(
    "<h2 style='text-align: center; color: #FFFFFF; font-weight: 600; margin-top: -10px;'>AI Legal Document Generator</h2>",
    unsafe_allow_html=True
)

# Initialize Session State
if "generated_text" not in st.session_state:
    st.session_state.generated_text = None
if "show_edit" not in st.session_state:
    st.session_state.show_edit = False
if "current_doc_type" not in st.session_state:
    st.session_state.current_doc_type = "Freelance Work Contract"

# Step 3: User Input Interface
document_type = st.text_input(
    "Document Type (Ex: Agreement, Contract, NDA)",
    placeholder="Freelance Work Contract"
)

parties = st.text_area(
    "Parties Involved",
    placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)",
    height=80
)

terms = st.text_area(
    "Terms & Conditions (Use semicolons for bullet points)",
    placeholder="Work must be delivered by May 15, 2025;\nPayment will be made within 7 days of invoice;\nClient retains intellectual property rights.",
    height=100
)

dates = st.text_input(
    "Effective Date",
    placeholder="April 15, 2025"
)

col_gen, col_info = st.columns([1, 2])
with col_gen:
    generate_btn = st.button("Generate Document", type="primary", use_container_width=True)
with col_info:
    st.caption("ℹ️ Click 'Generate Document' to start")

# Activity 4.2: Creating Dynamic Previews and Export Options
# Step 1: Generate Document with Backend AI
if generate_btn:
    doc_type_val = document_type.strip() if document_type else "Freelance Work Contract"
    parties_val = parties.strip() if parties else "Jane Doe (Service Provider), TechNova Inc. (Client)"
    terms_val = terms.strip()
    dates_val = dates.strip() if dates else "April 15, 2025"

    with st.spinner("Generating document..."):
        try:
            # POST request to FastAPI backend
            response = requests.post(
                f"{config.BACKEND_URL}/generate",
                json={
                    "document_type": doc_type_val,
                    "parties": parties_val,
                    "terms": terms_val,
                    "dates": dates_val
                },
                timeout=60
            )
            if response.status_code == 200:
                raw_text = response.json().get("document", "")
            else:
                raw_text = ""
        except Exception:
            # Direct generation fallback if backend server is not running
            from ai_core.gemini_generator import GeminiDocumentGenerator
            gen = GeminiDocumentGenerator()
            raw_text = gen.generate_document(doc_type_val, parties_val, terms_val, dates_val)

        if raw_text:
            st.session_state.generated_text = sanitize_text(raw_text)
            st.session_state.current_doc_type = doc_type_val
            st.session_state.show_edit = False

# Display Output
if st.session_state.generated_text:
    st.success("✅ Document Generated Successfully!")
    
    # Step 2: HTML Preview Rendering
    styled_html = format_html_preview(st.session_state.generated_text)
    st.markdown(f"<div class='preview-card'>{styled_html}</div>", unsafe_allow_html=True)
    
    # Step 3: Editable Document Preview
    if st.button("🖊️ Click to Edit Document"):
        st.session_state.show_edit = not st.session_state.show_edit
        st.rerun()

    if st.session_state.show_edit:
        st.markdown("##### Edit Document Below:")
        edited_text = st.text_area(
            "Document Editor",
            value=st.session_state.generated_text,
            height=300,
            label_visibility="collapsed"
        )
        if edited_text != st.session_state.generated_text:
            st.session_state.generated_text = edited_text
    
    # Step 4: Multi-Format Download Options
    safe_name = st.session_state.current_doc_type.replace(" ", "_").replace("/", "_").lower()
    if not safe_name:
        safe_name = "legal_document"
        
    doc_text = st.session_state.generated_text
    
    col_d1, col_d2, col_d3 = st.columns(3)
    
    with col_d1:
        st.download_button(
            label="📄 Download as .TXT",
            data=doc_text,
            file_name=f"{safe_name}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
    with col_d2:
        docx_data = format_docx(doc_text, st.session_state.current_doc_type)
        st.download_button(
            label="📝 Download as .DOCX",
            data=docx_data,
            file_name=f"{safe_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
        
    with col_d3:
        pdf_data = format_pdf(doc_text, st.session_state.current_doc_type)
        st.download_button(
            label="📕 Download as .PDF",
            data=pdf_data,
            file_name=f"{safe_name}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
