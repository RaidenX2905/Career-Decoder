import re


TECH_SKILLS = {
    "python": ["python"],
    "java": ["java"],
    "c++": ["c++", "cpp"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "reactjs"],
    "node": ["node", "nodejs", "node.js"],
    "sql": ["sql", "mysql", "postgres", "postgresql"],
    "mongodb": ["mongodb", "mongo"],
    "machine learning": ["machine learning", "ml", "scikit-learn", "sklearn"],
    "deep learning": ["deep learning", "tensorflow", "keras", "pytorch", "lstm"],
    "data analysis": ["data analysis", "eda", "pandas", "numpy"],
    "data visualization": ["matplotlib", "seaborn", "plotly", "power bi", "tableau"],
    "html": ["html"],
    "css": ["css", "tailwind"],
    "git": ["git", "github"],
    "docker": ["docker"],
    "aws": ["aws", "amazon web services"],
    "fastapi": ["fastapi"],
}

SKILL_DISPLAY = {
    "c++": "C++",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "node": "Node.js",
    "sql": "SQL",
    "mongodb": "MongoDB",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "data analysis": "Data Analysis",
    "data visualization": "Data Visualization",
    "html": "HTML",
    "css": "CSS",
    "git": "Git",
    "aws": "AWS",
    "fastapi": "FastAPI",
}

SOFT_SKILLS = [
    "communication",
    "leadership",
    "teamwork",
    "problem solving",
    "critical thinking",
    "collaboration",
    "mentoring",
]

ROLE_SKILLS = {
    "Frontend Developer": ["html", "css", "javascript", "react"],
    "Backend Developer": ["python", "java", "sql", "node", "fastapi"],
    "Full Stack Developer": ["html", "css", "javascript", "react", "node", "sql"],
    "Data Analyst": ["python", "sql", "data analysis", "data visualization"],
    "Data Scientist": ["python", "machine learning", "data analysis", "data visualization"],
    "ML Engineer": ["python", "machine learning", "deep learning", "sql"],
}

LEARNING_MAP = {
    "html": "Build semantic HTML layouts",
    "css": "Practice responsive CSS and layout systems",
    "javascript": "Strengthen modern JavaScript",
    "typescript": "Learn TypeScript fundamentals",
    "react": "Build React projects with state and routing",
    "node": "Build REST APIs with Node.js",
    "fastapi": "Build production APIs with FastAPI",
    "sql": "Practice SQL joins, aggregation, and schema design",
    "java": "Build backend services with Java",
    "python": "Practice Python scripting and data structures",
    "machine learning": "Learn supervised ML workflows",
    "deep learning": "Learn neural networks and model training",
    "data analysis": "Practice EDA with Pandas and NumPy",
    "data visualization": "Build dashboards with visualization libraries",
}

SECTION_ALIASES = {
    "projects": {"projects", "project", "academic projects", "personal projects"},
    "skills": {"skills", "technical skills", "tools", "technologies"},
    "experience": {"experience", "work experience", "employment"},
    "education": {"education", "academics"},
    "summary": {"summary", "profile", "objective"},
    "certifications": {"certifications", "certificates"},
}


def normalize(text):
    return text.lower()


def safe_list(value):
    return value if isinstance(value, list) else []


def safe_dict(value):
    return value if isinstance(value, dict) else {}


def section_name(line):
    clean = re.sub(r"[^A-Za-z ]", "", line).strip().lower()
    for canonical, aliases in SECTION_ALIASES.items():
        if clean in aliases:
            return canonical
    return ""


def split_sections(text):
    sections = {}
    current = "header"
    sections[current] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        detected = section_name(line)
        if detected:
            current = detected
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)

    return {key: "\n".join(value).strip() for key, value in sections.items()}


def clean_bullet(line):
    return line.strip().strip("-*").strip()


def display_skill(skill):
    return SKILL_DISPLAY.get(skill, skill.title())


