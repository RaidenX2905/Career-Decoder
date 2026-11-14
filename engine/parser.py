import re
import warnings

warnings.filterwarnings("ignore")

# Delegate directly to our unified document_parser
from engine.document_parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_text,
    parse_contact_info,
    parse_candidate_name,
    parse_job_title,
    detect_sections,
    parse_resume_document,
)

def parse_resume(text: str) -> dict:
    """Backward compatibility wrapper around parse_resume_document"""
    contact = parse_contact_info(text)
    name = parse_candidate_name(text, contact)
    title = parse_job_title(text)
    sections = detect_sections(text)
    return {
        "name": name,
        "title": title,
        "location": contact.get("location", ""),
        "contact": contact,
        "sections": sections,
        "raw_text": text,
    }
