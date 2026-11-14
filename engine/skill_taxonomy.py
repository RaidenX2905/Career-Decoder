import re

# Comprehensive skill taxonomy with aliases, categories, and direct graph prerequisites
SKILL_TAXONOMY = {
    # Languages
    "python": {
        "display": "Python",
        "category": "Languages",
        "aliases": ["python", "py", "python3"],
        "prerequisites": [],
        "related": ["django", "fastapi", "pandas", "numpy", "scikit-learn"]
    },
    "javascript": {
        "display": "JavaScript",
        "category": "Languages",
        "aliases": ["javascript", "js", "ecmascript"],
        "prerequisites": [],
        "related": ["typescript", "react", "node", "html", "css"]
    },
    "typescript": {
        "display": "TypeScript",
        "category": "Languages",
        "aliases": ["typescript", "ts"],
        "prerequisites": ["javascript"],
        "related": ["react", "nextjs", "node"]
    },
    "java": {
        "display": "Java",
        "category": "Languages",
        "aliases": ["java", "jvm", "j2ee"],
        "prerequisites": [],
        "related": ["spring", "microservices", "sql"]
    },
    "c++": {
        "display": "C++",
        "category": "Languages",
        "aliases": ["c++", "cpp"],
        "prerequisites": [],
        "related": ["linux", "algorithms", "opencv"]
    },
    "c#": {
        "display": "C# / .NET",
        "category": "Languages",
        "aliases": ["c#", "csharp", ".net", "dotnet"],
        "prerequisites": [],
        "related": ["sql", "microservices", "azure"]
    },
    "go": {
        "display": "Go (Golang)",
        "category": "Languages",
        "aliases": ["golang", "go lang", "go"],
        "prerequisites": [],
        "related": ["kubernetes", "docker", "microservices", "grpc"]
    },
    "rust": {
        "display": "Rust",
        "category": "Languages",
        "aliases": ["rust", "rustlang"],
        "prerequisites": [],
        "related": ["systems programming", "linux", "webassembly"]
    },
    "sql": {
        "display": "SQL & Relational DBs",
        "category": "Databases",
        "aliases": ["sql", "mysql", "postgres", "postgresql", "tsql", "plsql", "sqlite", "mariadb"],
        "prerequisites": [],
        "related": ["data analysis", "data warehouse", "database optimization"]
    },

    # Frontend
    "html": {
        "display": "HTML5",
        "category": "Frontend",
        "aliases": ["html", "html5"],
        "prerequisites": [],
        "related": ["css", "javascript"]
    },
    "css": {
        "display": "CSS3 & Modern Styling",
        "category": "Frontend",
        "aliases": ["css", "css3", "tailwind", "tailwindcss", "sass", "scss", "bootstrap"],
        "prerequisites": ["html"],
        "related": ["html", "javascript", "react"]
    },
    "react": {
        "display": "React.js",
        "category": "Frontend",
        "aliases": ["react", "reactjs", "react.js"],
        "prerequisites": ["javascript", "html", "css"],
        "related": ["nextjs", "redux", "typescript"]
    },
    "nextjs": {
        "display": "Next.js",
        "category": "Frontend",
        "aliases": ["next.js", "nextjs", "next"],
        "prerequisites": ["react", "typescript"],
        "related": ["react", "node", "typescript"]
    },
    "vue": {
        "display": "Vue.js",
        "category": "Frontend",
        "aliases": ["vue", "vuejs", "vue.js", "nuxt"],
        "prerequisites": ["javascript", "html", "css"],
        "related": ["javascript", "typescript"]
    },
    "redux": {
        "display": "Redux / State Management",
        "category": "Frontend",
        "aliases": ["redux", "zustand", "mobx"],
        "prerequisites": ["react"],
        "related": ["react", "typescript"]
    },

    # Backend
    "node": {
        "display": "Node.js & Express",
        "category": "Backend",
        "aliases": ["node", "nodejs", "node.js", "express", "expressjs"],
        "prerequisites": ["javascript"],
        "related": ["typescript", "rest api", "mongodb", "sql"]
    },
    "fastapi": {
        "display": "FastAPI",
        "category": "Backend",
        "aliases": ["fastapi"],
        "prerequisites": ["python"],
        "related": ["python", "rest api", "docker"]
    },
    "django": {
        "display": "Django & DRF",
        "category": "Backend",
        "aliases": ["django", "django rest framework", "drf"],
        "prerequisites": ["python"],
        "related": ["python", "sql", "rest api"]
    },
    "spring": {
        "display": "Spring Boot",
        "category": "Backend",
        "aliases": ["spring", "spring boot", "springboot"],
        "prerequisites": ["java"],
        "related": ["java", "microservices", "sql"]
    },
    "rest api": {
        "display": "RESTful API Architecture",
        "category": "Backend",
        "aliases": ["rest", "restful", "rest api", "apis", "api design"],
        "prerequisites": [],
        "related": ["microservices", "node", "fastapi", "spring"]
    },
    "microservices": {
        "display": "Distributed Microservices",
        "category": "Backend",
        "aliases": ["microservices", "micro-services", "distributed systems"],
        "prerequisites": ["rest api", "docker"],
        "related": ["kubernetes", "kafka", "docker"]
    },
    "graphql": {
        "display": "GraphQL",
        "category": "Backend",
        "aliases": ["graphql", "apollo"],
        "prerequisites": ["rest api"],
        "related": ["react", "node", "typescript"]
    },

    # Databases & Big Data
    "mongodb": {
        "display": "MongoDB (NoSQL)",
        "category": "Databases",
        "aliases": ["mongodb", "mongo", "nosql"],
        "prerequisites": [],
        "related": ["node", "redis"]
    },
    "redis": {
        "display": "Redis (In-Memory Cache)",
        "category": "Databases",
        "aliases": ["redis", "in-memory cache", "key-value store"],
        "prerequisites": [],
        "related": ["backend", "microservices"]
    },
    "kafka": {
        "display": "Apache Kafka (Event Bus)",
        "category": "Data Engineering",
        "aliases": ["kafka", "apache kafka", "event streaming"],
        "prerequisites": ["distributed systems"],
        "related": ["microservices", "spark", "data warehouse"]
    },
    "spark": {
        "display": "Apache Spark & PySpark",
        "category": "Data Engineering",
        "aliases": ["spark", "pyspark", "apache spark"],
        "prerequisites": ["python", "sql"],
        "related": ["kafka", "data warehouse", "hadoop"]
    },
    "data warehouse": {
        "display": "Data Warehousing (Snowflake/BigQuery)",
        "category": "Data Engineering",
        "aliases": ["snowflake", "bigquery", "redshift", "data warehouse", "dbt"],
        "prerequisites": ["sql"],
        "related": ["sql", "data analysis", "spark"]
    },

    # AI, ML & NLP
    "data analysis": {
        "display": "Data Analysis (Pandas/NumPy)",
        "category": "AI & Data",
        "aliases": ["data analysis", "eda", "pandas", "numpy", "scipy"],
        "prerequisites": ["python"],
        "related": ["python", "data visualization", "sql", "machine learning"]
    },
    "data visualization": {
        "display": "Data Visualization (Plotly/Tableau)",
        "category": "AI & Data",
        "aliases": ["matplotlib", "seaborn", "plotly", "power bi", "tableau", "looker"],
        "prerequisites": ["data analysis"],
        "related": ["data analysis", "python"]
    },
    "machine learning": {
        "display": "Machine Learning (Scikit-Learn)",
        "category": "AI & Data",
        "aliases": ["machine learning", "ml", "scikit-learn", "sklearn", "xgboost", "lightgbm"],
        "prerequisites": ["python", "data analysis"],
        "related": ["deep learning", "nlp", "mlops"]
    },
    "deep learning": {
        "display": "Deep Learning (PyTorch/TF)",
        "category": "AI & Data",
        "aliases": ["deep learning", "tensorflow", "keras", "pytorch", "torch", "neural network"],
        "prerequisites": ["machine learning", "python"],
        "related": ["computer vision", "nlp", "llm / genai"]
    },
    "nlp": {
        "display": "NLP & Transformers",
        "category": "AI & Data",
        "aliases": ["nlp", "natural language processing", "spacy", "nltk", "transformers", "huggingface", "bert"],
        "prerequisites": ["machine learning", "python"],
        "related": ["deep learning", "llm / genai"]
    },
    "llm / genai": {
        "display": "GenAI & LLM Architecture (RAG/Agents)",
        "category": "AI & Data",
        "aliases": ["llm", "large language model", "genai", "generative ai", "langchain", "llamaindex", "rag", "vector database", "chroma", "pinecone", "qdrant", "weaviate"],
        "prerequisites": ["nlp", "python"],
        "related": ["deep learning", "mlops", "fastapi"]
    },
    "mlops": {
        "display": "MLOps & Model Lifecycle",
        "category": "AI & Data",
        "aliases": ["mlops", "mlflow", "wandb", "kubeflow", "model deployment", "model serving"],
        "prerequisites": ["machine learning", "docker"],
        "related": ["docker", "kubernetes", "deep learning"]
    },
    "computer vision": {
        "display": "Computer Vision (OpenCV)",
        "category": "AI & Data",
        "aliases": ["computer vision", "cv", "opencv", "yolo", "mediapipe", "image processing"],
        "prerequisites": ["python", "deep learning"],
        "related": ["deep learning", "numpy"]
    },

    # DevOps, Cloud & Security
    "docker": {
        "display": "Docker Containerization",
        "category": "Cloud & DevOps",
        "aliases": ["docker", "container", "containers", "containerization"],
        "prerequisites": ["linux"],
        "related": ["kubernetes", "ci/cd", "microservices"]
    },
    "kubernetes": {
        "display": "Kubernetes (K8s)",
        "category": "Cloud & DevOps",
        "aliases": ["kubernetes", "k8s"],
        "prerequisites": ["docker", "linux"],
        "related": ["docker", "aws", "terraform"]
    },
    "aws": {
        "display": "AWS Cloud Services",
        "category": "Cloud & DevOps",
        "aliases": ["aws", "amazon web services", "ec2", "s3", "lambda", "ecs", "eks", "rds", "cloudformation"],
        "prerequisites": ["linux"],
        "related": ["docker", "kubernetes", "terraform", "ci/cd"]
    },
    "azure": {
        "display": "Microsoft Azure",
        "category": "Cloud & DevOps",
        "aliases": ["azure", "azure devops"],
        "prerequisites": ["linux"],
        "related": ["docker", "kubernetes", "ci/cd"]
    },
    "gcp": {
        "display": "Google Cloud Platform (GCP)",
        "category": "Cloud & DevOps",
        "aliases": ["gcp", "google cloud", "google cloud platform"],
        "prerequisites": ["linux"],
        "related": ["docker", "kubernetes", "bigquery"]
    },
    "ci/cd": {
        "display": "CI/CD Automation",
        "category": "Cloud & DevOps",
        "aliases": ["ci/cd", "cicd", "github actions", "gitlab ci", "jenkins", "circleci"],
        "prerequisites": ["git"],
        "related": ["docker", "testing", "kubernetes"]
    },
    "terraform": {
        "display": "Terraform & IaC",
        "category": "Cloud & DevOps",
        "aliases": ["terraform", "iac", "infrastructure as code", "ansible"],
        "prerequisites": ["aws"],
        "related": ["aws", "kubernetes", "docker"]
    },
    "linux": {
        "display": "Linux System & Shell",
        "category": "Cloud & DevOps",
        "aliases": ["linux", "bash", "shell scripting", "unix"],
        "prerequisites": [],
        "related": ["docker", "git", "ci/cd"]
    },
    "git": {
        "display": "Git & Version Control",
        "category": "Tools",
        "aliases": ["git", "github", "gitlab"],
        "prerequisites": [],
        "related": ["ci/cd", "linux"]
    },
    "cybersecurity": {
        "display": "Cybersecurity & AppSec",
        "category": "Security",
        "aliases": ["cybersecurity", "infosec", "penetration testing", "owasp", "soc2", "vulnerability assessment"],
        "prerequisites": ["linux", "rest api"],
        "related": ["linux", "docker", "cloud"]
    },
    "testing": {
        "display": "Automated Testing & QA",
        "category": "Quality",
        "aliases": ["unit testing", "pytest", "jest", "selenium", "cypress", "playwright", "tdd", "test automation"],
        "prerequisites": ["programming"],
        "related": ["ci/cd", "python", "javascript"]
    },
}