def extract_skills(text):
    lower = normalize(text)
    tech_found = {}

    for skill, keywords in TECH_SKILLS.items():
        count = 0
        for keyword in keywords:
            count += len(re.findall(rf"\b{re.escape(keyword)}\b", lower))
        if count >= 3:
            tech_found[skill] = "Strong"
        elif count == 2:
            tech_found[skill] = "Intermediate"
        elif count == 1:
            tech_found[skill] = "Basic"

    soft_found = [skill for skill in SOFT_SKILLS if re.search(rf"\b{re.escape(skill)}\b", lower)]

    return {
        "technical": tech_found,
        "soft": soft_found,
    }


def extract_education(text):
    section = split_sections(text).get("education", "")
    if not section:
        return []
    return [clean_bullet(line) for line in section.splitlines() if clean_bullet(line)]


def extract_certifications(text):
    section = split_sections(text).get("certifications", "")
    if not section:
        return []
    return [clean_bullet(line) for line in section.splitlines() if clean_bullet(line)]


def extract_experience(text):
    section = split_sections(text).get("experience", "")
    if not section:
        return []

    entries = []
    current = None
    duration_re = re.compile(
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+\d{4}\s*[-–]\s*(?:present|current|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+\d{4}|\d{4})",
        re.IGNORECASE,
    )

    for raw_line in section.splitlines():
        line = clean_bullet(raw_line)
        if not line:
            continue

        duration_match = duration_re.search(line)
        if "|" in line and not line.startswith("-"):
            role, company = [part.strip() for part in line.split("|", 1)]
            current = {
                "role": role,
                "company": company,
                "duration": "",
                "key_responsibilities": [],
            }
            entries.append(current)
            continue

        if duration_match and current:
            current["duration"] = duration_match.group(0)
            continue

        if current:
            current["key_responsibilities"].append(line)

    return entries


SKILL_LEVEL_WEIGHT = {
    "Basic": 0.45,
    "Intermediate": 0.70,
    "Strong": 1.0,
}


ROLE_EVIDENCE = {
    "Frontend Developer": ["frontend", "front end", "react", "portfolio", "responsive web"],
    "Backend Developer": ["backend", "api", "database", "fastapi", "flask", "server"],
    "Full Stack Developer": ["full stack", "frontend", "backend", "react", "api"],
    "Data Analyst": ["data analyst", "eda", "reporting", "dashboard", "visualization"],
    "Data Scientist": ["data scientist", "machine learning", "model", "regression", "classification"],
    "ML Engineer": ["ml engineer", "machine learning", "model", "pipeline", "tensorflow", "pytorch"],
}


def role_evidence_bonus(role, text):
    lower = normalize(text)
    hits = sum(1 for keyword in ROLE_EVIDENCE.get(role, []) if keyword in lower)
    return min(hits * 4, 12)


def match_roles(skills, text=""):
    results = []
    tech = safe_dict(skills)

    for role, required in ROLE_SKILLS.items():
        matched = [skill for skill in required if skill in tech]
        missing = [skill for skill in required if skill not in tech]
        weighted = sum(SKILL_LEVEL_WEIGHT.get(tech.get(skill, "Basic"), 0.45) for skill in required if skill in tech)
        base_score = (weighted / len(required)) * 88
        score = int(min(base_score + role_evidence_bonus(role, text), 96))
        if score >= 92 and missing:
            score = 88
        if score:
            results.append({
                "role": role,
                "match_percentage": score,
                "matched_skills": matched,
                "missing_skills": missing,
            })

    return sorted(results, key=lambda item: item["match_percentage"], reverse=True)


