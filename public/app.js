// Import Firebase SDK modules
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getFirestore, collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// Firebase Configuration from your project
const firebaseConfig = {
  apiKey: "AIzaSyD06j-Zi0iqpSVEx941ZC148IZTOjSPbR8",
  authDomain: "legalease-ai-3486c.firebaseapp.com",
  projectId: "legalease-ai-3486c",
  storageBucket: "legalease-ai-3486c.firebasestorage.app",
  messagingSenderId: "208353491643",
  appId: "1:208353491643:web:164390acf14c512978c79e",
  measurementId: "G-V8W545KPZZ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// DOM Elements
const docTypeInput = document.getElementById("docType");
const partiesInput = document.getElementById("parties");
const termsInput = document.getElementById("terms");
const datesInput = document.getElementById("dates");
const generateBtn = document.getElementById("generateBtn");
const btnText = document.getElementById("btnText");
const outputSection = document.getElementById("outputSection");
const previewCard = document.getElementById("previewCard");
const toggleEditBtn = document.getElementById("toggleEditBtn");
const editorContainer = document.getElementById("editorContainer");
const docEditor = document.getElementById("docEditor");
const downloadTxtBtn = document.getElementById("downloadTxtBtn");
const downloadDocxBtn = document.getElementById("downloadDocxBtn");
const downloadPdfBtn = document.getElementById("downloadPdfBtn");

let generatedDocumentText = "";
let currentDocId = null;

// Template Generator Fallback
function generateLegalTemplate(docType, parties, terms, dates) {
  const title = docType.trim() || "Freelance Work Contract";
  const dateStr = dates.trim() || "April 15, 2025";
  
  let p1 = "Jane Doe (Service Provider)";
  let p2 = "TechNova Inc. (Client)";
  if (parties.includes(",")) {
    const parts = parties.split(",");
    p1 = parts[0].trim();
    p2 = parts[1].trim();
  } else if (parties.trim()) {
    p1 = parties.trim();
  }

  const rawTerms = terms.split(";").map(t => t.trim()).filter(t => t.length > 0);
  let termsList = "";
  rawTerms.forEach((term, idx) => {
    termsList += `${idx + 1}. **Obligation & Clause ${idx + 1}:**\n${term}\n\n`;
  });

  return `## ${title}

Agreement made this ${dateStr}.

**Between:**
${p1} (hereinafter referred to as the "First Party"),

**And:**
${p2} (hereinafter referred to as the "Second Party").

### WITNESSETH:
WHEREAS, the parties desire to enter into this ${title} to define their respective rights, duties, and covenants; and
WHEREAS, the parties have agreed to the terms and conditions hereinafter set forth;

NOW, THEREFORE, in consideration of the mutual covenants and promises contained herein, the parties agree as follows:

### 1. Scope and Core Terms:
${termsList}
### 2. Term and Termination:
This Agreement shall commence on the Effective Date (${dateStr}) and shall continue in full force and effect until terminated by either party upon fifteen (15) days prior written notice, or upon completion of all obligations specified herein.

### 3. Confidentiality:
Each party agrees that all confidential information disclosed by one party to the other shall be treated with the highest degree of care, shall not be disclosed to any third party without prior written consent, and shall be used solely for the purposes of this Agreement.

### 4. Intellectual Property Rights:
Unless otherwise agreed in writing, all work product, intellectual property, and deliverables created under this Agreement shall be the exclusive property of the commissioning party upon full settlement of consideration.

### 5. Governing Law:
This Agreement shall be governed by, and construed in accordance with, the laws of the jurisdiction agreed upon by the parties.

### 6. Severability & Entire Agreement:
If any provision of this Agreement is held to be invalid or unenforceable, the remaining provisions shall continue in full force and effect. This document represents the entire understanding between the parties and supersedes all prior agreements.

### IN WITNESS WHEREOF:
The parties hereto have executed this ${title} as of the Effective Date written above.

___________________________________
**${p1}**
Authorized Signature & Date:

___________________________________
**${p2}**
Authorized Signature & Date:`;
}

// Convert markdown to styled HTML for preview
function formatHtmlPreview(text) {
  const lines = text.split("\n");
  let html = "";
  
  lines.forEach(line => {
    const trimmed = line.trim();
    if (!trimmed) {
      html += "<div style='margin-bottom: 6px;'></div>";
      return;
    }

    let parsed = trimmed.replace(/\*\*(.*?)\*\*/g, "<strong style='color: #F8FAFC;'>$1</strong>");

    if (trimmed.startsWith("## ")) {
      html += `<h2 style='color: #38BDF8; margin-top: 14px; margin-bottom: 8px;'>${parsed.replace('## ', '')}</h2>`;
    } else if (trimmed.startsWith("### ")) {
      html += `<h3 style='color: #93C5FD; margin-top: 12px; margin-bottom: 6px;'>${parsed.replace('### ', '')}</h3>`;
    } else if (/^\d+\.\s+[A-Z]/.test(trimmed)) {
      html += `<h4 style='color: #E2E8F0; margin-top: 10px; margin-bottom: 4px;'>${parsed}</h4>`;
    } else {
      html += `<p style='color: #CBD5E1; margin-bottom: 6px;'>${parsed}</p>`;
    }
  });

  return html;
}

// Generate Document Action
generateBtn.addEventListener("click", async () => {
  const docType = docTypeInput.value;
  const parties = partiesInput.value;
  const terms = termsInput.value;
  const dates = datesInput.value;

  if (!docType.trim() || !parties.trim()) {
    alert("Please fill in Document Type and Parties Involved.");
    return;
  }

  btnText.innerHTML = `<span class="spinner"></span> Generating...`;
  generateBtn.disabled = true;

  try {
    // Generate text via smart generator or local API
    generatedDocumentText = generateLegalTemplate(docType, parties, terms, dates);

    // Save to Firebase Firestore Cloud
    try {
      const docRef = await addDoc(collection(db, "legal_documents"), {
        document_type: docType,
        parties: parties,
        terms: terms,
        dates: dates,
        document_text: generatedDocumentText,
        created_at: serverTimestamp(),
        created_date: new Date().toLocaleString()
      });
      currentDocId = docRef.id;
      console.log("Document successfully saved to Firebase Firestore with ID:", currentDocId);
    } catch (fbErr) {
      console.warn("Firestore save warning:", fbErr);
    }

    // Display Output
    previewCard.innerHTML = formatHtmlPreview(generatedDocumentText);
    docEditor.value = generatedDocumentText;
    outputSection.style.display = "block";
    outputSection.scrollIntoView({ behavior: "smooth" });

  } catch (err) {
    console.error("Generation error:", err);
  } finally {
    btnText.textContent = "Generate Document";
    generateBtn.disabled = false;
  }
});

// Toggle Editor
toggleEditBtn.addEventListener("click", () => {
  if (editorContainer.style.display === "block") {
    editorContainer.style.display = "none";
    toggleEditBtn.textContent = "🖊️ Click to Edit Document";
  } else {
    editorContainer.style.display = "block";
    toggleEditBtn.textContent = "🖊️ Close Editor";
  }
});

// Editor change sync
docEditor.addEventListener("input", (e) => {
  generatedDocumentText = e.target.value;
  previewCard.innerHTML = formatHtmlPreview(generatedDocumentText);
});

// Download .TXT
downloadTxtBtn.addEventListener("click", () => {
  const safeName = (docTypeInput.value || "legal_document").toLowerCase().replace(/\s+/g, "_");
  const blob = new Blob([generatedDocumentText], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${safeName}.txt`;
  a.click();
  URL.revokeObjectURL(url);
});

// Download .DOCX
downloadDocxBtn.addEventListener("click", () => {
  const safeName = (docTypeInput.value || "legal_document").toLowerCase().replace(/\s+/g, "_");
  const blob = new Blob([generatedDocumentText], { type: "application/msword;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${safeName}.doc`;
  a.click();
  URL.revokeObjectURL(url);
});

// Download .PDF using jsPDF
downloadPdfBtn.addEventListener("click", () => {
  const { jsPDF } = window.jspdf;
  const pdf = new jsPDF({ unit: "pt", format: "letter" });
  const safeName = (docTypeInput.value || "legal_document").toLowerCase().replace(/\s+/g, "_");

  pdf.setFont("Helvetica", "bold");
  pdf.setFontSize(16);
  pdf.setTextColor(15, 23, 42);
  pdf.text(docTypeInput.value.toUpperCase() || "LEGAL AGREEMENT", 306, 50, { align: "center" });

  pdf.setDrawColor(203, 213, 225);
  pdf.line(40, 65, 572, 65);

  pdf.setFont("Helvetica", "normal");
  pdf.setFontSize(10);
  pdf.setTextColor(30, 41, 59);

  const cleanText = generatedDocumentText.replace(/\*\*/g, "");
  const lines = pdf.splitTextToSize(cleanText, 520);
  
  let y = 85;
  lines.forEach(line => {
    if (y > 740) {
      pdf.addPage();
      y = 50;
    }
    pdf.text(line, 40, y);
    y += 14;
  });

  pdf.save(`${safeName}.pdf`);
});
