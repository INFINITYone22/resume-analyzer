import unittest
import os
import io
from app.utils.parse_resume import extract_resume_text, extract_resume_sections
from app.nlp.skill_extractor import extract_skills
from app.utils.ai_services import validate_api_key, AIProvider
from app.utils.report_generator import generate_analysis_report

class TestIntegration(unittest.TestCase):
    """Integration tests for the resume analyzer application."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_resume_text = """
        JOHN DOE
        Software Developer
        Email: john.doe@example.com | Phone: (123) 456-7890
        
        EXPERIENCE
        Senior Software Developer, ABC Tech
        - Developed applications using Python and JavaScript
        - Led a team of 5 developers
        
        EDUCATION
        Bachelor of Science in Computer Science
        
        SKILLS
        Python, JavaScript, React, Node.js, Git, Docker, Kubernetes
        """
        
        self.sample_analysis_result = {
            "analysis": "This is a strong resume that effectively showcases technical skills and experience.",
            "provider": "Test Provider",
            "model": "Test Model",
            "tokens_used": 150
        }
        
        self.sample_job_match_result = {
            "analysis": "This resume matches 80% of the job requirements.",
            "provider": "Test Provider",
            "model": "Test Model",
            "tokens_used": 120
        }
    
    def test_end_to_end_extraction_flow(self):
        """Test the entire extraction process from text to skills."""
        # First extract sections from the resume
        sections = extract_resume_sections(self.sample_resume_text)
        
        # Verify sections were extracted correctly
        self.assertIn("experience", sections)
        self.assertIn("education", sections)
        self.assertIn("skills", sections)
        
        # Extract skills from the resume
        skills = extract_skills(self.sample_resume_text)
        
        # Verify skills were extracted correctly
        self.assertIn("technical_skills", skills)
        self.assertIn("soft_skills", skills)
        
        # Check specific skills were found
        tech_skills = skills["technical_skills"]
        self.assertTrue(any(skill in tech_skills for skill in ["python", "javascript", "react"]))
    
    def test_pdf_report_generation(self):
        """Test PDF report generation with sample data."""
        # Extract sections from the resume
        sections = extract_resume_sections(self.sample_resume_text)
        
        # Extract skills from the resume
        skills = extract_skills(self.sample_resume_text)
        
        # Generate a PDF report
        pdf_data = generate_analysis_report(
            resume_text=self.sample_resume_text,
            analysis_result=self.sample_analysis_result,
            extracted_skills=skills,
            extracted_sections=sections,
            job_match_result=self.sample_job_match_result
        )
        
        # Verify PDF was generated
        self.assertIsInstance(pdf_data, bytes)
        self.assertTrue(len(pdf_data) > 0)
        self.assertTrue(pdf_data.startswith(b'%PDF'))
    
    def test_api_integration_readiness(self):
        """Test that the API integration is ready to use with valid keys."""
        # Test OpenAI key validation
        valid_openai_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
        self.assertTrue(validate_api_key(AIProvider.OPENAI.value, valid_openai_key))
        
        # Test invalid key
        invalid_key = "invalid-key"
        self.assertFalse(validate_api_key(AIProvider.OPENAI.value, invalid_key))

if __name__ == "__main__":
    unittest.main() 