# Precompile skill regex map for instant sub-millisecond execution
SKILL_PATTERNS = {
    skill: re.compile(
        rf"(?:\b|\s)(?:{'|'.join(re.escape(k) for k in data['aliases'])})(?:\b|\s|[,\.;:])",
        re.IGNORECASE
    )
    for skill, data in SKILL_TAXONOMY.items()
}

def normalize_skill(name):
    clean = name.strip().lower()
    for canonical, data in SKILL_TAXONOMY.items():
        if clean == canonical or clean in data["aliases"]:
            return canonical
    return clean

def get_skill_display(canonical_key):
    return SKILL_TAXONOMY.get(canonical_key, {}).get("display", canonical_key.title())

def extract_taxonomy_skills(text):
    lower = f" {text.lower()} "
    found = {}
    for canonical, pat in SKILL_PATTERNS.items():
        matches = pat.findall(lower)
        count = len(matches)
        if count >= 3:
            found[canonical] = "Strong"
        elif count == 2:
            found[canonical] = "Intermediate"
        elif count == 1:
            found[canonical] = "Basic"
    return found

def get_prerequisites_path(missing_skills):
    """
    Topological ordering of missing skills based on skill dependency graph.
    """
    ordered = []
    visited = set()

    def visit(skill):
        if skill not in visited:
            visited.add(skill)
            prereqs = SKILL_TAXONOMY.get(skill, {}).get("prerequisites", [])
            for p in prereqs:
                if p in SKILL_TAXONOMY:
                    visit(p)
            ordered.append(skill)

    for s in missing_skills:
        visit(s)
    return ordered
