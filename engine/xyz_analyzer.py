import re

# High-impact Action Verbs categorized by engineering competency
POWER_ACTION_VERBS = {
    "Architecture & Development": [
        "architected", "engineered", "developed", "built", "designed", "constructed",
        "implemented", "authored", "deployed", "spearheaded", "formulated", "created"
    ],
    "Optimization & Performance": [
        "optimized", "accelerated", "streamlined", "reduced", "scaled", "boosted",
        "minimized", "enhanced", "consolidated", "upgraded", "maximized", "achieved", "maintained"
    ],
    "Automation & Operations": [
        "automated", "orchestrated", "containerized", "provisioned", "standardized",
        "integrated", "refactored", "migrated", "configured", "debugged", "decreased"
    ],
    "Analytics & Research": [
        "analyzed", "forecasted", "modeled", "evaluated", "benchmarked", "extracted",
        "quantified", "audited", "discovered", "investigated", "delivered", "trained"
    ]
}

# Weak phrases that recruiters flag as passive / low-agency
WEAK_PHRASES = [
    (r"\bworked on\b", "developed / engineered / built"),
    (r"\bresponsible for\b", "spearheaded / executed / delivered"),
    (r"\bhelped with\b", "accelerated / co-developed"),
    (r"\binvolved in\b", "contributed to / implemented"),
    (r"\bassisted in\b", "collaborated on / supported"),
    (r"\btasked with\b", "delivered / executed"),
    (r"\bhandled\b", "managed / orchestrated"),
]

METRIC_PATTERNS = [
    r"\d+%\b",
    r"\d+x\b",
    r"\b\d+k\b",
    r"\$\d+",
    r"\b\d+(?:\.\d+)?\s*(?:ms|fps|sec|seconds|s|users|nodes|requests|mb|gb|tb|k-fold|fps)\b",
    r"\b\d+\+\b",
    r"\b(?:99\.9%|sub-\d+ms|sub-\d+(?:\.\d+)?s)\b"
]


def is_bullet_point_candidate(line: str) -> bool:
    """Check if a line represents an accomplishment bullet rather than a title/metadata."""
    clean = line.strip()
    if len(clean) < 35:
        return False
    # Reject tech stack tags, titles, dates, URLs
    if clean.startswith("[") or clean.startswith("(") or "http" in clean.lower():
        return False
    if re.search(r"^(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{4})\b", clean, re.IGNORECASE):
        return False
    if " | " in clean or clean.endswith("Demo") or clean.endswith("GitHub"):
        return False
    return True


def analyze_bullet_xyz(sentence: str):
    """
    Evaluates a single resume bullet point against Google's XYZ formula:
    - X (Accomplishment / What)
    - Y (Measurable impact / Quantified metric)
    - Z (How / Methodology & Tool)
    """
    clean_s = sentence.strip(" -*•\t")
    if not is_bullet_point_candidate(clean_s):
        return None

    lower = clean_s.lower()

    # 1. Action Verb Evaluation (Z / X)
    found_power_verbs = []
    for cat, verbs in POWER_ACTION_VERBS.items():
        for v in verbs:
            if re.search(rf"\b{re.escape(v)}\b", lower):
                found_power_verbs.append(v)

    # Check for weak passive phrases
    detected_weak_phrases = []
    for pat, suggestion in WEAK_PHRASES:
        if re.search(pat, lower):
            detected_weak_phrases.append(suggestion)

    # 2. Metric / Quantification Detection (Y)
    metrics = []
    for p in METRIC_PATTERNS:
        matches = re.findall(p, lower)
        if matches:
            metrics.extend(matches)
    has_metric = len(metrics) > 0

    # 3. Method / Tool Evidence (Z)
    method_indicators = ["by", "using", "utilizing", "via", "through", "leveraging", "architecting", "implementing", "engineering", "deploying"]
    has_method = any(re.search(rf"\b{re.escape(m)}\b", lower) for m in method_indicators)

    # Scoring out of 100
    score = 0
    feedback_reasons = []

    if found_power_verbs:
        score += 35
    else:
        feedback_reasons.append("Start with a decisive power action verb.")

    if has_metric:
        score += 40
    else:
        feedback_reasons.append("Add quantified metrics (%, ms, fps, scale).")

    if has_method:
        score += 25
    else:
        feedback_reasons.append("State engineering methodology [Z].")

    if detected_weak_phrases:
        score = max(score - 15, 10)
        feedback_reasons.append(f"Replace passive phrasing with ({', '.join(detected_weak_phrases)}).")

    score = min(score, 100)

    suggested_rewrite = None
    if not has_metric:
        suggested_rewrite = f"Accomplished [Outcome], as measured by [X% / Y metric], by {clean_s[0].lower() + clean_s[1:]}."

    return {
        "original": clean_s,
        "score": score,
        "is_xyz_compliant": score >= 75,
        "has_metric": has_metric,
        "metrics_found": list(set(metrics))[:3],
        "power_verbs": list(set(found_power_verbs))[:2],
        "weak_phrases": detected_weak_phrases,
        "feedback": feedback_reasons,
        "suggested_template": suggested_rewrite,
    }


def extract_multiline_bullets(text: str) -> list:
    """Reassembles wrapped multi-line bullets into coherent single bullets."""
    lines = text.splitlines()
    bullets = []
    current_bullet = []

    for raw in lines:
        line = raw.strip()
        if not line:
            if current_bullet:
                bullets.append(" ".join(current_bullet))
                current_bullet = []
            continue

        if line.startswith(("•", "-", "*")):
            if current_bullet:
                bullets.append(" ".join(current_bullet))
            current_bullet = [line.lstrip("•-* \t")]
        elif current_bullet:
            # Continuation line
            current_bullet.append(line)
        else:
            if len(line) >= 40 and not line.startswith("["):
                current_bullet = [line]

    if current_bullet:
        bullets.append(" ".join(current_bullet))

    return bullets


def analyze_all_bullets(text: str):
    raw_bullets = extract_multiline_bullets(text)
    analyzed = []
    for b in raw_bullets:
        res = analyze_bullet_xyz(b)
        if res:
            analyzed.append(res)
    return analyzed
