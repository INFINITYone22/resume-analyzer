from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from typing import Dict, List, Any, Optional
import io
import os
import datetime

# Try to import visualization packages, but don't fail if they're not available
try:
    import matplotlib.pyplot as plt
    import numpy as np
    from wordcloud import WordCloud
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

def generate_skill_wordcloud(skills: List[str], title: str = "Skills") -> Optional[str]:
    """Generate a word cloud image from the skills list."""
    if not skills or not VISUALIZATION_AVAILABLE:
        return None
        
    # Create text for wordcloud
    text = " ".join(skills)
    
    try:
        # Generate the wordcloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            colormap='viridis',
            max_words=100,
            min_font_size=10
        ).generate(text)
        
        # Create a temporary file to save the image
        img_path = f"temp_{title.lower().replace(' ', '_')}_wordcloud.png"
        
        # Save the wordcloud image
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.title(title)
        plt.tight_layout()
        plt.savefig(img_path)
        plt.close()
        
        return img_path
    except Exception as e:
        print(f"Error generating wordcloud: {e}")
        return None

def generate_analysis_report(
    resume_text: str,
    analysis_result: Dict[str, Any],
    extracted_skills: Optional[Dict[str, List[str]]] = None,
    extracted_sections: Optional[Dict[str, str]] = None,
    job_match_result: Optional[Dict[str, Any]] = None
) -> bytes:
    """
    Generate a PDF report with resume analysis results.
    
    Args:
        resume_text: The extracted resume text
        analysis_result: The AI analysis results
        extracted_skills: Optional dictionary of extracted skills
        extracted_sections: Optional dictionary of extracted resume sections
        job_match_result: Optional job match analysis results
        
    Returns:
        PDF report as bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='Heading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.darkblue,
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='Heading3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.darkblue,
        spaceAfter=6
    ))
    
    styles.add(ParagraphStyle(
        name='Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    ))
    
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,  # Center alignment
        textColor=colors.gray
    ))
    
    # List of elements to add to the document
    elements = []
    
    # Title and date
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"Resume Analysis Report", styles['Title']))
    elements.append(Paragraph(f"Generated on {current_date}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # If skills were extracted, add skills section with wordclouds
    if extracted_skills:
        tech_skills = extracted_skills.get("technical_skills", [])
        soft_skills = extracted_skills.get("soft_skills", [])
        
        if tech_skills or soft_skills:
            elements.append(Paragraph("Skills Analysis", styles['Heading2']))
            
            if tech_skills:
                elements.append(Paragraph("Technical Skills", styles['Heading3']))
                tech_skills_text = ", ".join(tech_skills)
                elements.append(Paragraph(tech_skills_text, styles['Normal']))
                
                # Generate wordcloud for technical skills
                tech_cloud_path = generate_skill_wordcloud(tech_skills, "Technical Skills")
                if tech_cloud_path and os.path.exists(tech_cloud_path):
                    elements.append(Image(tech_cloud_path, width=6*inch, height=3*inch))
                    # Mark for cleanup later
                
            if soft_skills:
                elements.append(Paragraph("Soft Skills", styles['Heading3']))
                soft_skills_text = ", ".join(soft_skills)
                elements.append(Paragraph(soft_skills_text, styles['Normal']))
                
                # Generate wordcloud for soft skills
                soft_cloud_path = generate_skill_wordcloud(soft_skills, "Soft Skills")
                if soft_cloud_path and os.path.exists(soft_cloud_path):
                    elements.append(Image(soft_cloud_path, width=6*inch, height=3*inch))
                    # Mark for cleanup later
            
            elements.append(Spacer(1, 0.2*inch))
    
    # AI Analysis
    elements.append(Paragraph("AI-Powered Analysis", styles['Heading2']))
    
    if analysis_result:
        # Provider info
        provider = analysis_result.get("provider", "AI Provider")
        model = analysis_result.get("model", "Unknown Model")
        elements.append(Paragraph(f"Analysis by: {provider} ({model})", styles['Normal']))
        
        # Format analysis text with proper styling
        analysis_text = analysis_result.get("analysis", "No analysis was provided.")
        
        # Split by sections and add proper formatting
        sections = analysis_text.split("\n\n")
        for section in sections:
            if section.strip():
                # Check if it's a numbered section like "1. Something"
                if section.strip()[0].isdigit() and ". " in section[:5]:
                    # This is likely a heading
                    title, *content = section.split("\n", 1)
                    elements.append(Paragraph(title.strip(), styles['Heading3']))
                    if content:
                        elements.append(Paragraph(content[0].strip(), styles['Normal']))
                else:
                    elements.append(Paragraph(section.strip(), styles['Normal']))
    
    # Job match analysis if available
    if job_match_result:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Job Match Analysis", styles['Heading2']))
        
        match_analysis = job_match_result.get("analysis", "No job match analysis available.")
        
        # Split by sections and add proper formatting
        sections = match_analysis.split("\n\n")
        for section in sections:
            if section.strip():
                # Check if it's a numbered section like "1. Something"
                if section.strip()[0].isdigit() and ". " in section[:5]:
                    # This is likely a heading
                    title, *content = section.split("\n", 1)
                    elements.append(Paragraph(title.strip(), styles['Heading3']))
                    if content:
                        elements.append(Paragraph(content[0].strip(), styles['Normal']))
                else:
                    elements.append(Paragraph(section.strip(), styles['Normal']))
    
    # Add copyright footer
    elements.append(Spacer(1, 0.5*inch))
    copyright_text = "© 2024 @INFINITYone22 (https://github.com/INFINITYone22). All Rights Reserved."
    elements.append(Paragraph(copyright_text, styles['Footer']))
    
    # Build the PDF
    doc.build(elements)
    
    # Clean up temporary files
    for filename in os.listdir('.'):
        if filename.startswith('temp_') and filename.endswith('_wordcloud.png'):
            try:
                os.remove(filename)
            except:
                pass
    
    # Get the PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data 