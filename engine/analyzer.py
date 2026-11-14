import re
from engine.skill_taxonomy import (
    extract_taxonomy_skills,
    get_skill_display,
    get_prerequisites_path,
    SKILL_TAXONOMY
)
from engine.xyz_analyzer import analyze_all_bullets

# 16 High-Precision Industry Roles with explicit core, supporting, and bonus profiles
ROLE_SPECIFICATIONS = {
    "AI / GenAI Engineer": {
        "core": ["python", "llm / genai", "nlp", "deep learning"],
        "supporting": ["machine learning", "fastapi", "docker", "mlops", "git"],
        "bonus": ["aws", "kubernetes"],
        "category": "AI & Data",
        "description": "Architects, fine-tunes, and deploys production RAG systems, LLM agents, and deep learning backbones."
    },
    "Machine Learning Engineer": {
        "core": ["python", "machine learning", "deep learning", "docker"],
        "supporting": ["mlops", "sql", "fastapi", "git", "data analysis"],
        "bonus": ["aws", "kubernetes"],
        "category": "AI & Data",
        "description": "Bridges machine learning research and distributed deployment with reproducible training pipelines."
    },
    "Data Scientist": {
        "core": ["python", "machine learning", "data analysis", "sql"],
        "supporting": ["data visualization", "deep learning", "nlp", "git"],
        "bonus": ["aws", "docker"],
        "category": "AI & Data",
        "description": "Transforms high-dimensional enterprise datasets into predictive statistical models and executive insights."
    },
    "Data Analyst": {
        "core": ["sql", "data analysis", "data visualization"],
        "supporting": ["python", "data warehouse", "git"],
        "bonus": ["machine learning", "aws"],
        "category": "AI & Data",
        "description": "Designs executive business dashboards, performs exploratory analyses, and standardizes BI pipelines."
    },
    "Data Engineer": {
        "core": ["python", "sql", "data warehouse", "kafka"],
        "supporting": ["spark", "docker", "aws", "git"],
        "bonus": ["kubernetes", "terraform"],
        "category": "Data Engineering",
        "description": "Builds resilient streaming ingestion buses, lakehouse architectures, and dimensional data warehouses."
    },
    "Backend Developer": {
        "core": ["python", "node", "java", "sql", "rest api"],
        "supporting": ["fastapi", "docker", "git", "microservices", "redis"],
        "bonus": ["aws", "kubernetes", "ci/cd"],
        "category": "Software Engineering",
        "description": "Constructs high-concurrency microservices, robust REST APIs, cache layers, and relational schema designs."
    },
    "Frontend Developer": {
        "core": ["html", "css", "javascript", "react"],
        "supporting": ["typescript", "nextjs", "git", "testing"],
        "bonus": ["redux", "graphql"],
        "category": "Software Engineering",
        "description": "Builds responsive, high-performance web applications with modular client architectures."
    },
    "Full Stack Developer": {
        "core": ["javascript", "react", "node", "sql", "html", "css"],
        "supporting": ["typescript", "docker", "git", "rest api", "fastapi"],
        "bonus": ["aws", "redis"],
        "category": "Software Engineering",
        "description": "Full lifecycle engineering across client interfaces, business microservices, caching, and databases."
    },
    "DevOps / Cloud Engineer": {
        "core": ["docker", "kubernetes", "aws", "ci/cd"],
        "supporting": ["terraform", "linux", "git"],
        "bonus": ["python", "gcp"],
        "category": "Cloud & Infrastructure",
        "description": "Automates cloud environments, maintains Kubernetes clusters, and codifies infrastructure as code."
    },
    "Site Reliability Engineer (SRE)": {
        "core": ["linux", "kubernetes", "docker"],
        "supporting": ["python", "aws", "terraform", "ci/cd", "git"],
        "bonus": ["go", "microservices"],
        "category": "Cloud & Infrastructure",
        "description": "Ensures uptime SLAs, auto-healing infrastructure, observability metrics, and incident recovery."
    },
    "Cybersecurity / AppSec Engineer": {
        "core": ["cybersecurity", "linux", "python"],
        "supporting": ["docker", "git", "aws", "rest api"],
        "bonus": ["kubernetes", "sql"],
        "category": "Security",
        "description": "Audits application vulnerabilities, implements zero-trust architectures, and secures cloud perimeters."
    },
    "QA & Automation Engineer": {
        "core": ["testing", "python", "git"],
        "supporting": ["javascript", "ci/cd", "rest api", "docker"],
        "bonus": ["sql", "react"],
        "category": "Quality",
        "description": "Designs automated end-to-end regression frameworks, performance benchmarks, and CI testing gates."
    },
    "Product Manager (Technical)": {
        "core": ["sql", "data analysis", "rest api"],
        "supporting": ["git", "data visualization", "testing"],
        "bonus": ["python", "docker"],
        "category": "Product & Strategy",
        "description": "Aligns engineering execution with commercial objectives, technical specifications, and user data metrics."
    },
}

SOFT_SKILLS = [
    "communication", "leadership", "teamwork", "problem solving",
    "critical thinking", "collaboration", "mentoring", "agile", "scrum", "ownership"
]

SOFT_PATTERNS = {
    s: re.compile(rf"\b{re.escape(s)}\b", re.IGNORECASE) for s in SOFT_SKILLS
}


def display_skill(canonical_key: str) -> str:
    return get_skill_display(canonical_key)


