import io
import re
import os
import html
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF
import config

def sanitize_text(text: str) -> str:
    """
    Removes unsupported characters, cleans typographic quotes, and standardizes whitespace.
    Ensures safe encoding for PDF and DOCX generation.
    """
    if not text:
        return ""
    
    replacements = {
        '“': '"',
        '”': '"',
        '‘': "'",
        '’': "'",
        '—': "-",
        '–': "-",
        '…': "...",
        '•': "*",
        '\r\n': '\n',
        '\r': '\n',
        '\u200b': '',
        '\xa0': ' ',
    }
    
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)
        
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

class LegalEasePDF(FPDF):
    """
    Custom branded FPDF class for LegalEase documents
    """
    def __init__(self, doc_type: str = "Legal Document"):
        super().__init__()
        self.doc_type = doc_type
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        logo_path = config.INVERSE_LOGO_PATH if config.INVERSE_LOGO_PATH.exists() else config.LOGO_PATH
        if logo_path.exists():
            try:
                self.image(str(logo_path), x=65, y=10, w=80)
                self.ln(22)
            except Exception:
                self.set_font("Helvetica", "B", 16)
                self.set_text_color(15, 23, 42)
                self.cell(0, 10, "LegalEase", ln=True, align="C")
                self.ln(5)
        else:
            self.set_font("Helvetica", "B", 16)
            self.set_text_color(15, 23, 42)
            self.cell(0, 10, "LegalEase", ln=True, align="C")
            self.ln(5)

    def footer(self):
        self.set_y(-18)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        footer_text = f"{config.COMPANY_FOOTER}   |   Page {self.page_no()}/{{nb}}"
        self.cell(0, 10, footer_text, align="C")

def format_pdf(text: str, doc_type: str = "Legal Document") -> bytes:
    clean_text = sanitize_text(text)
    
    pdf = LegalEasePDF(doc_type=doc_type)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, doc_type.strip(), ln=True, align="C")
    pdf.ln(4)
    
    pdf.set_draw_color(203, 213, 225)
    pdf.set_line_width(0.5)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    lines = clean_text.split("\n")
    for line in lines:
        line_str = line.strip()
        if not line_str:
            pdf.ln(3)
            continue
        
        if line_str.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(30, 41, 59)
            heading_content = line_str.replace("### ", "").strip()
            pdf.multi_cell(0, 6, heading_content)
            pdf.ln(2)
        elif line_str.startswith("## ") or line_str.startswith("# "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(15, 23, 42)
            heading_content = line_str.lstrip("#").strip()
            pdf.multi_cell(0, 7, heading_content)
            pdf.ln(2)
        elif re.match(r'^\d+\.\s+[A-Z]', line_str) or (line_str.isupper() and len(line_str) < 50):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(15, 23, 42)
            pdf.multi_cell(0, 6, line_str)
            pdf.ln(1)
        elif line_str.startswith("* ") or line_str.startswith("- ") or line_str.startswith("• "):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 41, 59)
            bullet_text = "   •  " + line_str.lstrip("*-• ").strip()
            pdf.multi_cell(0, 5, bullet_text)
            pdf.ln(1)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 41, 59)
            plain_line = re.sub(r'\*\*(.*?)\*\*', r'\1', line_str)
            pdf.multi_cell(0, 5.5, plain_line)
            pdf.ln(1.5)
            
    return bytes(pdf.output())

def format_docx(text: str, doc_type: str = "Legal Document", terms: str = "") -> bytes:
    clean_text = sanitize_text(text)
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        f_run = f_p.add_run(config.COMPANY_FOOTER)
        f_run.font.name = "Times New Roman"
        f_run.font.size = Pt(8.5)
        f_run.font.color.rgb = RGBColor(100, 116, 139)

    logo_path = config.INVERSE_LOGO_PATH if config.INVERSE_LOGO_PATH.exists() else config.LOGO_PATH
    if logo_path.exists():
        try:
            p_logo = doc.add_paragraph()
            p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_logo = p_logo.add_run()
            run_logo.add_picture(str(logo_path), width=Inches(2.5))
        except Exception:
            pass

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(12)
    run_title = p_title.add_run(doc_type.upper())
    run_title.bold = True
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(16)
    run_title.font.color.rgb = RGBColor(15, 23, 42)

    lines = clean_text.split("\n")
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        
        if line_str.startswith("# ") or line_str.startswith("## "):
            h_text = line_str.lstrip("#").strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(h_text)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(12.5)
            run.font.color.rgb = RGBColor(15, 23, 42)
        elif line_str.startswith("### "):
            h_text = line_str.replace("### ", "").strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            run = p.add_run(h_text)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
            run.font.color.rgb = RGBColor(30, 41, 59)
        elif re.match(r'^\d+\.\s+[A-Z]', line_str) or (line_str.isupper() and len(line_str) < 50):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)
            run = p.add_run(line_str)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(11.5)
        elif line_str.startswith("* ") or line_str.startswith("- ") or line_str.startswith("• "):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2)
            bullet_body = line_str.lstrip("*-• ").strip()
            plain_body = re.sub(r'\*\*(.*?)\*\*', r'\1', bullet_body)
            run = p.add_run(plain_body)
            run.font.name = "Times New Roman"
            run.font.size = Pt(10.5)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.line_spacing = 1.15
            parts = re.split(r'(\*\*.*?\*\*)', line_str)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    run = p.add_run(part[2:-2])
                    run.bold = True
                else:
                    run = p.add_run(part)
                run.font.name = "Times New Roman"
                run.font.size = Pt(10.5)
                run.font.color.rgb = RGBColor(30, 41, 59)

    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    return doc_io.getvalue()

def format_html_preview(text: str) -> str:
    if not text:
        return ""
    
    clean_text = sanitize_text(text)
    lines = clean_text.split("\n")
    html_parts = []
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            html_parts.append("<div style='margin-bottom: 8px;'></div>")
            continue
        
        escaped = html.escape(line_str)
        escaped = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #F8FAFC;">\1</strong>', escaped)
        
        if line_str.startswith("# ") or line_str.startswith("## "):
            content = re.sub(r'^#+\s*', '', escaped)
            html_parts.append(
                f"<h3 style='color: #38BDF8; margin-top: 18px; margin-bottom: 8px; font-weight: 700; "
                f"border-bottom: 1px solid #334155; padding-bottom: 4px;'>{content}</h3>"
            )
        elif line_str.startswith("### "):
            content = re.sub(r'^#+\s*', '', escaped)
            html_parts.append(
                f"<h4 style='color: #93C5FD; margin-top: 14px; margin-bottom: 6px; font-weight: 600;'>{content}</h4>"
            )
        elif re.match(r'^\d+\.\s+[A-Z]', line_str) or (line_str.isupper() and len(line_str) < 50):
            html_parts.append(
                f"<h4 style='color: #E2E8F0; margin-top: 12px; margin-bottom: 4px; font-weight: 600;'>{escaped}</h4>"
            )
        elif line_str.startswith("* ") or line_str.startswith("- ") or line_str.startswith("• "):
            bullet_body = re.sub(r'^[\*\-•]\s*', '', escaped)
            html_parts.append(
                f"<li style='margin-left: 20px; color: #CBD5E1; line-height: 1.6;'>{bullet_body}</li>"
            )
        else:
            html_parts.append(
                f"<p style='color: #CBD5E1; line-height: 1.6; margin-bottom: 6px;'>{escaped}</p>"
            )
            
    return "\n".join(html_parts)
