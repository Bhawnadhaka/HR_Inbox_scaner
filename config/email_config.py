"""
Email configuration settings for HR inbox scanning
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailConfig:
    """Email configuration class"""
    
    # Gmail IMAP settings
    GMAIL_IMAP_HOST = "imap.gmail.com"
    GMAIL_IMAP_PORT = 993
    
    # Outlook IMAP settings  
    OUTLOOK_IMAP_HOST = "outlook.office365.com"
    OUTLOOK_IMAP_PORT = 993
    
    # Default settings (using Gmail)
    IMAP_HOST = GMAIL_IMAP_HOST
    IMAP_PORT = GMAIL_IMAP_PORT
    
    # Email credentials (will be set from environment or user input)
    EMAIL_ADDRESS = os.getenv('HR_EMAIL_ADDRESS', '')
    EMAIL_PASSWORD = os.getenv('HR_EMAIL_PASSWORD', '')
    
    # Email filtering settings
    INBOX_FOLDER = 'INBOX'
    SEARCH_CRITERIA = 'UNSEEN'  # Only unread emails
    
    # Keywords to identify job applications
    APPLICATION_KEYWORDS = [
        'application', 'apply', 'resume', 'cv', 'position', 
        'job', 'vacancy', 'opportunity', 'interested', 'candidate'
    ]
    
    # Supported file extensions for resumes
    RESUME_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt']
    
    @classmethod
    def set_credentials(cls, email, password, provider='gmail'):
        """Set email credentials dynamically"""
        cls.EMAIL_ADDRESS = email
        cls.EMAIL_PASSWORD = password
        
        if provider.lower() == 'outlook':
            cls.IMAP_HOST = cls.OUTLOOK_IMAP_HOST
            cls.IMAP_PORT = cls.OUTLOOK_IMAP_PORT
        else:
            cls.IMAP_HOST = cls.GMAIL_IMAP_HOST
            cls.IMAP_PORT = cls.GMAIL_IMAP_PORT
    
    @classmethod
    def is_configured(cls):
        """Check if email credentials are configured"""
        return bool(cls.EMAIL_ADDRESS and cls.EMAIL_PASSWORD)