def evaluate_role_suitability(skills_dict: dict, text: str):
    """
    Evaluates candidate skills against 13 core industry specializations.
    Deterministic multi-tier scoring:
    - Core Skills (55% weight)
    - Supporting Skills (25% weight)
    - Bonus Integrations (10% weight)
    - Depth of Evidence (10% weight)
    """
    candidate_skills = set(skills_dict.keys())
    results = []

    for role_name, spec in ROLE_SPECIFICATIONS.items():
        core = spec.get("core", [])
        supporting = spec.get("supporting", [])
        bonus = spec.get("bonus", [])

        # Backend developer qualification rule
        matched_core = [s for s in core if s in candidate_skills]
        if role_name == "Backend Developer":
            core_ratio = min(len(matched_core) / 2.0, 1.0)
        else:
            core_ratio = len(matched_core) / len(core) if core else 1.0

        matched_supporting = [s for s in supporting if s in candidate_skills]
        supporting_ratio = len(matched_supporting) / len(supporting) if supporting else 0.5

        matched_bonus = [s for s in bonus if s in candidate_skills]
        bonus_pts = min(len(matched_bonus) * 3, 10)

        depth_pts = sum(4 if skills_dict.get(s) == "Strong" else (2 if skills_dict.get(s) == "Intermediate" else 0) for s in matched_core)

        raw_score = (core_ratio * 55) + (supporting_ratio * 25) + bonus_pts + min(depth_pts, 10)
        final_score = int(min(max(raw_score, 0), 100))

        missing_core = [s for s in core if s not in candidate_skills]
        missing_supporting = [s for s in supporting if s not in candidate_skills]

        results.append({
            "role": role_name,
            "match_percentage": final_score,
            "category": spec.get("category", "General"),
            "description": spec.get("description", ""),
            "matched_skills": [get_skill_display(s) for s in matched_core + matched_supporting],
            "missing_skills": missing_core + missing_supporting,
            "missing_core": missing_core,
            "prerequisites_roadmap": [get_skill_display(s) for s in get_prerequisites_path(missing_core[:3])],
        })

    return sorted(results, key=lambda x: x["match_percentage"], reverse=True)


def calculate_ats_scoring_index(skills_dict: dict, bullets_analysis: list, sections: dict, text: str):
    """
    Explainable, 5-Dimension Transparent Scoring Model:
    1. Technical Stack Breadth & Depth (30 pts)
    2. Quantified Project Impact & Metrics (25 pts)
    3. Structural Completeness & Formatting (15 pts)
    4. Seniority & Experience Signals (15 pts)
    5. Soft Skills & Communication Evidence (15 pts)
    """
    # 1. Tech stack
    tech_count = len(skills_dict)
    strong_count = sum(1 for v in skills_dict.values() if v == "Strong")
    tech_pts = min(tech_count * 2.5 + strong_count * 2, 30)

    # 2. Project impact
    if bullets_analysis:
        avg_score = sum(b.get("score", 0) for b in bullets_analysis) / len(bullets_analysis)
        project_pts = min((avg_score / 100) * 25 + len(bullets_analysis) * 1.5, 25)
    else:
        project_pts = 10

    # 3. Format integrity
    struct_pts = 0
    if "experience" in sections: struct_pts += 5
    if "skills" in sections: struct_pts += 5
    if "projects" in sections or "education" in sections: struct_pts += 5

    # 4. Seniority signal
    lines = text.splitlines()
    exp_pts = 14 if len(lines) > 25 else 9

    # 5. Soft skills
    soft_found = [s for s, pat in SOFT_PATTERNS.items() if pat.search(text)]
    soft_pts = min(len(soft_found) * 3, 15)

    breakdown = {
        "Technical Stack": int(tech_pts),
        "Project Impact": int(project_pts),
        "Format Integrity": int(struct_pts),
        "Seniority Signal": int(exp_pts),
        "Soft Skills": int(soft_pts),
    }

    total_score = int(min(max(sum(breakdown.values()), 15), 100))
    return total_score, breakdown, soft_found


def extract_project_summaries(text: str):
    projects_section = ""
    for sec_name in ["projects", "experience"]:
        lines = text.splitlines()
        # Find section boundary
        if sec_name in text.lower():
            projects_section = text
            break
    
    bullets = analyze_all_bullets(projects_section if projects_section else text)
    results = []
    for b in bullets:
        results.append({
            "summary": b["original"],
            "impact_score": b["score"],
            "rating": "High Impact" if b["score"] >= 75 else ("Solid Evidence" if b["score"] >= 45 else "Unquantified"),
            "is_xyz": b["is_xyz_compliant"],
            "metrics": b["metrics_found"],
            "feedback": b["feedback"]
        })
    return results[:4]


def run_analysis(parsed_data: dict):
    raw_text = parsed_data.get("raw_text", "")
    if not raw_text:
        return {}

    sections = parsed_data.get("sections", {})
    tech_skills = extract_taxonomy_skills(raw_text)
    bullets = analyze_all_bullets(raw_text)
    role_matches = evaluate_role_suitability(tech_skills, raw_text)
    ats_score, ats_breakdown, soft_skills = calculate_ats_scoring_index(tech_skills, bullets, sections, raw_text)
    projects = extract_project_summaries(raw_text)

    top_role = role_matches[0]["role"] if role_matches else "Software Engineer"
    top_score = role_matches[0]["match_percentage"] if role_matches else 0

    return {
        "skills": {
            "technical": tech_skills,
            "soft": soft_skills,
        },
        "role_matches": role_matches,
        "projects": projects,
        "bullets_analysis": bullets,
        "inferred_role": top_role,
        "top_match_score": top_score,
        "ats_score": ats_score,
        "ats_breakdown": ats_breakdown,
    }
