import plotly.graph_objects as go
import streamlit as st

from engine.analyzer import run_analysis, display_skill
from engine.document_parser import parse_resume_document
from engine.jd_matcher import match_resume_to_job_description
from engine.skill_taxonomy import get_prerequisites_path


st.set_page_config(
    page_title="Career Decoder",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom High-Contrast Editorial CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {
        --ground: #fbfbf8;
        --surface: #ffffff;
        --hairline: #e2e2de;
        --text: #171717;
        --muted: #5a5a5a;
        --action: #121212;
    }

    /* 1. HIDE DEFAULT STREAMLIT HEADER TO PREVENT TITLE CLIPPING */
    [data-testid="stHeader"] {
        display: none !important;
        height: 0 !important;
    }

    #MainMenu, footer {
        visibility: hidden !important;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'IBM Plex Mono', monospace, sans-serif;
        background-color: var(--ground);
        color: var(--text);
        overflow-x: hidden;
    }

    /* 2. CENTERED APPLICATION CONTAINER */
    .block-container {
        max-width: 1180px !important;
        margin: 0 auto !important;
        padding-top: 3.2rem !important;
        padding-bottom: 1.5rem !important;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.75rem !important;
    }

    /* Minimal Card */
    .compact-panel {
        background: #ffffff;
        border: 1px solid var(--hairline);
        border-radius: 8px;
        padding: 1.25rem 1.4rem;
        box-sizing: border-box;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        margin-bottom: 0.5rem;
    }

    /* EDITORIAL MASTHEAD HEADER */
    .site-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        border-bottom: 1px solid var(--hairline);
        padding-top: 0.5rem;
        padding-bottom: 1.25rem;
        margin-bottom: 1.5rem;
    }

    .brand-title {
        font-family: 'EB Garamond', Georgia, serif !important;
        font-size: clamp(30px, 3.2vw, 40px) !important;
        font-weight: 800 !important;
        color: #171717 !important;
        letter-spacing: -0.03em !important;
        line-height: 1.1 !important;
        margin: 0 !important;
        padding: 0 !important;
        white-space: nowrap !important;
    }

    .brand-subtitle {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        color: var(--muted) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        margin-bottom: 4px !important;
        white-space: nowrap !important;
    }

    /* Action Buttons */
    button, div.stButton > button, div[data-testid="stButton"] > button {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        padding: 0.55rem 1.3rem !important;
        border: 1px solid #121212 !important;
        background-color: #121212 !important;
        color: #ffffff !important;
        cursor: pointer !important;
        transition: background-color 150ms ease !important;
    }

    button:hover, div.stButton > button:hover, div[data-testid="stButton"] > button:hover {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
        border-color: #000000 !important;
    }

    .status-tag {
        display: inline-block;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        padding: 2px 7px;
        border-radius: 4px;
        font-weight: 600;
    }
    .status-tag.green {
        background: #f0fdfa;
        color: #0f766e;
        border: 1px solid #99f6e4;
    }

    /* Candidate Header Compact */
    .dash-header {
        background: #ffffff;
        border: 1px solid var(--hairline);
        border-radius: 8px;
        padding: 0.95rem 1.4rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.85rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }

    .ats-big-num {
        font-family: 'EB Garamond', Georgia, serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #171717;
        line-height: 1;
    }

    /* Prevent adding multiple files: hide dropzone when a file is selected */
    [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"]) [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"]) button[data-testid="baseButton-secondary"],
    [data-testid="stFileUploaderFile"] ~ div [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] + div button,
    [data-testid="stFileUploader"] button[aria-label*="Add"],
    [data-testid="stFileUploader"] svg[data-icon="plus"] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_landing():
    st.markdown(
        """
        <header class="site-header">
            <h1 class="brand-title">Career Decoder</h1>
            <div class="brand-subtitle">ATS DIAGNOSTICS & MULTI-ROLE EVALUATION</div>
        </header>
        """,
        unsafe_allow_html=True,
    )

    c_left, c_right = st.columns([1.1, 0.9], gap="large")

    with c_left:
        st.markdown(
            """
            <h2 style="font-family: 'EB Garamond', Georgia, serif; font-size: 2.6rem; font-weight: 600; line-height: 1.15; margin: 0.25rem 0 0.75rem 0; color: #171717;">
                Evaluate technical resumes against algorithmic hiring standards.
            </h2>
            <p style="font-size: 0.92rem; color: #434342; line-height: 1.6; margin-bottom: 1.5rem;">
                Fast, zero-latency extraction across 16 modern engineering tracks, ATS breakdown, and automated recruitment score analytics.
            </p>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="display: flex; gap: 2.5rem; border-top: 1px solid #e2e2de; padding-top: 1rem; margin-top: 1rem;">
                <div>
                    <div style="font-family: 'EB Garamond', Georgia, serif; font-size: 2rem; font-weight: 600; color: #171717;">16</div>
                    <div style="font-size: 0.72rem; color: #666; text-transform: uppercase;">Role Models</div>
                </div>
                <div>
                    <div style="font-family: 'EB Garamond', Georgia, serif; font-size: 2rem; font-weight: 600; color: #171717;">&lt; 0.5s</div>
                    <div style="font-size: 0.72rem; color: #666; text-transform: uppercase;">Analysis Speed</div>
                </div>
                <div>
                    <div style="font-family: 'EB Garamond', Georgia, serif; font-size: 2rem; font-weight: 600; color: #171717;">100%</div>
                    <div style="font-size: 0.72rem; color: #666; text-transform: uppercase;">Private & In-Memory</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_right:
        st.markdown(
            """
            <div class="compact-panel">
                <p style="font-size: 0.88rem; font-weight: 600; color: #171717; margin: 0 0 8px 0;">Upload Technical Resume</p>
            """,
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Upload",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=False,
            label_visibility="collapsed",
            key="ephemeral_resume_uploader"
        )

        analyze_btn = st.button("Evaluate Resume", use_container_width=True)

        if analyze_btn:
            if uploaded_file is None:
                st.warning("Please select a file to evaluate.")
            else:
                file_bytes = uploaded_file.read()
                filename = uploaded_file.name
                parsed = parse_resume_document(file_bytes, filename)
                analysis = run_analysis(parsed)

                st.session_state.result = (parsed, analysis)
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def render_dashboard(parsed, analysis):
    name = parsed.get("name") or "Candidate Profile"
    title = parsed.get("title") or analysis.get("inferred_role") or "Software Engineer"
    location = parsed.get("location") or ""
    contact = parsed.get("contact", {})
    email = contact.get("email", "")
    
    ats_score = analysis.get("ats_score", 0)
    top_role = analysis.get("inferred_role", "Software Engineer")
    top_match = analysis.get("top_match_score", 0)
    role_matches = analysis.get("role_matches", [])

    # Minimal Top Bar with Reset button on the right
    col_nav_l, col_nav_r = st.columns([3.8, 1.2])
    with col_nav_l:
        st.markdown(
            """
            <header class="site-header" style="margin-bottom: 0.6rem; padding-bottom: 0.6rem;">
                <h1 class="brand-title">Career Decoder</h1>
                <div class="brand-subtitle">DIAGNOSTIC REPORT</div>
            </header>
            """,
            unsafe_allow_html=True,
        )
    with col_nav_r:
        if st.button("← New Evaluation", use_container_width=True):
            # Complete ephemeral memory purge: zero-out session state and garbage collect
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state.result = None
            import gc
            gc.collect()
            st.rerun()

    # Candidate Meta Strip
    loc_email = f" · {location}" if location else ""
    if email: loc_email += f" · {email}"

    st.markdown(
        f"""
        <div class="dash-header">
            <div>
                <span class="status-tag green" style="margin-bottom: 3px;">Primary Track: {top_role} ({top_match}% Fit)</span>
                <div style="font-family: 'EB Garamond', Georgia, serif; font-size: 1.7rem; font-weight: 600; color: #171717; line-height: 1.1;">{name}</div>
                <div style="font-size: 0.8rem; color: #5a5a5a; margin-top: 2px;">{title}{loc_email}</div>
            </div>
            <div style="display: flex; align-items: center; gap: 14px; background: #fbfbf8; border: 1px solid #e2e2de; padding: 6px 14px; border-radius: 6px;">
                <div style="text-align: right;">
                    <div style="font-size: 0.68rem; text-transform: uppercase; color: #666; font-weight: 600;">ATS Strength</div>
                    <div style="font-size: 0.74rem; color: #0f766e; font-weight: 600;">Deterministic Index</div>
                </div>
                <div class="ats-big-num">{ats_score}<span style="font-size: 0.95rem; color: #888;">/100</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2-Column Balanced Layout (Radar Capability Analysis | ATS Breakdown & Skills)
    col1, col2 = st.columns([1.45, 1], gap="large")

    with col1:
        st.markdown(
            """
            <div class="compact-panel">
                <div style="font-size: 0.76rem; font-weight: 600; text-transform: uppercase; color: #171717; margin-bottom: 6px;">Role Capability Radar</div>
            """,
            unsafe_allow_html=True,
        )
        # Clean & wrap role titles so labels never clip beyond canvas borders
        short_role_names = {
            "Product Manager (Technical)": "Product Mgr<br>(Tech)",
            "Cybersecurity / AppSec Engineer": "Cybersecurity<br>AppSec",
            "QA & Automation Engineer": "QA & Test<br>Automation",
            "Site Reliability Engineer (SRE)": "Site Reliability<br>(SRE)",
            "Machine Learning Engineer": "Machine Learning<br>Engineer",
            "AI / GenAI Engineer": "AI / GenAI<br>Engineer",
            "Full Stack Developer": "Full Stack<br>Developer",
            "Backend Developer": "Backend<br>Developer",
            "Frontend Developer": "Frontend<br>Developer",
            "Data Scientist": "Data<br>Scientist",
            "Data Analyst": "Data<br>Analyst",
            "Data Engineer": "Data<br>Engineer",
        }
        top_6 = role_matches[:6]
        labels = [short_role_names.get(r["role"], r["role"].replace(" ", "<br>")) for r in top_6]
        values = [r["match_percentage"] for r in top_6]

        if labels:
            labels_closed = labels + [labels[0]]
            values_closed = values + [values[0]]
            fig = go.Figure(
                go.Scatterpolar(
                    r=values_closed,
                    theta=labels_closed,
                    fill='toself',
                    fillcolor='rgba(18, 18, 18, 0.05)',
                    line=dict(color='#121212', width=1.5),
                    marker=dict(size=4, color='#121212')
                )
            )
            fig.update_layout(
                polar=dict(
                    domain=dict(x=[0.14, 0.86], y=[0.05, 0.95]),
                    radialaxis=dict(visible=True, range=[0, 100], color='#888', showticklabels=False),
                    angularaxis=dict(color='#171717', rotation=90, tickfont=dict(size=9.5, family="IBM Plex Mono"))
                ),
                margin=dict(l=10, r=10, t=25, b=25),
                height=380,
                paper_bgcolor='#ffffff',
                plot_bgcolor='#ffffff',
                font=dict(family="IBM Plex Mono", size=9.5, color="#434342")
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div class="compact-panel">
                <div style="font-size: 0.76rem; font-weight: 600; text-transform: uppercase; color: #171717; margin-bottom: 10px;">ATS Dimension Breakdown</div>
            """,
            unsafe_allow_html=True,
        )
        ats_breakdown = analysis.get("ats_breakdown", {})
        max_pts = {
            "Technical Stack": 30,
            "Project Impact": 25,
            "Format Integrity": 15,
            "Seniority Signal": 15,
            "Soft Skills": 15,
        }
        for metric, pts in ats_breakdown.items():
            m_max = max_pts.get(metric, 30)
            pct = int((pts / m_max) * 100) if m_max else 0
            st.markdown(
                f"""
                <div style="margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.76rem; margin-bottom: 2px;">
                        <span>{metric}</span>
                        <span style="color: #666;">{pts}/{m_max} ({pct}%)</span>
                    </div>
                    <div style="height: 5px; background: #eee; border-radius: 4px; overflow: hidden;">
                        <div style="height: 100%; width: {pct}%; background: #121212;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        tech = analysis.get("skills", {}).get("technical", {})
        if tech:
            st.markdown("<div style='font-size: 0.74rem; font-weight: 600; text-transform: uppercase; margin-top: 14px; margin-bottom: 6px;'>Extracted Tech Stack</div>", unsafe_allow_html=True)
            badges = " ".join([f"<span style='font-size: 0.72rem; background: #fbfbf8; border: 1px solid #dcdcd9; padding: 2px 6px; border-radius: 3px; display: inline-block; margin: 2px 1px;'>{display_skill(s)}</span>" for s in list(tech.keys())[:14]])
            st.markdown(badges, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


if "result" not in st.session_state:
    st.session_state.result = None

if st.session_state.result:
    parsed_res, analysis_res = st.session_state.result
    render_dashboard(parsed_res, analysis_res)
else:
    render_landing()
