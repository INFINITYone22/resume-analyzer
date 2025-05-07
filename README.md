# AI-Powered Resume Analyzer

<!-- Uncomment and use a real badge if you set up CI -->
<!-- ![Tests](https://github.com/INFINITYone22/resume-analyzer/actions/workflows/tests.yml/badge.svg) -->

An impressive, modern web application that analyzes your resume using AI/NLP and provides actionable feedback to help you stand out!

**© 2024 [@INFINITYone22](https://github.com/INFINITYone22). All Rights Reserved.**

## 🚀 Features
- Upload your resume (PDF/DOCX)
- Extracted content preview
- AI-driven feedback on skills, keywords, and suggestions
- Downloadable feedback report (PDF)
- Beautiful, responsive UI with modern design
- Easy local setup (Docker support)
- Multiple AI provider integration (OpenAI, Google Gemini, Claude, etc.)
- Model selection for each AI provider
- Job matching analysis against job descriptions
- Graceful fallback for missing NLP libraries
- Comprehensive test suite

## 🛠️ Tech Stack
- Python (Streamlit)
- NLP: spaCy, NLTK (with graceful fallback to regex)
- PDF/DOCX parsing: PyPDF2, python-docx
- AI Integration: OpenAI, Google Gemini, Anthropic Claude, NVIDIA, OpenRouter, Cohere
- Data Visualization: matplotlib, wordcloud
- PDF Generation: reportlab
- Docker containerization
- Unit and integration testing

## 📁 Project Structure
```
resume-analyzer/
│
├── app/                  # Main application code
│   ├── nlp/              # NLP models and scripts
│   ├── utils/            # Utility functions
│   └── main.py           # Entry point
│
├── tests/                # Unit and integration tests
│   ├── test_parse_resume.py
│   ├── test_skill_extractor.py 
│   ├── test_ai_services.py
│   └── test_integration.py
│
├── Dockerfile            # For containerization
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
├── .gitignore
└── LICENSE
```

## 🏁 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/INFINITYone22/resume-analyzer.git
cd resume-analyzer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run locally
```bash
streamlit run app/main.py
```

### 4. Run with Docker
```bash
docker build -t resume-analyzer .
docker run -p 8501:8501 resume-analyzer
```

### 5. Run tests
```bash
python -m unittest discover -s tests
```

## 📸 Screenshots
*To be added as the project develops!*

## 🔑 Setting Up API Keys
To use the AI features, you'll need to provide your own API keys in the Settings tab for one of the supported providers:

- [OpenAI](https://platform.openai.com/api-keys)
- [Google Gemini](https://makersuite.google.com/)
- [Anthropic Claude](https://console.anthropic.com/)
- [OpenRouter](https://openrouter.ai/)
- [NVIDIA NIMs](https://www.nvidia.com/)
- [Cohere](https://dashboard.cohere.ai/)

## 🆕 Latest Updates
- Added model selection for each AI provider
- Improved error handling for NLP libraries
- Enhanced UI with modern header design
- Added comprehensive test suite
- Graceful fallback when optional dependencies aren't available

## 🤝 Contributing
- This is a personal project by [@INFINITYone22](https://github.com/INFINITYone22). If you'd like to contribute, please contact me first.

Contributions, issues, and feature requests are welcome!

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards.

For major changes, please open an issue first to discuss what you would like to change. Contact [@INFINITYone22](https://github.com/INFINITYone22) before starting work on large features or refactors.

## 📄 License
All rights reserved. This code may not be used commercially without explicit permission.

Copyright (c) 2024 [@INFINITYone22](https://github.com/INFINITYone22)
