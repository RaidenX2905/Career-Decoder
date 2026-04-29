import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engine.analyzer import run_analysis
from engine.parser import extract_text_from_pdf, parse_resume


st.set_page_config(
    page_title="Career Decoder",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #f4f7fb;
        --panel: #ffffff;
        --panel-soft: #f8fafc;
        --border: #d9e2ec;
        --text: #0f172a;
        --muted: #64748b;
        --primary: #334ee8;
        --primary-2: #7c3aed;
        --accent: #06b6d4;
        --gold: #f59e0b;
        --rose: #e11d48;
        --primary-soft: #eef2ff;
        --success: #0f766e;
        --warning: #b45309;
    }

    html, body, [class*="css"] {
        font-family: Inter, sans-serif;
    }

    .stApp {
        background:
            linear-gradient(135deg, rgba(51, 78, 232, 0.10) 0%, rgba(6, 182, 212, 0.06) 24%, transparent 44%),
            linear-gradient(225deg, rgba(124, 58, 237, 0.08) 0%, rgba(245, 158, 11, 0.04) 28%, transparent 48%),
            linear-gradient(180deg, #fbfdff 0%, var(--bg) 45%, #eef3f9 100%);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(248, 250, 252, 0.88);
        backdrop-filter: blur(10px);
    }

    .block-container {
        max-width: 1240px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.96);
        border: 1px solid var(--border);
        border-radius: 12px;
        box-shadow: 0 14px 38px rgba(15, 23, 42, 0.08);
    }

    .hero-panel {
        border: 1px solid var(--border);
        border-radius: 18px;
        background:
            linear-gradient(135deg, rgba(255,255,255,0.96) 0%, rgba(248,250,252,0.88) 52%, rgba(238,242,255,0.88) 100%),
            linear-gradient(90deg, rgba(51,78,232,0.14), rgba(6,182,212,0.08), rgba(245,158,11,0.08));
        box-shadow: 0 24px 70px rgba(15, 23, 42, 0.13);
        padding: 34px 34px;
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
    }

    .eyebrow {
        color: #3730a3;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.11em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .hero-title {
        background: linear-gradient(90deg, #0f172a 0%, #334ee8 45%, #0e7490 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.15rem;
        font-weight: 850;
        line-height: 1.05;
        margin: 0 0 10px 0;
    }

    .hero-copy {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.6;
        max-width: 780px;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin-top: 22px;
    }

    .hero-chip {
        border: 1px solid rgba(148, 163, 184, 0.34);
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.78);
        padding: 12px 14px;
        color: #334155;
        font-size: 0.88rem;
        font-weight: 700;
    }

    .gradient-strip {
        height: 4px;
        border-radius: 999px;
        background: linear-gradient(90deg, #334ee8, #06b6d4, #7c3aed, #f59e0b);
        margin: 12px 0 0 0;
    }

    .upload-shell {
        max-width: 760px;
        margin: 0 auto;
    }

    .upload-panel {
        border: 1px solid var(--border);
        border-radius: 18px;
        background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.96) 100%);
        box-shadow: 0 18px 48px rgba(15, 23, 42, 0.10);
        padding: 26px 28px;
        text-align: center;
    }

    .upload-title {
        color: var(--text);
        font-size: 1.6rem;
        font-weight: 820;
        margin: 0 0 8px 0;
    }

    .upload-copy {
        color: var(--muted);
        font-size: 0.96rem;
        line-height: 1.6;
        margin-bottom: 18px;
    }

    .upload-actions {
        display: flex;
        gap: 10px;
        justify-content: center;
        margin-top: 12px;
        flex-wrap: wrap;
    }

    .section-note {
        color: var(--muted);
        font-size: 0.92rem;
    }

    .score-band {
        border-radius: 10px;
        padding: 16px 18px;
        background: var(--primary-soft);
        border: 1px solid #c7d2fe;
    }

    .stButton > button {
        border-radius: 9px;
        font-weight: 750;
        border: 1px solid var(--primary);
        background: var(--primary);
        color: white;
        min-height: 2.55rem;
    }

    .stButton > button[kind="secondary"] {
        background: #ffffff;
        color: var(--text);
        border-color: var(--border);
    }

    .stFileUploader section {
        background: var(--panel-soft);
        border: 1px dashed #b8c7d9;
        border-radius: 10px;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #dbe5f0;
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.9);
    }

    div[data-testid="stMetricValue"] {
        color: var(--text);
        font-weight: 850;
    }

    .dataframe {
        border-radius: 8px;
    }

    div[data-testid="stTabs"] button {
        font-weight: 750;
    }

    .premium-callout {
        border: 1px solid #c7d2fe;
        border-radius: 12px;
        background: linear-gradient(135deg, #eef2ff 0%, #ecfeff 58%, #fffbeb 100%);
        padding: 14px 16px;
        color: #1e293b;
        font-weight: 650;
        margin: 8px 0 10px 0;
    }

    .mini-label {
        color: var(--muted);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    .role-row {
        display: grid;
        grid-template-columns: minmax(120px, 1fr) 62px;
        gap: 12px;
        align-items: center;
        margin: 10px 0;
    }

    .role-name {
        color: #1e293b;
        font-weight: 750;
        font-size: 0.92rem;
    }

    .role-score {
        color: #334ee8;
        font-weight: 850;
        text-align: right;
    }

    .role-track {
        grid-column: 1 / 3;
        height: 9px;
        border-radius: 999px;
        overflow: hidden;
        background: #e2e8f0;
    }

    .role-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #334ee8, #06b6d4, #7c3aed);
    }

    @media (max-width: 760px) {
        .hero-title {
            font-size: 2rem;
        }
        .hero-panel {
            padding: 22px 20px;
        }
        .hero-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .upload-panel {
            padding: 22px 18px;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            padding: 12px;
        }
        .hero-copy {
            font-size: 0.9rem;
        }
        .hero-chip {
            font-size: 0.75rem;
            padding: 8px 10px;
        }
    }

    @media (max-width: 480px) {
        .hero-title {
            font-size: 1.6rem;
        }
        .hero-panel {
            padding: 18px 16px;
        }
        .hero-grid {
            grid-template-columns: 1fr;
        }
        .upload-panel {
            padding: 18px 14px;
        }
        .upload-title {
            font-size: 1.3rem;
        }
        .upload-copy {
            font-size: 0.85rem;
        }
        .stButton > button {
            font-size: 0.85rem;
            min-height: 2.2rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def read_uploaded_resume(uploaded_file):
    if uploaded_file.name.lower().endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file.read())
    return uploaded_file.read().decode("utf-8", errors="ignore")


def analyze_text(text):
    parsed = parse_resume(text)
    analysis = run_analysis(parsed)
    return parsed, analysis


def get_value(data, key, fallback="No data available"):
    if not isinstance(data, dict):
        return fallback
    value = data.get(key)
    if value in (None, "", []):
        return fallback
    return value


def as_list(value):
    return value if isinstance(value, list) else []


def as_dict(value):
    return value if isinstance(value, dict) else {}


def structured_payload(analysis):
    payload = get_value(analysis, "structured_resume", {})
    return payload if isinstance(payload, dict) else {}


def readiness_score(analysis):
    score = int(get_value(analysis, "top_match_score", 0) or 0)
    skills = as_dict(get_value(analysis, "skills", {})).get("technical", {})
    projects = as_list(get_value(analysis, "projects", []))
    payload = structured_payload(analysis)
    education = as_list(payload.get("education", []))
    experience = as_list(payload.get("experience", []))

    skill_score = min(len(skills), 12) / 12 * 100
    project_score = min(len(projects), 4) / 4 * 100
    evidence_score = min(len(education) + len(experience), 4) / 4 * 100
    return int((score * 0.45) + (skill_score * 0.25) + (project_score * 0.18) + (evidence_score * 0.12))


def avg_project_impact(analysis):
    projects = as_list(get_value(analysis, "projects", []))
    if not projects:
        return 0
    scores = [int(project.get("impact_score", 0) or 0) for project in projects]
    return int(sum(scores) / len(scores))


def unique_missing_skills(analysis):
    missing = []
    for role in as_list(get_value(analysis, "suggested_roles", [])):
        for skill in role.get("missing_skills", []):
            if skill not in missing:
                missing.append(skill)
    return missing


def role_suggestions(analysis):
    return as_list(get_value(analysis, "suggested_roles", []))


def empty(message="No data available"):
    st.info(message, icon=None)


def render_hero():
    st.markdown(
        """
        <div class="hero-panel">
            <div class="eyebrow">Career Intelligence System</div>
            <h1 class="hero-title">Career Decoder</h1>
            <div class="hero-copy">
                Upload a resume, extract structured career data, score realistic role fits,
                and generate concise learning recommendations from evidence in the document.
            </div>
            <div class="hero-grid">
                <div class="hero-chip">Resume evidence parser</div>
                <div class="hero-chip">Role-fit intelligence</div>
                <div class="hero-chip">Skill gap roadmap</div>
                <div class="hero-chip">Evidence quality scoring</div>
            </div>
            <div class="gradient-strip"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_input_section():
    with st.container():
        st.markdown("<div class='upload-shell'>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="upload-panel">
                <div class="upload-title">Upload Resume</div>
                <div class="upload-copy">
                    Drop PDF or TXT here, then submit to generate role scores, skill gaps, and structured evidence.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("resume_upload_form", clear_on_submit=False):
            uploaded = st.file_uploader(
                "Resume file",
                type=["pdf", "txt"],
                label_visibility="collapsed",
            )
            left, right = st.columns([0.5, 0.5])
            with left:
                submitted = st.form_submit_button("Submit resume", use_container_width=True)
            with right:
                reset_clicked = st.form_submit_button("Reset", use_container_width=True)

        if reset_clicked:
            st.session_state.result = None
            st.session_state.last_file_name = ""
            st.rerun()

        if submitted:
            if uploaded is None:
                st.error("Upload a PDF or TXT resume before submitting.")
            else:
                text = read_uploaded_resume(uploaded)
                if not text.strip():
                    st.error("No readable text found in uploaded file.")
                else:
                    with st.spinner("Parsing resume and generating role intelligence..."):
                        st.session_state.result = analyze_text(text)
                        st.session_state.last_file_name = uploaded.name
                    st.rerun()

        if st.session_state.get("last_file_name"):
            st.caption(f"Last analyzed: {st.session_state.last_file_name}")
        st.markdown("</div>", unsafe_allow_html=True)


def render_result_header():
    with st.container(border=True):
        left, right = st.columns([0.82, 0.18])
        with left:
            st.subheader("Career Decoder")
            if st.session_state.get("last_file_name"):
                st.caption(f"Analyzed: {st.session_state.last_file_name}")
        with right:
            if st.button("Reset", use_container_width=True, type="secondary"):
                st.session_state.result = None
                st.session_state.last_file_name = ""
                st.rerun()


def render_profile(parsed, analysis):
    name = get_value(parsed, "name", "Unknown Candidate")
    location = get_value(parsed, "location")
    title = get_value(parsed, "title", get_value(analysis, "inferred_role"))
    score = int(get_value(analysis, "top_match_score", 0) or 0)
    skills = get_value(analysis, "skills", {})
    technical = skills.get("technical", {}) if isinstance(skills, dict) else {}
    projects = get_value(analysis, "projects", [])
    suggestions = role_suggestions(analysis)

    with st.container(border=True):
        profile, stats = st.columns([1.35, 1.65], gap="large")
        with profile:
            st.caption("Candidate profile")
            st.header(name)
            st.write(f"{title} | {location}")
            if suggestions:
                st.write(f"Highest capability: {suggestions[0].get('role', 'No data available')}")
        with stats:
            c1, c2, c3 = st.columns(3)
            c1.metric("Top match", f"{score}%")
            c2.metric("Technical skills", len(technical))
            c3.metric("Projects", len(projects) if isinstance(projects, list) else 0)


def render_intelligence_brief(analysis):
    payload = structured_payload(analysis)
    suggestions = role_suggestions(analysis)
    top_role = suggestions[0].get("role", "No role match") if suggestions else "No role match"
    readiness = readiness_score(analysis)
    impact = avg_project_impact(analysis)
    missing = unique_missing_skills(analysis)
    education_count = len(as_list(payload.get("education", [])))
    experience_count = len(as_list(payload.get("experience", [])))
    cert_count = len(as_list(payload.get("certifications", [])))

    with st.container(border=True):
        st.subheader("Executive career brief")
        st.markdown(
            f"""
            <div class="premium-callout">
                Primary positioning: {top_role}. Readiness score blends role match,
                technical depth, project evidence, and resume completeness.
            </div>
            """,
            unsafe_allow_html=True,
        )

        left, right = st.columns([0.95, 1.05], gap="large")
        with left:
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=readiness,
                    number={"suffix": "%", "font": {"size": 42, "color": "#0f172a"}},
                    gauge={
                        "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "#94a3b8"},
                        "bar": {"color": "#334EE8"},
                        "bgcolor": "#f8fafc",
                        "borderwidth": 1,
                        "bordercolor": "#dbe5f0",
                        "steps": [
                            {"range": [0, 45], "color": "#fee2e2"},
                            {"range": [45, 70], "color": "#fef3c7"},
                            {"range": [70, 100], "color": "#d1fae5"},
                        ],
                    },
                    title={"text": "Career readiness", "font": {"size": 16, "color": "#475569"}},
                )
            )
            fig.update_layout(
                height=270,
                margin=dict(l=10, r=10, t=40, b=0),
                paper_bgcolor="#FFFFFF",
                font=dict(color="#0f172a"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with right:
            c1, c2 = st.columns(2)
            c1.metric("Avg project impact", f"{impact}%")
            c2.metric("Skill gaps", len(missing))
            c3, c4, c5 = st.columns(3)
            c3.metric("Education", education_count)
            c4.metric("Experience", experience_count)
            c5.metric("Certifications", cert_count)
            if missing:
                st.caption("Highest-value gaps")
                st.write(", ".join(missing[:6]))


def render_role_radar(analysis):
    suggestions = role_suggestions(analysis)

    with st.container(border=True):
        st.subheader("Capability radar")
        st.caption("All suggested roles plotted as percentage capability.")
        if not suggestions:
            empty()
            return

        roles = [item.get("role", "Role") for item in suggestions]
        scores = [int(item.get("match_score", 0) or 0) for item in suggestions]
        radar_roles = roles + [roles[0]]
        radar_scores = scores + [scores[0]]

        fig = go.Figure()
        fig.add_trace(
            go.Scatterpolar(
                r=radar_scores,
                theta=radar_roles,
                fill="toself",
                fillcolor="rgba(51, 78, 232, 0.20)",
                line=dict(color="#334EE8", width=4),
                marker=dict(size=8, color="#7C3AED"),
                hovertemplate="%{theta}: %{r}%<extra></extra>",
            )
        )
        fig.update_layout(
            height=420,
            margin=dict(l=20, r=20, t=20, b=20),
            polar=dict(
                radialaxis=dict(range=[0, 100], tickfont=dict(color="#64748b"), gridcolor="#e2e8f0"),
                angularaxis=dict(tickfont=dict(color="#0f172a", size=12)),
                bgcolor="#ffffff",
            ),
            paper_bgcolor="#FFFFFF",
            font=dict(color="#0f172a"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_skills(analysis):
    skills = get_value(analysis, "skills", {})
    technical = skills.get("technical", {}) if isinstance(skills, dict) else {}
    soft = skills.get("soft", []) if isinstance(skills, dict) else []

    with st.container(border=True):
        st.subheader("Skills inventory")
        st.caption("Normalized skills extracted from resume evidence.")
        if not technical and not soft:
            empty()
            return

        if technical:
            rows = [{"Skill": skill.title(), "Level": level} for skill, level in technical.items()]
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

        if soft:
            st.markdown("**Soft skills**")
            st.write(", ".join(skill.title() for skill in soft))


def render_skill_visuals(analysis):
    skills = as_dict(get_value(analysis, "skills", {}))
    technical = as_dict(skills.get("technical", {}))

    with st.container(border=True):
        st.subheader("Skill signal")
        st.caption("Distribution of extracted technical skill strength.")
        if not technical:
            empty()
            return

        level_counts = pd.Series(list(technical.values())).value_counts().reset_index()
        level_counts.columns = ["Level", "Count"]
        colors = {"Basic": "#06B6D4", "Intermediate": "#7C3AED", "Strong": "#F59E0B"}
        fig = go.Figure(
            go.Pie(
                labels=level_counts["Level"],
                values=level_counts["Count"],
                hole=0.58,
                marker_colors=[colors.get(level, "#334EE8") for level in level_counts["Level"]],
                textinfo="label+percent",
            )
        )
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="#FFFFFF",
            font=dict(color="#0f172a"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_role_matches(analysis):
    suggestions = role_suggestions(analysis)

    with st.container(border=True):
        st.subheader("All role capability scores")
        st.caption("Every modeled role scored as candidate capability percentage.")
        if not suggestions:
            empty()
            return

        st.markdown("**Capability by role**")
        for item in suggestions:
            role = item.get("role", "Role")
            score = int(item.get("match_score", 0) or 0)
            st.markdown(
                f"""
                <div class="role-row">
                    <div class="role-name">{role}</div>
                    <div class="role-score">{score}%</div>
                    <div class="role-track"><div class="role-fill" style="width:{score}%"></div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_projects(analysis):
    projects = get_value(analysis, "projects", [])

    with st.container(border=True):
        st.subheader("Project evidence")
        st.caption("Extracted project lines with impact scoring.")
        if not projects:
            empty()
            return

        rows = [
            {
                "Project / Evidence": project.get("summary", "No data available"),
                "Impact score": project.get("impact_score", 0),
            }
            for project in projects
        ]
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def render_evidence_map(analysis):
    payload = structured_payload(analysis)
    projects = as_list(get_value(analysis, "projects", []))
    skills = as_dict(get_value(analysis, "skills", {})).get("technical", {})
    categories = [
        ("Education", len(as_list(payload.get("education", []))), 1),
        ("Experience", len(as_list(payload.get("experience", []))), 2),
        ("Projects", len(projects), 3),
        ("Technical skills", len(skills), 10),
        ("Certifications", len(as_list(payload.get("certifications", []))), 1),
    ]

    with st.container(border=True):
        st.subheader("Resume evidence map")
        st.caption("Coverage view for facts extracted from the resume.")
        for label, count, target in categories:
            completion = min(count / target, 1.0) if target else 0
            st.write(f"{label}: {count}")
            st.progress(completion)


def render_dashboard(parsed, analysis):
    render_profile(parsed, analysis)
    tab_overview, tab_evidence = st.tabs(["Overview", "Evidence"])

    with tab_overview:
        c1, c2, c3, c4 = st.columns([1.05, 0.95, 1, 1], gap="small")
        with c1:
            render_role_matches(analysis)
        with c2:
            render_role_radar(analysis)
        with c3:
            render_skill_visuals(analysis)
        with c4:
            render_skills(analysis)

    with tab_evidence:
        left, right = st.columns([0.8, 1.2], gap="large")
        with left:
            render_evidence_map(analysis)
        with right:
            render_projects(analysis)

if "result" not in st.session_state:
    st.session_state.result = None
if "last_file_name" not in st.session_state:
    st.session_state.last_file_name = ""

if st.session_state.result:
    render_result_header()
    parsed_data, analysis_data = st.session_state.result
    render_dashboard(parsed_data, analysis_data)
else:
    render_hero()
    render_input_section()
