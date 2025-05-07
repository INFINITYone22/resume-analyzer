import re
from typing import List, Dict, Set
import os

# Flag to track NLP libraries availability
NLP_LIBRARIES_AVAILABLE = True

# Try to import NLP libraries, but don't fail if they aren't available
try:
    import spacy
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    
    # Download NLTK resources on first run
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('punkt')
        nltk.download('stopwords')
except ImportError:
    NLP_LIBRARIES_AVAILABLE = False
    print("Warning: NLP libraries (spaCy and/or NLTK) not available. Using regex-based skill extraction only.")

# Common technical skills - this is a starter list
COMMON_TECH_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "c++", "c#", "ruby", "php", "swift", "kotlin", "typescript",
    "go", "rust", "scala", "perl", "r", "matlab", "bash", "powershell", "sql", "html", "css",
    "c", "objective-c", "assembly", "dart", "elixir", "haskell", "lua", "fortran", 
    
    # Frameworks & Libraries
    "react", "angular", "vue", "django", "flask", "spring", "laravel", "express", ".net", "node.js",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "bootstrap", "jquery",
    "redux", "next.js", "gatsby", "rails", "symfony", "fastapi", "flask", "asp.net",
    
    # Databases & Storage
    "mysql", "postgresql", "mongodb", "sqlite", "oracle", "sql server", "dynamodb", "cassandra",
    "redis", "couchbase", "firebase", "mariadb", "elasticsearch", "neo4j", "influxdb",
    
    # Cloud & DevOps
    "aws", "azure", "google cloud", "gcp", "docker", "kubernetes", "jenkins", "github actions",
    "terraform", "ansible", "puppet", "chef", "prometheus", "grafana", "circleci", "travis ci",
    "gitlab ci", "heroku", "digitalocean", "cloudflare", "nginx", "apache",
    
    # Tools & Platforms
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "trello", "slack", "notion",
    "figma", "sketch", "adobe xd", "photoshop", "illustrator", "vscode", "intellij", "eclipse",
    "android studio", "xcode", "postman", "jupyter",
    
    # Methodologies & Concepts
    "agile", "scrum", "kanban", "tdd", "bdd", "ci/cd", "devops", "microservices", "rest", "graphql",
    "oauth", "jwt", "mvc", "oop", "functional programming", "serverless", "machine learning", "ai",
    "data science", "big data", "etl", "data warehousing", "data mining", "nlp", "computer vision",
    "deep learning", "reinforcement learning", "blockchain",
    
    # Soft Skills
    "communication", "teamwork", "leadership", "problem solving", "critical thinking", 
    "project management", "time management", "adaptability", "creativity"
}

# Business and soft skills
BUSINESS_SKILLS = {
    "leadership", "management", "project management", "team management", "strategy", 
    "business analysis", "business intelligence", "business development", "sales", "marketing",
    "product management", "analytics", "data analysis", "communication", "presentation",
    "negotiation", "stakeholder management", "customer service", "client relationship",
    "problem solving", "decision making", "critical thinking", "adaptability", 
    "time management", "organization", "planning", "reporting", "budgeting", "forecasting",
    "research", "risk management", "compliance", "teamwork", "collaboration", "agile", "scrum"
}

# Load spaCy model
def load_nlp_model():
    """Load the spaCy NLP model if available."""
    if not NLP_LIBRARIES_AVAILABLE:
        return None
        
    try:
        # Try to load the model
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # If model not found, download it
        try:
            os.system("python -m spacy download en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
        except:
            print("Warning: Could not download spaCy model. Using regex-based skill extraction only.")
            return None
    return nlp

def extract_skills_with_nlp(text: str) -> Dict[str, List[str]]:
    """Extract skills using NLP libraries if available."""
    # Convert text to lowercase for matching
    text_lower = text.lower()
    
    # Tokenize text
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text_lower)
    
    # Filter out stop words and punctuation
    filtered_tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
    
    # Extract n-grams (1, 2, and 3-grams)
    unigrams = filtered_tokens
    bigrams = [unigrams[i] + " " + unigrams[i+1] for i in range(len(unigrams)-1)]
    trigrams = [unigrams[i] + " " + unigrams[i+1] + " " + unigrams[i+2] for i in range(len(unigrams)-2)]
    
    all_ngrams = unigrams + bigrams + trigrams
    
    # Match against skill lists
    tech_skills = set()
    soft_skills = set()
    
    for term in all_ngrams:
        if term in COMMON_TECH_SKILLS:
            tech_skills.add(term)
        if term in BUSINESS_SKILLS:
            soft_skills.add(term)
    
    return tech_skills, soft_skills

def extract_skills_with_regex(text: str) -> Dict[str, List[str]]:
    """Extract skills using regex patterns when NLP libraries aren't available."""
    # Convert text to lowercase for matching
    text_lower = text.lower()
    
    tech_skills = set()
    soft_skills = set()
    
    # Look for exact matches in the original text
    for skill in COMMON_TECH_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            tech_skills.add(skill)
            
    for skill in BUSINESS_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            soft_skills.add(skill)
    
    # Try to extract programming languages, frameworks, and tools using patterns
    patterns = [
        # Programming language pattern
        r'(?:proficient in|experience with|skilled in|knowledge of|familiar with)\s+([A-Za-z0-9, \.+#]+)',
        # Skills section pattern
        r'(?:technical skills|skills|technical expertise|languages|programming languages)[:\s]*([A-Za-z0-9, \.+#]+)'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            skill_text = match.group(1)
            skill_candidates = re.split(r'[,;/]', skill_text)
            for candidate in skill_candidates:
                candidate = candidate.strip()
                if candidate and len(candidate) > 2:  # Avoid very short terms
                    # Check if it's a known tech skill
                    if candidate in COMMON_TECH_SKILLS:
                        tech_skills.add(candidate)
                    elif candidate in BUSINESS_SKILLS:
                        soft_skills.add(candidate)
                    # Else add any capitalized terms as potential skills
                    elif any(c.isupper() for c in candidate):
                        tech_skills.add(candidate)
    
    return tech_skills, soft_skills

def extract_skills(text: str) -> Dict[str, List[str]]:
    """
    Extract technical and soft skills from resume text.
    Works with or without NLP libraries installed.
    
    Args:
        text: The resume text
        
    Returns:
        Dictionary with technical_skills and soft_skills lists
    """
    if NLP_LIBRARIES_AVAILABLE:
        # Use NLP-based extraction
        tech_skills, soft_skills = extract_skills_with_nlp(text)
    else:
        # Fall back to regex-based extraction
        tech_skills, soft_skills = extract_skills_with_regex(text)
    
    # Also use regex extraction in all cases to catch additional terms
    tech_skills_regex, soft_skills_regex = extract_skills_with_regex(text)
    
    # Combine results
    tech_skills.update(tech_skills_regex)
    soft_skills.update(soft_skills_regex)
    
    # Sort skills alphabetically
    return {
        "technical_skills": sorted(list(tech_skills)),
        "soft_skills": sorted(list(soft_skills))
    } 