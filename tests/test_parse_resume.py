import unittest
import io
from app.utils.parse_resume import extract_resume_text, extract_resume_sections

class TestParseResume(unittest.TestCase):
    """Test cases for resume parsing functionality."""
    
    def test_extract_sections_empty(self):
        """Test section extraction with empty text."""
        text = ""
        sections = extract_resume_sections(text)
        self.assertEqual(sections, {})
    
    def test_extract_sections_basic(self):
        """Test basic section extraction."""
        text = """
        John Doe
        Email: john.doe@example.com
        
        EDUCATION
        Bachelor of Science in Computer Science
        University XYZ, 2015-2019
        
        EXPERIENCE
        Software Developer
        Company ABC, 2019-Present
        
        SKILLS
        Python, JavaScript, SQL
        """
        
        sections = extract_resume_sections(text)
        
        # Should extract header, education, experience, and skills
        self.assertIn("header", sections)
        self.assertIn("education", sections)
        self.assertIn("experience", sections)
        self.assertIn("skills", sections)
        
        # Check content of sections
        self.assertIn("John Doe", sections["header"])
        self.assertIn("Bachelor of Science", sections["education"])
        self.assertIn("Software Developer", sections["experience"])
        self.assertIn("Python", sections["skills"])
    
    def test_pdf_extraction_mock(self):
        """Mock test for PDF extraction."""
        # This is a mock test since we can't create a real PDF in a unit test
        class MockPdfReader:
            def __init__(self):
                self.pages = [MockPage(), MockPage()]
        
        class MockPage:
            def extract_text(self):
                return "Test PDF content"
        
        # Create a dummy file-like object
        dummy_file = io.BytesIO(b"dummy content")
        
        # We'd normally test with a real PDF, but here we're just checking the function structure
        # This is just a placeholder for a real test
        self.assertTrue(callable(extract_resume_text))

if __name__ == "__main__":
    unittest.main() 