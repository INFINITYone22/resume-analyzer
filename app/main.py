import streamlit as st
import io
import os
import base64
from utils.parse_resume import extract_resume_text, extract_resume_sections
# Now we can directly import the extract_skills function
from nlp.skill_extractor import extract_skills
from utils.ai_services import AIProvider, analyze_resume_with_ai, get_job_match_analysis, AIServiceError, get_available_models
from utils.report_generator import generate_analysis_report

# Initialize session state variables if they don't exist
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "extracted_skills" not in st.session_state:
    st.session_state.extracted_skills = None
if "extracted_sections" not in st.session_state:
    st.session_state.extracted_sections = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "job_match_result" not in st.session_state:
    st.session_state.job_match_result = None
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "ai_provider" not in st.session_state:
    st.session_state.ai_provider = AIProvider.OPENAI.value
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = (
        "AI Talent Scout - 'Spark Finder'\n"
        "Your Role: You are 'Spark Finder,' an advanced AI Talent Scout. Your unique specialization is to identify individuals, especially freshers or those early in their career, who possess a genuine spark of passion, intrinsic motivation, and a strong drive to learn and contribute. Your analysis must transcend traditional, rigid metrics (like GPA or overly formal achievements). Instead, focus on uncovering authentic enthusiasm, the effort invested in personal projects (regardless of polish), and a candidate's potential alignment with a company's implied culture and work.\n"
        "Core Philosophy: Prioritize potential over polish, effort over formal endorsement, and genuine interest over keyword stuffing.\n"
        "I. Candidate Analysis (The 'Spark' Assessment):\n"
        "De-emphasize Formalities:\n"
        "Education: Briefly acknowledge educational background (institution, degree). Do not heavily weigh GPA or formal accolades unless they directly support evidence of passion or exceptional initiative (e.g., a thesis project deeply aligned with their stated interests or overcoming significant odds).\n"
        "Certificates: Note them, but prioritize demonstrated application of skills in projects over the certificate itself.\n"
        "Deep Dive into Projects & Self-Initiated Learning (CRITICAL):\n"
        "Genuine Enthusiasm & Personal Investment:\n"
        "For each project (especially personal/non-academic ones): What is the story behind it? Does the description convey genuine excitement, curiosity, or a desire to solve a personally meaningful problem?\n"
        "Look for language that indicates personal ownership, challenges overcome with persistence, and learnings that go beyond technical skills (e.g., 'I was really stuck on X, but then I discovered Y and it was a breakthrough!').\n"
        "Assess the effort and learning journey evident, even if projects are incomplete, 'hobbyist' in nature, or use unconventional approaches. The attempt and the learning are key.\n"
        "Problem-Solving & Creativity:\n"
        "What problem were they trying to solve? Was it self-defined?\n"
        "Is there evidence of creative thinking or a unique approach, even if simple?\n"
        "Resourcefulness & Learning Agility:\n"
        "What technologies/tools did they use? Does it show a willingness to pick up new things, even outside a formal curriculum?\n"
        "Are there mentions of online courses, tutorials, communities, or self-teaching that fueled their projects?\n"
        "Identifying Intrinsic Motivation & 'Openness':\n"
        "Breadth vs. Depth of Interests: Do their projects/activities show a focused passion in one area, or an open curiosity exploring multiple domains? Both can be valuable; note the pattern.\n"
        "Beyond the Resume: Look for hints of engagement with a wider community (e.g., GitHub contributions, blog posts, forum participation mentioned, hackathons, personal websites showcasing work).\n"
        "Language of Passion: Does the overall tone of the resume (especially in project descriptions or summaries) feel authentic, active, and driven by interest rather than obligation?\n"
        "Potential for Company Contribution & Growth:\n"
        "Learning Trajectory: Based on their projects and self-learning, what is their apparent capacity and eagerness to acquire new skills relevant to a professional environment?\n"
        "Collaborative Clues (if any): Do any project descriptions mention teamwork, sharing knowledge, or contributing to a group effort? (This is often limited in fresher resumes but look for it).\n"
        "II. Job Description (JD) & Company Context Analysis (If Provided):\n"
        "If a Job Description is provided, perform the following additional analysis:\n"
        "JD 'Strictness' Assessment:\n"
        "Analyze the language and requirements. Is it heavily weighted with 'must-have' skills, specific years of experience (even for entry-level), and non-negotiable criteria? Or does it seem more open to potential, learning on the job, and transferable skills?\n"
        "Rate perceived strictness (e.g., Low, Medium, High) with a brief justification.\n"
        "Implied Company Culture & Work Environment (Inferred solely from JD language):\n"
        "Keyword Analysis: Identify words and phrases in the JD that suggest cultural aspects (e.g., 'fast-paced,' 'collaborative,' 'innovative,' 'supportive,' 'autonomous,' 'results-driven,' 'client-focused,' 'detail-oriented,' 'dynamic').\n"
        "Tone & Emphasis: What is the overall tone? Is it formal and corporate, or more casual and enthusiastic? What qualities or values seem to be most emphasized for potential candidates?\n"
        "Hypothesize Environment: Based only on the JD text, what kind of work environment might a candidate expect? (e.g., 'Seems to value individual high-achievers in a competitive setting,' or 'Appears to foster teamwork and continuous learning in a supportive atmosphere.')\n"
        "Disclaimer for Output: Clearly state that this cultural inference is based solely on the text of the Job Description and is not an external assessment of the company.\n"
        "Candidate-JD Alignment (Focus on Potential & Enthusiasm):\n"
        "Beyond direct skill matches, how does the candidate's demonstrated enthusiasm, learning agility, and project themes align with the implied needs and culture of the role/company as suggested by the JD?\n"
        "Could their passion for a related area be channeled effectively for this role, even if direct experience is missing?\n"
        "Output Structure & Tone:\n"
        "Your analysis should be a narrative report, focusing on insights and potential:\n"
        "Candidate: [Name]\n"
        "Overall 'Spark' Assessment: A brief, holistic summary of their potential, genuine interest, and drive. Why do they stand out (or not)?\n"
        "Key Indicators of Passion & Drive: (Bullet points with specific evidence from projects, self-learning, language used)\n"
        "Project Deep Dive Highlights:\n"
        "For 1-2 most indicative projects:\n"
        "Project Name & Brief Goal\n"
        "Evidence of Enthusiasm/Effort:\n"
        "Key Learnings/Skills Demonstrated (technical & soft):\n"
        "Learning Agility & Resourcefulness: (Observations and evidence)\n"
        "Areas to Explore with Candidate: (Questions an interviewer could ask to delve deeper into their motivations, project challenges, and learning process, e.g., 'Tell me more about what inspired you to start Project X?' or 'What was the most enjoyable/frustrating part of learning Y technology for that project?')\n"
        "(If JD Provided) JD & Company Context Insights:\n"
        "JD Strictness Level: [e.g., Medium] - Rationale.\n"
        "Implied Work Environment (from JD): [Description based on JD language, with disclaimer].\n"
        "Potential Alignment & Fit: How might this candidate's 'spark' align with the role and implied culture? Where are the synergies or potential gaps to explore?\n"
        "Final Recommendation Level: (e.g., 'Strongly Consider for Interview,' 'Consider for Interview,' 'Potentially Promising - Needs Further Exploration,' 'Likely Not a Fit for This Type of Focus').\n"
        "Tone: Be an advocate for potential. Your language should be insightful, empathetic, and geared towards uncovering hidden gems. Focus on what the candidate is trying to do and could become, rather than what they haven't formally achieved. Be honest but constructive."
    )
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

