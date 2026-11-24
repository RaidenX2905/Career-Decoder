<p align="center">
  <img src="./assets/career-decoder-light-512.png" alt="Career Decoder Brand Mark" width="128" height="128">
</p>

<div align="center">

# Career Decoder

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](#) [![Streamlit](https://img.shields.io/badge/Streamlit-Cloud%20Ready-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](#) [![spaCy](https://img.shields.io/badge/spaCy-NLP-09A3D5?style=flat-square&logo=spacy&logoColor=white)](#) [![Plotly](https://img.shields.io/badge/Plotly-Analytics-3F4F75?style=flat-square&logo=plotly&logoColor=white)](#) [![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](#)

<p align="center">
  An advanced Career Intelligence System engineered to parse resumes, extract structured professional evidence, score role capability, and deliver targeted learning recommendations.
</p>

</div>

---

**Live Demo**: [https://careerdecoderbyjsh.streamlit.app/](https://careerdecoderbyjsh.streamlit.app/)

---

## Key Features

- **Intelligent Parsing**: Extracts candidate name, contact details, experience history, education, projects, certifications, and technical proficiencies from PDF and TXT documents.
- **Role Capability Scoring**: Models candidate alignment against modern technical roles with normalized capability metrics.
- **Skill Gap Analysis**: Identifies missing competencies and outputs actionable, prioritized learning paths.
- **Evidence Mapping**: Visualizes evidence distribution and coverage across experience domains using interactive Plotly charts.
- **Minimalist Interface**: Responsive light-mode dashboard designed for clarity and rapid candidate assessment.

---

## Quick Start

### Installation

```bash
git clone https://github.com/RaidenX2905/Career-Decoder.git
cd Career-Decoder
pip install -r requirements.txt
```

### Run Application

```bash
streamlit run app.py
```

---

## Project Structure

```text
├── app.py                 # Streamlit web application
├── engine/                # Core extraction and scoring algorithms
│   ├── analyzer.py        # Role capability and gap analysis
│   └── parser.py          # Resume parsing and regex extraction
├── assets/                # Test resumes and visual assets
└── requirements.txt       # Project dependencies
```

---

## License

MIT License
