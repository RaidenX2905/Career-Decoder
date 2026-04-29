# Career Decoder

**Career Decoder** is an advanced Career Intelligence System built with Streamlit. It parses resumes (PDF/TXT), extracts structured career evidence, scores role capability, and generates concise learning recommendations based on the candidate's profile.

## ✨ Key Features

- **Intelligent Parsing**: Extracts candidate name, location, title, education, experience, projects, certifications, and skills.
- **Role Capability Scoring**: Models candidate fit against various roles and provides a capability percentage.
- **Skill Gap Analysis**: Identifies missing skills and provides actionable learning recommendations.
- **Evidence Mapping**: Visualizes the strength and coverage of the extracted resume evidence.
- **Polished UI**: A modern, responsive dashboard with a clean light-mode aesthetic, featuring interactive Plotly charts and robust data presentation.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/RaidenX2905/Career-Decoder.git
   cd Career-Decoder
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## 📁 Project Structure

```text
├── app.py                 # Main Streamlit application
├── engine/                # Core intelligence engine
│   ├── analyzer.py        # Role capability and skill gap analysis
│   └── parser.py          # Resume parsing and extraction logic
├── assets/                # Static assets and sample data
│   └── sample_resume.txt  # Sample resume for testing
├── .streamlit/            # Streamlit configuration
│   └── config.toml
└── requirements.txt       # Project dependencies
```

## ☁️ Deployment

This application is ready to be deployed on platforms like [Streamlit Community Cloud](https://streamlit.io/cloud), [Render](https://render.com/), or [Hugging Face Spaces](https://huggingface.co/spaces). Simply point the deployment service to `app.py` as the entry point.

## 📄 License

This project is licensed under the MIT License.