# Set page config
st.set_page_config(
    page_title="AI-Powered Resume Analyzer", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
body {
    background: linear-gradient(120deg, #f8fafc 0%, #e0e7ef 100%) !important;
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
}
.main .block-container {
    padding-top: 2rem;
    max-width: 900px;
}
.st-emotion-cache-1dp5vir {
    background: none !important;
}

/* Modern card */
.card {
    background: #1f2937;
    color: #e2e8f0;
    border-radius: 16px;
    box-shadow: 0 4px 24px 0 rgba(0, 0, 0, 0.5);
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    border: 1px solid #374151;
}
.card-header {
    font-size: 1.4rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.card-section {
    margin-bottom: 1.2rem;
}
.badge {
    display: inline-block;
    background: #0d6efd;
    color: #fff;
    border-radius: 12px;
    padding: 0.2em 0.8em;
    font-size: 0.9em;
    margin-right: 0.5em;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #2a5298;
    margin-top: 1.2rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.strengths { color: #27ae60; }
.weaknesses { color: #e67e22; }
.suggestions { color: #0d6efd; }
.st-emotion-cache-1dp5vir { background: none !important; }

/* Modern header */
.header-container {
    display: flex;
    align-items: center;
    background: linear-gradient(90deg, #1e3c72, #2a5298);
    padding: 1.5rem;
    border-radius: 14px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(44,62,80,0.10);
}
.header-icon {
    font-size: 2.5rem;
    margin-right: 1.2rem;
    color: white;
}
.header-text {
    color: white;
}
.header-text h1 {
    margin: 0;
    padding: 0;
    color: white;
    font-size: 2.1rem;
    font-weight: 800;
}
.header-text p {
    margin: 0;
    padding: 0;
    color: rgba(255, 255, 255, 0.85);
    font-size: 1.1rem;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: #232946 !important;
    border-right: 1px solid #232946;
    color: #f8fafc !important;
}
.sidebar-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.5rem;
}
.sidebar-link {
    color: #f8fafc !important;
    text-decoration: none;
    font-size: 1rem;
    margin-bottom: 0.5rem;
    display: block;
    transition: color 0.2s;
}
.sidebar-link:hover, .sidebar-link:focus {
    color: #a5b4fc !important;
    text-decoration: underline;
}
.sidebar-madeby {
    color: #f8fafc !important;
    font-size: 1rem;
    margin-top: 2rem;
    opacity: 0.85;
}
.theme-toggle {
    margin-top: 2rem;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    background: #e6eaf1;
    color: #1e3c72;
    border: none;
    font-size: 1rem;
    cursor: pointer;
}

/* Footer */
.footer {
    margin-top: 20px;
    padding-top: 10px;
    border-top: 1px solid #eee;
    text-align: center;
    font-size: 0.8em;
    color: #666;
}

/* Code block styling for dark theme */
pre, code, .stCodeBlock {
    background-color: #1f2937 !important;
    color: #e2e8f0 !important;
    border-radius: 8px;
    padding: 1rem !important;
}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.markdown('<div class="sidebar-title">🤖 Resume Analyzer</div>', unsafe_allow_html=True)
st.sidebar.markdown('<a class="sidebar-link" href="https://github.com/INFINITYone22/resume-analyzer" target="_blank">GitHub Repository</a>', unsafe_allow_html=True)
st.sidebar.markdown('<a class="sidebar-link" href="https://github.com/INFINITYone22/resume-analyzer#readme" target="_blank">Documentation</a>', unsafe_allow_html=True)
st.sidebar.markdown('<a class="sidebar-link" href="https://platform.openai.com/api-keys" target="_blank">Get OpenAI API Key</a>', unsafe_allow_html=True)
st.sidebar.markdown('<a class="sidebar-link" href="https://makersuite.google.com/" target="_blank">Get Gemini API Key</a>', unsafe_allow_html=True)
st.sidebar.markdown('<a class="sidebar-link" href="https://console.anthropic.com/" target="_blank">Get Claude API Key</a>', unsafe_allow_html=True)
st.sidebar.markdown('<a class="sidebar-link" href="https://openrouter.ai/" target="_blank">Get OpenRouter API Key</a>', unsafe_allow_html=True)
st.sidebar.markdown('<a class="sidebar-link" href="https://dashboard.cohere.ai/" target="_blank">Get Cohere API Key</a>', unsafe_allow_html=True)
st.sidebar.markdown('<a class="sidebar-link" href="https://www.nvidia.com/" target="_blank">Get NVIDIA API Key</a>', unsafe_allow_html=True)
st.sidebar.markdown('---')
st.sidebar.markdown('Made by <a href="https://github.com/INFINITYone22" target="_blank">@INFINITYone22</a>', unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="header-container">
    <div class="header-icon">🤖</div>
    <div class="header-text">
        <h1>AI-Powered Resume Analyzer</h1>
        <p>Upload your resume, get AI-driven analysis, and improve your chances of landing interviews.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Create tabs for different sections
tabs = st.tabs([
    "📄 Upload Resume", 
    "🔍 Analysis", 
    "🎯 Job Match", 
    "⚙️ Settings"
])

# --- SETTINGS TAB ---
with tabs[3]:
    st.header("⚙️ Settings: AI Model Integration (Fresher Potential Focus)")
    st.markdown("""
    Configure your preferred AI provider and API key for deep, context-aware resume analysis. 
    Your API key is stored in your session only and never sent to our servers.
    """)
    
    st.subheader("AI Provider Configuration")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        provider = st.selectbox(
            "Select AI Provider",
            [provider.value for provider in AIProvider],
            index=[provider.value for provider in AIProvider].index(st.session_state.ai_provider),
            help="Choose your preferred AI model provider."
        )
        
        api_key = st.text_input(
            f"Enter your {provider} API Key",
            value=st.session_state.api_key if st.session_state.api_key else "",
            type="password",
            help="Your API key is used only for this session."
        )
        
        # Get available models for the selected provider
        models = get_available_models(provider, api_key if api_key else None)
        model_options = [{"label": model["name"], "value": model["id"]} for model in models]
        
        # Select model dropdown
        if models:
            selected_model_id = st.selectbox(
                "Select Model",
                options=[model["id"] for model in models],
                format_func=lambda x: next((model["name"] for model in models if model["id"] == x), x),
                help="Choose which model to use for analysis."
            )
            
            # Save selected model to session state
            st.session_state.selected_model = selected_model_id
        
        if provider == AIProvider.CUSTOM.value:
            st.info("""
            For custom API, enter: `endpoint_url|header_name:header_value`
            
            Example: `https://api.example.com/v1/completions|Authorization:Bearer my_token`
            """)
    
    with col2:
        st.markdown("### Provider Details")
        
        if provider == AIProvider.OPENAI.value:
            st.markdown("**OpenAI (ChatGPT)**")
            st.markdown("- Uses GPT-4o or GPT-3.5-Turbo")
            st.markdown("- Requires an API key from [OpenAI](https://platform.openai.com/api-keys)")
        elif provider == AIProvider.GOOGLE.value:
            st.markdown("**Google Gemini**")
            st.markdown("- Uses Gemini Pro")
            st.markdown("- Requires an API key from [Google AI Studio](https://makersuite.google.com/)")
        elif provider == AIProvider.ANTHROPIC.value:
            st.markdown("**Anthropic Claude**")
            st.markdown("- Uses Claude 3 Opus")
            st.markdown("- Requires an API key from [Anthropic](https://console.anthropic.com/)")
        elif provider == AIProvider.OPENROUTER.value:
            st.markdown("**OpenRouter**")
            st.markdown("- Provides access to various models")
            st.markdown("- Requires an API key from [OpenRouter](https://openrouter.ai/)")
        elif provider == AIProvider.NVIDIA.value:
            st.markdown("**NVIDIA NIMs**")
            st.markdown("- Uses NVIDIA's large language models")
            st.markdown("- Requires an API key from [NVIDIA](https://www.nvidia.com/)")
        elif provider == AIProvider.COHERE.value:
            st.markdown("**Cohere**")
            st.markdown("- Uses Command R+")
            st.markdown("- Requires an API key from [Cohere](https://dashboard.cohere.ai/)")
    
    st.subheader("System Prompt")
    system_prompt = st.text_area(
        "Customize the instructions sent to the AI model",
        value=st.session_state.system_prompt,
        height=150,
        help="This prompt guides the AI on how to analyze the resume."
    )
    
    if st.button("Save Settings", type="primary"):
        st.session_state.ai_provider = provider
        st.session_state.api_key = api_key
        st.session_state.system_prompt = system_prompt
        st.success(f"Settings saved for {provider}.")

# --- UPLOAD RESUME TAB ---
with tabs[0]:
    st.header("📄 Upload Your Resume")
    st.markdown("Upload your resume in PDF or DOCX format for AI-powered analysis.")

    # File uploader
    uploaded_file = st.file_uploader(
        "Drop your resume file here", 
        type=["pdf", "docx"], 
        help="PDF or DOCX files only"
    )

    if uploaded_file:
        with st.spinner("Extracting text from your resume..."):
            try:
                # Extract text from resume
                resume_text = extract_resume_text(uploaded_file, uploaded_file.name)
                
                if resume_text:
                    st.session_state.resume_text = resume_text
                    
                    # Extract resume sections
                    st.session_state.extracted_sections = extract_resume_sections(resume_text)
                    
                    # Extract skills using NLP
                    st.session_state.extracted_skills = extract_skills(resume_text)
                    
                    st.success(f"Successfully processed: {uploaded_file.name}")
                    
                    # Show extracted text and skills in expandable sections
                    with st.expander("View Extracted Text", expanded=False):
                        st.code(resume_text, language="markdown")
                    
                    # Display extracted skills
                    if st.session_state.extracted_skills:
                        tech_skills = st.session_state.extracted_skills.get("technical_skills", [])
                        soft_skills = st.session_state.extracted_skills.get("soft_skills", [])
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Technical Skills")
                            if tech_skills:
                                for skill in tech_skills:
                                    st.markdown(f"- {skill}")
                            else:
                                st.info("No technical skills detected.")
                        
                        with col2:
                            st.subheader("Soft Skills")
                            if soft_skills:
                                for skill in soft_skills:
                                    st.markdown(f"- {skill}")
                            else:
                                st.info("No soft skills detected.")
                                
                    # Next steps
                    st.markdown("### Next Steps")
                    st.markdown("Go to the **🔍 Analysis** tab to get AI-powered feedback on your resume.")
                    
                else:
                    st.warning("No text could be extracted from this file. Please upload a text-based PDF or DOCX.")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                st.warning("Please make sure your file is a valid PDF or DOCX.")
    else:
        # When no file is uploaded, offer a sample
        st.info("No file uploaded yet. You can upload your resume or use a sample file.")
        
        # Add sample resume option
        if st.button("Use Sample Resume"):
            # Load a sample resume text
            sample_text = """
            JOHN DOE
            Software Developer
            Email: john.doe@example.com | Phone: (123) 456-7890
            LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

            SUMMARY
            Experienced software developer with 5 years of experience in full-stack development.
            Proficient in Python, JavaScript, and cloud technologies.
            
            EXPERIENCE
            Senior Software Developer
            ABC Tech, San Francisco, CA
            January 2021 - Present
            • Led development of a customer-facing web application using React and Node.js
            • Implemented CI/CD pipeline using GitHub Actions, reducing deployment time by 40%
            • Mentored junior developers and conducted code reviews
            
            Software Developer
            XYZ Solutions, San Francisco, CA
            June 2018 - December 2020
            • Developed RESTful APIs using Python Flask
            • Optimized database queries, improving response time by 30%
            • Collaborated with UX designers to implement responsive UI components
            
            EDUCATION
            Bachelor of Science in Computer Science
            University of California, Berkeley
            2014 - 2018
            
            SKILLS
            Programming: Python, JavaScript, TypeScript, Java, SQL
            Web Technologies: React, Node.js, Express, HTML/CSS
            Cloud: AWS (EC2, S3, Lambda), Docker, Kubernetes
            Tools: Git, GitHub Actions, JIRA
            Soft Skills: Team leadership, communication, problem-solving
            
            PROJECTS
            Personal Website Builder (github.com/johndoe/website-builder)
            • Created a tool for non-technical users to build personal websites
            • Used React, Node.js, and MongoDB
            
            Data Visualization Dashboard
            • Built a dashboard to visualize business metrics using D3.js
            • Implemented real-time updates with WebSocket
            """
            
            st.session_state.resume_text = sample_text
            
            # Extract resume sections
            st.session_state.extracted_sections = extract_resume_sections(sample_text)
            
            # Extract skills using NLP
            st.session_state.extracted_skills = extract_skills(sample_text)
            
            st.success("Sample resume loaded successfully!")
            
            # Show extracted text and skills in expandable sections
            with st.expander("View Sample Resume Text", expanded=False):
                st.code(sample_text, language="markdown")
            
            # Display extracted skills
            if st.session_state.extracted_skills:
                tech_skills = st.session_state.extracted_skills.get("technical_skills", [])
                soft_skills = st.session_state.extracted_skills.get("soft_skills", [])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Technical Skills")
                    if tech_skills:
                        for skill in tech_skills:
                            st.markdown(f"- {skill}")
                    else:
                        st.info("No technical skills detected.")
                
                with col2:
                    st.subheader("Soft Skills")
                    if soft_skills:
                        for skill in soft_skills:
                            st.markdown(f"- {skill}")
                    else:
                        st.info("No soft skills detected.")
                        
            # Next steps
            st.markdown("### Next Steps")
            st.markdown("Go to the **🔍 Analysis** tab to get AI-powered feedback on your resume.")

# --- ANALYSIS TAB ---
with tabs[1]:
    st.header("🔍 Resume Analysis")
    
    if not st.session_state.resume_text:
        st.warning("Please upload a resume in the 'Upload Resume' tab first.")
    else:
        st.markdown("Get AI-powered analysis and feedback on your resume.")
        
        # Check if API key is configured
        if not st.session_state.api_key:
            st.warning(f"Please configure your {st.session_state.ai_provider} API key in the Settings tab.")
        else:
            if st.button("Analyze My Resume", type="primary"):
                with st.spinner("Analyzing your resume with AI..."):
                    try:
                        # Get AI analysis
                        analysis_result = analyze_resume_with_ai(
                            resume_text=st.session_state.resume_text,
                            provider=st.session_state.ai_provider,
                            api_key=st.session_state.api_key,
                            system_prompt=st.session_state.system_prompt,
                            model_id=st.session_state.selected_model,
                            extracted_skills=st.session_state.extracted_skills,
                            extracted_sections=st.session_state.extracted_sections
                        )
                        
                        # Save result to session state
                        st.session_state.analysis_result = analysis_result
                        
                        st.toast("Analysis complete!", icon="✅")
                    except AIServiceError as e:
                        st.error(f"AI Service Error: {str(e)}")
                        st.warning("Please check your API key and settings.")
        
        # Display analysis result if available
        if st.session_state.analysis_result:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><span>🧠</span> AI Analysis Results</div>', unsafe_allow_html=True)
            provider = st.session_state.analysis_result.get("provider", "AI Provider")
            model = st.session_state.analysis_result.get("model", "Unknown Model")
            st.markdown(f'<span class="badge">{provider}</span> <span class="badge">{model}</span>', unsafe_allow_html=True)
            tokens_used = st.session_state.analysis_result.get("tokens_used")
            if tokens_used:
                st.markdown(f'<span class="badge" style="background:#27ae60;">Tokens: {tokens_used}</span>', unsafe_allow_html=True)
            st.markdown('<hr style="margin:1rem 0;">', unsafe_allow_html=True)
            # Parse and display sections
            analysis_text = st.session_state.analysis_result.get("analysis", "No analysis available.")
            # Try to split by numbered sections
            import re
            sections = re.split(r"\n\s*\d+\. ", analysis_text)
            if len(sections) > 1:
                # The first section may be empty or intro
                for i, section in enumerate(sections):
                    if not section.strip():
                        continue
                    if i == 0:
                        continue
                    # Try to guess section type
                    title = None
                    if i == 1:
                        title = '<div class="section-title strengths">💪 Overall Assessment</div>'
                    elif i == 2:
                        title = '<div class="section-title strengths">🌟 Key Strengths</div>'
                    elif i == 3:
                        title = '<div class="section-title weaknesses">⚠️ Areas for Improvement</div>'
                    elif i == 4:
                        title = '<div class="section-title suggestions">💡 Suggestions</div>'
                    elif i == 5:
                        title = '<div class="section-title suggestions">📝 Action Items</div>'
                    else:
                        title = f'<div class="section-title">Section {i}</div>'
                    st.markdown(title, unsafe_allow_html=True)
                    st.markdown(f'<div class="card-section">{section.strip()}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="card-section">{analysis_text}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            # Generate PDF report button
            if st.button("Generate PDF Report"):
                with st.spinner("Generating PDF report..."):
                    try:
                        pdf_data = generate_analysis_report(
                            resume_text=st.session_state.resume_text,
                            analysis_result=st.session_state.analysis_result,
                            extracted_skills=st.session_state.extracted_skills,
                            extracted_sections=st.session_state.extracted_sections,
                            job_match_result=st.session_state.job_match_result
                        )
                        b64_pdf = base64.b64encode(pdf_data).decode('utf-8')
                        href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="resume_analysis_report.pdf">Download PDF Report</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error generating PDF report: {str(e)}")

# --- JOB MATCH TAB ---
with tabs[2]:
    st.header("🎯 Job Match Analysis")
    
    if not st.session_state.resume_text:
        st.warning("Please upload a resume in the 'Upload Resume' tab first.")
    else:
        st.markdown("Compare your resume against a job description to see how well you match and how to improve.")
        
        # Job description input
        job_description = st.text_area(
            "Paste the job description here",
            height=200,
            help="Copy and paste the full job description you're interested in."
        )
        
        # Check if API key is configured
        if not st.session_state.api_key:
            st.warning(f"Please configure your {st.session_state.ai_provider} API key in the Settings tab.")
        elif not job_description:
            st.info("Paste a job description above to analyze your match.")
        else:
            if st.button("Analyze Match", type="primary"):
                with st.spinner("Analyzing how well your resume matches this job..."):
                    try:
                        # Get job match analysis
                        job_match_result = get_job_match_analysis(
                            resume_text=st.session_state.resume_text,
                            job_description=job_description,
                            provider=st.session_state.ai_provider,
                            api_key=st.session_state.api_key,
                            model_id=st.session_state.selected_model
                        )
                        
                        # Save result to session state
                        st.session_state.job_match_result = job_match_result
                        
                        st.toast("Job match analysis complete!", icon="🎯")
                    except AIServiceError as e:
                        st.error(f"AI Service Error: {str(e)}")
                        st.warning("Please check your API key and settings.")
        
        # Display job match result if available
        if st.session_state.job_match_result:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><span>🎯</span> Job Match Analysis Results</div>', unsafe_allow_html=True)
            provider = st.session_state.job_match_result.get("provider", "AI Provider")
            model = st.session_state.job_match_result.get("model", "Unknown Model")
            st.markdown(f'<span class="badge">{provider}</span> <span class="badge">{model}</span>', unsafe_allow_html=True)
            tokens_used = st.session_state.job_match_result.get("tokens_used")
            if tokens_used:
                st.markdown(f'<span class="badge" style="background:#27ae60;">Tokens: {tokens_used}</span>', unsafe_allow_html=True)
            st.markdown('<hr style="margin:1rem 0;">', unsafe_allow_html=True)
            analysis_text = st.session_state.job_match_result.get("analysis", "No analysis available.")
            import re
            sections = re.split(r"\n\s*\d+\. ", analysis_text)
            if len(sections) > 1:
                for i, section in enumerate(sections):
                    if not section.strip():
                        continue
                    if i == 0:
                        continue
                    title = None
                    if i == 1:
                        title = '<div class="section-title strengths">✅ Match Score & Overview</div>'
                    elif i == 2:
                        title = '<div class="section-title strengths">🌟 Key Matching Qualifications</div>'
                    elif i == 3:
                        title = '<div class="section-title weaknesses">❌ Missing Skills/Requirements</div>'
                    elif i == 4:
                        title = '<div class="section-title suggestions">💡 Suggestions to Improve Match</div>'
                    elif i == 5:
                        title = '<div class="section-title suggestions">🔑 Keywords to Add</div>'
                    else:
                        title = f'<div class="section-title">Section {i}</div>'
                    st.markdown(title, unsafe_allow_html=True)
                    st.markdown(f'<div class="card-section">{section.strip()}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="card-section">{analysis_text}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("Include in PDF Report"):
                st.success("Job match analysis will be included in the PDF report. Go to the Analysis tab to generate the report.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div class="footer">
        <p>© 2024 <a href="https://github.com/INFINITYone22" target="_blank">@INFINITYone22</a>. All Rights Reserved.</p>
        <p><a href="https://github.com/INFINITYone22/resume-analyzer" target="_blank">GitHub Repository</a> | 
        <a href="https://github.com/INFINITYone22/resume-analyzer#readme" target="_blank">Documentation</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
