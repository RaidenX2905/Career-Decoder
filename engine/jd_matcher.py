import math
import re
from engine.skill_taxonomy import extract_taxonomy_skills, get_skill_display, SKILL_TAXONOMY

def tokenize(text: str):
    words = re.findall(r"\b[A-Za-z0-9+#.-]{2,}\b", text.lower())
    # Exclude common stop words
    stopwords = {
        "and", "the", "for", "with", "that", "this", "from", "into", "using",
        "our", "your", "have", "been", "will", "are", "were", "was", "has"
    }
    return [w for w in words if w not in stopwords]

def compute_tf_vector(tokens):
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    total = len(tokens) if tokens else 1
    return {k: v / total for k, v in tf.items()}

def cosine_similarity(vec1: dict, vec2: dict):
    intersection = set(vec1.keys()) & set(vec2.keys())
    dot_product = sum(vec1[k] * vec2[k] for k in intersection)
    mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
    if not mag1 or not mag2:
        return 0.0
    return dot_product / (mag1 * mag2)

def match_resume_to_job_description(resume_text: str, jd_text: str):
    """
    Deterministic Job Description matching:
    1. Skill overlap (Exact & Synonymous)
    2. TF-IDF Cosine Term Similarity
    3. Missing Hard Requirements
    4. Keyword Coverage
    """
    if not jd_text or not resume_text:
        return {}

    # Extract skills present in both
    jd_skills = extract_taxonomy_skills(jd_text)
    resume_skills = extract_taxonomy_skills(resume_text)

    jd_keys = set(jd_skills.keys())
    res_keys = set(resume_skills.keys())

    matched_skills = sorted(list(jd_keys & res_keys))
    missing_skills = sorted(list(jd_keys - res_keys))

    skill_coverage_pct = int((len(matched_skills) / len(jd_keys)) * 100) if jd_keys else 100

    # Term-level Cosine Similarity
    jd_tokens = tokenize(jd_text)
    res_tokens = tokenize(resume_text)
    vec_jd = compute_tf_vector(jd_tokens)
    vec_res = compute_tf_vector(res_tokens)
    semantic_sim = int(cosine_similarity(vec_jd, vec_res) * 100)

    # Composite JD Match Index (65% Skill Vector, 35% Content Alignment)
    composite_score = int((skill_coverage_pct * 0.65) + (semantic_sim * 0.35))
    composite_score = min(max(composite_score, 0), 100)

    return {
        "overall_match_score": composite_score,
        "skill_coverage_pct": skill_coverage_pct,
        "semantic_similarity_pct": semantic_sim,
        "matched_skills": [get_skill_display(s) for s in matched_skills],
        "missing_skills": [get_skill_display(s) for s in missing_skills],
        "missing_raw": missing_skills,
        "total_jd_skills_detected": len(jd_keys),
    }
