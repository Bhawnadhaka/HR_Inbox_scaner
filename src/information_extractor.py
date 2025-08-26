"""
Information extraction module for parsing candidate details from text
"""
import re
import logging
from typing import Dict, List, Optional
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InformationExtractor:
    """Extracts structured information from resume text and email content"""
    
    def __init__(self):
        """Initialize information extractor"""
        try:
            # Download required NLTK data if not present
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
        
        # Regex patterns for extraction
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.name_pattern = re.compile(r'^([A-Z][a-z]+\s+[A-Z][a-z]+)', re.MULTILINE)
        
        # Experience extraction patterns
        self.experience_patterns = [
            re.compile(r'(\d+)\+?\s*years?\s*(?:of\s*)?experience', re.IGNORECASE),
            re.compile(r'experience.*?(\d+)\+?\s*years?', re.IGNORECASE),
            re.compile(r'(\d+)\+?\s*years?\s*in', re.IGNORECASE),
            re.compile(r'over\s*(\d+)\s*years?', re.IGNORECASE),
            re.compile(r'more\s*than\s*(\d+)\s*years?', re.IGNORECASE)
        ]
        
        # Location patterns
        self.location_patterns = [
            re.compile(r'(?:Location|Address|Based|Located):\s*([A-Za-z\s,]+)', re.IGNORECASE),
            re.compile(r'([A-Za-z\s]+),\s*([A-Z]{2})\s*\d{5}', re.IGNORECASE),
            re.compile(r'([A-Za-z\s]+),\s*([A-Za-z\s]+)\s*,\s*([A-Za-z\s]+)', re.IGNORECASE)
        ]
    
    def extract_candidate_info(self, resume_text: str, email_data: Dict) -> Dict:
        """Extract comprehensive candidate information"""
        candidate_info = {
            'name': '',
            'email': '',
            'phone': '',
            'location': '',
            'years_of_experience': 0,
            'applied_position': '',
            'skills': [],
            'education': '',
            'raw_text_length': len(resume_text) if resume_text else 0,
            'extraction_source': 'resume' if resume_text else 'email'
        }
        
        # Use resume text if available, otherwise use email body
        text_to_analyze = resume_text if resume_text else email_data.get('body', '')
        
        if not text_to_analyze:
            logger.warning("No text available for extraction")
            return candidate_info
        
        # Extract basic information
        candidate_info['name'] = self._extract_name(text_to_analyze, email_data)
        candidate_info['email'] = self._extract_email(text_to_analyze, email_data)
        candidate_info['phone'] = self._extract_phone(text_to_analyze)
        candidate_info['location'] = self._extract_location(text_to_analyze)
        candidate_info['years_of_experience'] = self._extract_experience(text_to_analyze)
        candidate_info['applied_position'] = self._extract_applied_position(email_data)
        candidate_info['skills'] = self._extract_skills(text_to_analyze)
        candidate_info['education'] = self._extract_education(text_to_analyze)
        
        logger.info(f"Extracted info for candidate: {candidate_info['name']}")
        return candidate_info
    
    def _extract_name(self, text: str, email_data: Dict) -> str:
        """Extract candidate name"""
        # Try to extract name from email sender first
        sender = email_data.get('sender', '')
        if sender:
            # Extract name from email format "Name <email@domain.com>"
            name_match = re.search(r'^([^<]+)', sender)
            if name_match:
                name = name_match.group(1).strip()
                if not any(char in name for char in ['@', '.com', 'noreply']):
                    return name
        
        # Extract from resume text
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) > 3 and len(line) < 50:
                # Check if line looks like a name
                if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+', line):
                    return line
                
        # Try regex pattern on full text
        name_match = self.name_pattern.search(text)
        if name_match:
            return name_match.group(1)
        
        return "Unknown"
    
    def _extract_email(self, text: str, email_data: Dict) -> str:
        """Extract email address"""
        # First check email sender
        sender = email_data.get('sender', '')
        email_match = self.email_pattern.search(sender)
        if email_match:
            return email_match.group(0)
        
        # Then check resume text
        email_match = self.email_pattern.search(text)
        if email_match:
            return email_match.group(0)
        
        return ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        phone_match = self.phone_pattern.search(text)
        if phone_match:
            return phone_match.group(0)
        return ""
    
    def _extract_location(self, text: str) -> str:
        """Extract location/address"""
        for pattern in self.location_patterns:
            match = pattern.search(text)
            if match:
                return match.group(1).strip()
        
        # Look for common location indicators
        location_indicators = ['City:', 'Location:', 'Address:', 'Based in:', 'Located in:']
        for indicator in location_indicators:
            if indicator in text:
                start = text.find(indicator) + len(indicator)
                end = text.find('\n', start)
                if end == -1:
                    end = start + 50
                location = text[start:end].strip()
                if location:
                    return location
        
        return ""
    
    def _extract_experience(self, text: str) -> int:
        """Extract years of experience"""
        for pattern in self.experience_patterns:
            matches = pattern.findall(text)
            if matches:
                try:
                    # Get the highest number found
                    years = max(int(match) for match in matches if match.isdigit())
                    return min(years, 50)  # Cap at 50 years for sanity
                except ValueError:
                    continue
        
        # Look for date ranges to estimate experience
        date_pattern = re.compile(r'(19|20)\d{2}')
        dates = [int(match) for match in date_pattern.findall(text)]
        if len(dates) >= 2:
            current_year = 2024
            earliest_year = min(dates)
            if earliest_year > 1980 and earliest_year < current_year:
                estimated_experience = current_year - earliest_year
                return min(estimated_experience, 50)
        
        return 0
    
    def _extract_applied_position(self, email_data: Dict) -> str:
        """Extract applied position from email subject or body"""
        subject = email_data.get('subject', '').lower()
        
        # Common position keywords
        position_keywords = [
            'software engineer', 'developer', 'programmer', 'analyst',
            'manager', 'consultant', 'specialist', 'coordinator',
            'director', 'architect', 'designer', 'administrator'
        ]
        
        for keyword in position_keywords:
            if keyword in subject:
                return keyword.title()
        
        # Extract from subject line patterns
        position_patterns = [
            r'application for\s+(.+?)(?:\s|$)',
            r'applying for\s+(.+?)(?:\s|$)',
            r'position:\s*(.+?)(?:\s|$)',
            r'role:\s*(.+?)(?:\s|$)'
        ]
        
        for pattern in position_patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                position = match.group(1).strip()
                return position.title()
        
        return "General Position"
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        # Common technical skills
        common_skills = [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'SQL', 'HTML', 'CSS',
            'React', 'Angular', 'Node.js', 'Django', 'Flask', 'Spring Boot',
            'AWS', 'Azure', 'Docker', 'Kubernetes', 'Git', 'Linux', 'Windows',
            'Machine Learning', 'Data Science', 'AI', 'TensorFlow', 'PyTorch',
            'Salesforce', 'SAP', 'Oracle', 'MongoDB', 'PostgreSQL', 'MySQL'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills[:10]  # Limit to top 10 skills
    
    def _extract_education(self, text: str) -> str:
        """Extract education information"""
        education_keywords = [
            'bachelor', 'master', 'phd', 'degree', 'university', 'college',
            'btech', 'mtech', 'mba', 'bca', 'mca', 'diploma'
        ]
        
        text_lower = text.lower()
        
        for keyword in education_keywords:
            if keyword in text_lower:
                # Find the sentence containing the education keyword
                sentences = sent_tokenize(text)
                for sentence in sentences:
                    if keyword in sentence.lower():
                        return sentence.strip()[:100]  # Limit length
        
        return ""
