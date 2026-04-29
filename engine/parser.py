import re

import fitz
import spacy


try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None


KNOWN_LOCATIONS = {
    "mysore", "mysuru", "bangalore", "bengaluru", "chennai", "hyderabad",
    "pune", "mumbai", "delhi", "new delhi", "gurgaon", "gurugram", "noida",
    "kolkata", "ahmedabad", "jaipur", "kochi", "cochin", "trivandrum",
    "thiruvananthapuram", "mangalore", "mangaluru", "hubli", "dharwad",
    "karnataka", "maharashtra", "tamil nadu", "telangana", "kerala",
    "uttar pradesh", "gujarat", "rajasthan", "india", "usa", "united states",
    "united kingdom", "uk", "canada", "australia", "san francisco",
    "los angeles", "new york", "seattle", "austin", "boston", "chicago",
    "california", "ca", "texas", "tx", "washington", "wa"
}

TITLE_PATTERNS = [
    "Frontend Developer", "Front End Developer", "Backend Developer",
    "Full Stack Developer", "Software Engineer", "Data Scientist",
    "Machine Learning Engineer", "ML Engineer", "Data Analyst",
    "DevOps Engineer", "Product Manager", "UI Developer", "React Developer",
    "Python Developer", "AI Engineer", "Business Analyst"
]

SECTION_HEADERS = {
    "summary", "profile", "objective", "experience", "work experience",
    "education", "projects", "academic projects", "skills", "technical skills",
    "certifications", "achievements", "contact"
}

LOCATION_RE = re.compile(
    r"\b(" + "|".join(re.escape(loc) for loc in sorted(KNOWN_LOCATIONS, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        return "\n".join(page.get_text("text") for page in doc)
    except Exception:
        return ""


def clean_text(text):
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def clean_name_candidate(name):
    name = name.splitlines()[0] if name else ""
    name = re.sub(r"\S+@\S+|https?://\S+|www\.\S+|\+?\d[\d\s().-]{7,}", " ", name)
    name = re.split(r"\s+[|/]\s+|,", name)[0]
    return re.sub(r"\s+", " ", name).strip(" -|/,")


def title_case_location(value):
    return " ".join(part.capitalize() for part in re.sub(r"\s+", " ", value).strip().split())


def extract_known_locations(text):
    seen = []
    for match in LOCATION_RE.finditer(text):
        loc = title_case_location(match.group(0))
        if loc.lower() not in {item.lower() for item in seen}:
            seen.append(loc)
    return seen


def extract_ner_entities(text):
    people = []
    locations = []
    if not nlp:
        return people, locations

    doc = nlp(text[:1200])
    for ent in doc.ents:
        clean_ent = re.sub(r"\s+", " ", ent.text).strip()
        if ent.label_ == "PERSON":
            people.append(clean_ent)
        elif ent.label_ in {"GPE", "LOC"}:
            locations.append(clean_ent)
    return people, locations


def remove_locations_from_name(name, locations):
    result = clean_name_candidate(name)
    for loc in sorted(locations, key=len, reverse=True):
        result = re.sub(rf"\b{re.escape(loc)}\b", " ", result, flags=re.IGNORECASE)
    result = LOCATION_RE.sub(" ", result)
    return re.sub(r"\s+", " ", result).strip(" -|/,")


def looks_like_name(value):
    words = value.split()
    if not (2 <= len(words) <= 5):
        return False
    if value.lower().strip(":") in SECTION_HEADERS:
        return False
    if any(token in value.lower() for token in ("@", "http", "linkedin", "github")):
        return False
    return all(re.search(r"[A-Za-z]", word) for word in words)


def fallback_name_from_header(text, locations):
    for line in text.splitlines()[:10]:
        candidate = remove_locations_from_name(line, locations)
        if looks_like_name(candidate):
            return candidate
    return ""


def extract_title(text):
    for line in text.splitlines()[:16]:
        for title in TITLE_PATTERNS:
            if re.search(rf"\b{re.escape(title)}\b", line, re.IGNORECASE):
                return title
    for title in TITLE_PATTERNS:
        if re.search(rf"\b{re.escape(title)}\b", text, re.IGNORECASE):
            return title
    return ""


def extract_name_and_location(text):
    known_locations = extract_known_locations(text[:1500])
    ner_people, ner_locations = extract_ner_entities(text)
    all_locations = known_locations + [
        title_case_location(loc) for loc in ner_locations
        if loc.lower() not in {item.lower() for item in known_locations}
    ]

    name = fallback_name_from_header(text, all_locations)
    for person in ner_people:
        if name:
            break
        candidate = remove_locations_from_name(person, all_locations)
        if looks_like_name(candidate):
            name = candidate
            break

    return name or "Unknown Candidate", all_locations[0] if all_locations else ""


def parse_resume(text):
    text = clean_text(text)
    name, location = extract_name_and_location(text)
    title = extract_title(text)

    return {
        "name": name,
        "location": location,
        "title": title,
        "sections": {
            "skills": text,
            "projects": text,
        },
        "raw_text": text,
    }