def suggest_roles(skills, text=""):
    suggestions = []
    matches = match_roles(skills, text)

    for match in matches:
        missing = match.get("missing_skills", [])
        matched = match.get("matched_skills", [])
        reason = "Matched skills: " + ", ".join(matched) if matched else "Partial skill overlap"
        suggestions.append({
            "role": match["role"],
            "match_score": match["match_percentage"],
            "reason": reason,
            "missing_skills": missing,
            "recommended_learning": [LEARNING_MAP.get(skill, f"Learn {skill}") for skill in missing[:3]],
        })

    existing = {item["role"] for item in suggestions}
    for role, required in ROLE_SKILLS.items():
        if role in existing:
            continue
        missing = list(required)
        suggestions.append({
            "role": role,
            "match_score": 0,
            "reason": "No direct required skill evidence found",
            "missing_skills": missing,
            "recommended_learning": [LEARNING_MAP.get(skill, f"Learn {skill}") for skill in missing[:3]],
        })

    return sorted(suggestions, key=lambda item: item["match_score"], reverse=True)


def extract_projects(text):
    sections = split_sections(text)
    source = sections.get("projects") or ""
    if not source:
        source = sections.get("experience") or text

    chunks = []
    buffer = []

    for line in source.splitlines():
        item = line.strip(" -*\t")
        if not item:
            continue
        if re.match(r"^[A-Za-z /+.-]+:\s*[\w, .+-]+$", item) and len(item) < 90:
            continue
        if len(item) >= 35:
            chunks.append(item)
        elif buffer:
            buffer.append(item)

    if not chunks:
        chunks = [part.strip(" -*\t") for part in re.split(r"\n|\.", source) if len(part.strip()) >= 35]

    deduped = []
    seen = set()
    for item in chunks:
        key = normalize(item)
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    return deduped[:6]


def score_project(text):
    lower = normalize(text)
    impact_words = [
        "improved", "increased", "reduced", "optimized", "achieved",
        "built", "developed", "created", "performed", "identified",
        "automated", "delivered", "analyzed", "implemented",
    ]
    metrics = re.findall(r"\d+%|\d+x|\d+k|\d+", lower)
    technologies = sum(1 for skill, keywords in TECH_SKILLS.items() if any(keyword in lower for keyword in keywords))

    score = len(metrics) * 10
    score += sum(8 for word in impact_words if word in lower)
    score += min(technologies * 4, 24)
    return min(score, 100)


def analyze_projects(text):
    return [
        {
            "summary": project[:140],
            "impact_score": score_project(project),
        }
        for project in extract_projects(text)
    ]


def infer_role(role_matches):
    if not role_matches:
        return "Generalist"
    return role_matches[0]["role"]


def detect_weaknesses(skills, role_matches, projects):
    weaknesses = []
    tech = safe_dict(skills).get("technical", {})
    top = role_matches[0] if role_matches else None

    if top:
        for skill in top.get("missing_skills", [])[:3]:
            weaknesses.append(f"Add {skill} to strengthen {top['role']} fit.")

    if not projects:
        weaknesses.append("Add project entries with tools, outcome, and measurable impact.")

    if "git" not in tech:
        weaknesses.append("Add Git or GitHub evidence.")

    if not role_matches:
        weaknesses.append("Focus resume toward one target role.")

    return weaknesses[:5]


def run_analysis(parsed_data):
    text = safe_dict(parsed_data).get("raw_text", "")
    if not text:
        return {}

    skills = extract_skills(text)
    role_matches = safe_list(match_roles(skills.get("technical", {}), text))
    projects = safe_list(analyze_projects(text))
    top_score = role_matches[0]["match_percentage"] if role_matches else 0
    suggested_roles = suggest_roles(skills.get("technical", {}), text)
    structured_resume = {
        "name": safe_dict(parsed_data).get("name", ""),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "skills": {
            "technical": [display_skill(skill) for skill in skills.get("technical", {}).keys()],
            "soft": [skill.title() for skill in skills.get("soft", [])],
        },
        "projects": [project["summary"] for project in projects],
        "certifications": extract_certifications(text),
        "suggested_roles": suggested_roles,
    }

    return {
        "skills": skills,
        "role_matches": role_matches,
        "projects": projects,
        "inferred_role": infer_role(role_matches),
        "top_match_score": top_score,
        "weaknesses": detect_weaknesses(skills, role_matches, projects),
        "suggested_roles": suggested_roles,
        "structured_resume": structured_resume,
    }
