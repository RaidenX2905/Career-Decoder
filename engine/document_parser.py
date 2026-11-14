import io
import re
import warnings

warnings.filterwarnings("ignore")

try:
    import fitz
except ImportError:
    import pymupdf as fitz

try:
    import docx
except ImportError:
    docx = None


SECTION_HEADERS = {
    "summary": ["summary", "professional summary", "about me", "profile", "career objective", "objective"],
    "experience": ["experience", "work experience", "employment history", "professional experience", "work history", "internships"],
    "skills": ["skills", "technical skills", "core competencies", "technologies", "tools", "technical proficiency"],
    "projects": ["projects", "personal projects", "academic projects", "key projects", "notable projects"],
    "education": ["education", "academic background", "educational qualifications", "academics"],
    "certifications": ["certifications", "certificates", "licenses", "courses", "credentials"],
    "achievements": ["achievements", "honors", "awards", "publications", "extracurricular"]
}

KNOWN_LOCATIONS = {
    "mysore", "mysuru", "bangalore", "bengaluru", "chennai", "hyderabad",
    "pune", "mumbai", "delhi", "new delhi", "gurgaon", "gurugram", "noida",
    "kolkata", "ahmedabad", "jaipur", "kochi", "cochin", "trivandrum",
    "thiruvananthapuram", "mangalore", "mangaluru", "hubli", "dharwad",
    "karnataka", "maharashtra", "tamil nadu", "telangana", "kerala",
    "uttar pradesh", "gujarat", "rajasthan", "india", "usa", "united states",
    "united kingdom", "uk", "canada", "australia", "san francisco",
    "los angeles", "new york", "seattle", "austin", "boston", "chicago",
    "california", "ca", "texas", "tx", "washington", "wa", "berlin",
    "london", "singapore", "toronto", "vancouver"
}

TITLE_PATTERNS = [
    "AI Engineer", "GenAI Engineer", "Machine Learning Engineer", "ML Engineer",
    "Data Scientist", "Data Analyst", "Data Engineer", "Backend Developer",
    "Frontend Developer", "Full Stack Developer", "DevOps Engineer",
    "Cloud Engineer", "Site Reliability Engineer", "SRE", "Cybersecurity Engineer",
    "Software Engineer", "Product Manager", "QA Automation Engineer",
    "Mobile Developer", "iOS Developer", "Android Developer"
]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        return "\n".join(page.get_text("text") for page in doc)
    except Exception:
        return ""


def extract_text_from_docx(file_bytes: bytes) -> str:
    if not docx:
        return ""
    try:
        doc_file = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc_file.paragraphs if p.text.strip()]
        for table in doc_file.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)
        return "\n".join(paragraphs)
    except Exception:
        return ""


def clean_text(text: str) -> str:
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def parse_contact_info(text: str):
    emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    phones = re.findall(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    linkedin = re.findall(r"linkedin\.com/in/[\w-]+", text, re.IGNORECASE)
    github = re.findall(r"github\.com/[\w-]+", text, re.IGNORECASE)

    # Location resolution
    found_loc = ""
    for loc in sorted(KNOWN_LOCATIONS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(loc)}\b", text[:1200], re.IGNORECASE):
            found_loc = " ".join(part.capitalize() for part in loc.split())
            break

    return {
        "email": emails[0] if emails else "",
        "phone": phones[0] if phones else "",
        "linkedin": linkedin[0] if linkedin else "",
        "github": github[0] if github else "",
        "location": found_loc,
    }


def parse_candidate_name(text: str, contact: dict):
    lines = text.splitlines()[:6]
    for line in lines:
        clean = line.strip(" -*|•,")
        if not clean or len(clean.split()) < 2 or len(clean.split()) > 4:
            continue
        # Avoid section headers or contact lines
        if any(h in clean.lower() for headers in SECTION_HEADERS.values() for h in headers):
            continue
        if "@" in clean or "http" in clean or "phone" in clean.lower() or "resume" in clean.lower():
            continue
        if all(re.search(r"^[A-Za-z.'-]+$", word) for word in clean.split()):
            return clean
    return "Candidate Profile"


def parse_job_title(text: str):
    for line in text.splitlines()[:12]:
        for pattern in TITLE_PATTERNS:
            if re.search(rf"\b{re.escape(pattern)}\b", line, re.IGNORECASE):
                return pattern
    for pattern in TITLE_PATTERNS:
        if re.search(rf"\b{re.escape(pattern)}\b", text[:1000], re.IGNORECASE):
            return pattern
    return "Software Professional"


def detect_sections(text: str):
    """
    Deterministic state machine for section demarcation.
    """
    sections = {}
    current_section = "header"
    sections[current_section] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        clean = re.sub(r"[^A-Za-z ]", "", line).strip().lower()
        matched_section = None

        for canonical, aliases in SECTION_HEADERS.items():
            if clean in aliases:
                matched_section = canonical
                break

        if matched_section:
            current_section = matched_section
            sections.setdefault(current_section, [])
            continue

        sections.setdefault(current_section, []).append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


def parse_resume_document(file_bytes: bytes, filename: str):
    fname_lower = filename.lower()
    if fname_lower.endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_bytes)
        format_type = "PDF"
    elif fname_lower.endswith(".docx"):
        raw_text = extract_text_from_docx(file_bytes)
        format_type = "DOCX"
    else:
        raw_text = file_bytes.decode("utf-8", errors="ignore")
        format_type = "TXT"

    raw_text = clean_text(raw_text)
    contact = parse_contact_info(raw_text)
    name = parse_candidate_name(raw_text, contact)
    title = parse_job_title(raw_text)
    sections = detect_sections(raw_text)

    # Validation flags
    validation = {
        "has_contact_info": bool(contact["email"] or contact["phone"]),
        "has_experience_section": "experience" in sections,
        "has_skills_section": "skills" in sections,
        "has_projects_section": "projects" in sections,
        "has_education_section": "education" in sections,
        "detected_sections_count": len([k for k in sections if k != "header"]),
        "character_count": len(raw_text),
        "word_count": len(raw_text.split()),
        "format": format_type,
    }

    return {
        "name": name,
        "title": title,
        "location": contact["location"],
        "contact": contact,
        "sections": sections,
        "raw_text": raw_text,
        "validation": validation,
    }
