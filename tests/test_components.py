"""
Basic tests for HR Inbox Scanner components
"""
import unittest
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.resume_parser import ResumeParser
from src.information_extractor import InformationExtractor
from src.candidate_rater import CandidateRater

class TestResumeParser(unittest.TestCase):
    """Test cases for ResumeParser"""
    
    def setUp(self):
        self.parser = ResumeParser()
    
    def test_is_valid_resume(self):
        """Test resume validation"""
        valid_text = "John Doe has 5 years of experience in software development. He graduated from XYZ University with a degree in Computer Science. His skills include Python, Java, and SQL."
        invalid_text = "Short text"
        
        self.assertTrue(self.parser.is_valid_resume(valid_text))
        self.assertFalse(self.parser.is_valid_resume(invalid_text))

class TestInformationExtractor(unittest.TestCase):
    """Test cases for InformationExtractor"""
    
    def setUp(self):
        self.extractor = InformationExtractor()
    
    def test_extract_email(self):
        """Test email extraction"""
        text = "Contact me at john.doe@email.com for more information"
        email_data = {'sender': 'John Doe <john.doe@email.com>'}
        
        email = self.extractor._extract_email(text, email_data)
        self.assertEqual(email, 'john.doe@email.com')
    
    def test_extract_experience(self):
        """Test experience extraction"""
        text = "I have 5 years of experience in software development"
        
        years = self.extractor._extract_experience(text)
        self.assertEqual(years, 5)

class TestCandidateRater(unittest.TestCase):
    """Test cases for CandidateRater"""
    
    def setUp(self):
        self.rater = CandidateRater()
    
    def test_categorize_experience(self):
        """Test experience categorization"""
        self.assertEqual(self.rater._categorize_experience(1), 'Junior')
        self.assertEqual(self.rater._categorize_experience(3), 'Mid-level')
        self.assertEqual(self.rater._categorize_experience(7), 'Senior')
    
    def test_calculate_overall_score(self):
        """Test overall score calculation"""
        candidate_info = {
            'years_of_experience': 5,
            'skills': ['Python', 'Java', 'SQL'],
            'education': 'Bachelor of Computer Science',
            'email': 'john@email.com',
            'phone': '123-456-7890',
            'location': 'New York'
        }
        
        score = self.rater._calculate_overall_score(candidate_info)
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)

if __name__ == '__main__':
    unittest.main()
