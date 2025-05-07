import unittest
from app.nlp.skill_extractor import extract_skills

class TestSkillExtractor(unittest.TestCase):
    """Test cases for skill extraction functionality."""
    
    def test_empty_text(self):
        """Test skill extraction with empty text."""
        result = extract_skills("")
        self.assertEqual(result["technical_skills"], [])
        self.assertEqual(result["soft_skills"], [])
    
    def test_technical_skills(self):
        """Test extraction of technical skills."""
        text = """
        I have 5 years of experience in Python programming, developing web applications 
        with Flask and Django. I'm also proficient in JavaScript, React, and Node.js.
        Database experience includes working with PostgreSQL and MongoDB.
        """
        
        result = extract_skills(text)
        tech_skills = result["technical_skills"]
        
        # Check for expected skills
        self.assertIn("python", tech_skills)
        self.assertIn("javascript", tech_skills)
        self.assertIn("flask", tech_skills)
        self.assertIn("django", tech_skills)
        self.assertIn("react", tech_skills)
        self.assertIn("node.js", tech_skills)
        self.assertIn("postgresql", tech_skills)
        self.assertIn("mongodb", tech_skills)
    
    def test_soft_skills(self):
        """Test extraction of soft skills."""
        text = """
        I have strong leadership and communication skills, with experience managing teams 
        of up to 10 developers. My problem solving abilities have been crucial in delivering 
        projects on time and within budget. I excel at stakeholder management and have 
        excellent time management skills.
        """
        
        result = extract_skills(text)
        soft_skills = result["soft_skills"]
        
        # Check for expected skills
        self.assertIn("leadership", soft_skills)
        self.assertIn("communication", soft_skills)
        self.assertIn("management", soft_skills)
        self.assertIn("problem solving", soft_skills)
        self.assertIn("time management", soft_skills)
    
    def test_skills_in_sections(self):
        """Test extraction of skills from a formal skills section."""
        text = """
        SKILLS
        
        Technical Skills: Python, Java, C++, SQL, Git, Docker, Kubernetes
        Frameworks: React, Angular, Django, Spring Boot
        Soft Skills: Leadership, Communication, Teamwork, Problem Solving
        """
        
        result = extract_skills(text)
        tech_skills = result["technical_skills"]
        soft_skills = result["soft_skills"]
        
        # Check for expected technical skills
        self.assertIn("python", tech_skills)
        self.assertIn("java", tech_skills)
        self.assertIn("sql", tech_skills)
        self.assertIn("git", tech_skills)
        self.assertIn("docker", tech_skills)
        self.assertIn("kubernetes", tech_skills)
        self.assertIn("react", tech_skills)
        self.assertIn("angular", tech_skills)
        self.assertIn("django", tech_skills)
        
        # Check for expected soft skills
        self.assertIn("leadership", soft_skills)
        self.assertIn("communication", soft_skills)
        self.assertIn("teamwork", soft_skills)
        self.assertIn("problem solving", soft_skills)

if __name__ == "__main__":
    unittest.main() 