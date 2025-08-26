"""
Main application script for HR Inbox Scanner
"""
import os
import sys
import logging
from datetime import datetime
from typing import List, Dict

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.email_config import EmailConfig
from src.email_processor import EmailProcessor
from src.resume_parser import ResumeParser
from src.information_extractor import InformationExtractor
from src.candidate_rater import CandidateRater
from src.excel_manager import ExcelManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hr_scanner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HRInboxScanner:
    """Main HR Inbox Scanner application"""
    
    def __init__(self):
        """Initialize the HR Inbox Scanner"""
        self.email_processor = None
        self.resume_parser = ResumeParser()
        self.info_extractor = InformationExtractor()
        self.candidate_rater = CandidateRater()
        self.excel_manager = ExcelManager()
        
    def setup_email_connection(self) -> bool:
        """Setup email connection with user credentials"""
        print("\n" + "="*50)
        print("HR INBOX SCANNER - EMAIL SETUP")
        print("="*50)
        
        # Check if credentials are already configured
        if EmailConfig.is_configured():
            print("✓ Email credentials found in configuration")
            provider = "gmail" if "gmail" in EmailConfig.IMAP_HOST else "outlook"
        else:
            print("\nPlease enter your email credentials:")
            
            email_address = input("Email address: ").strip()
            
            # Determine provider
            if 'gmail' in email_address.lower():
                provider = 'gmail'
                print("✓ Detected Gmail account")
                print("NOTE: You need to use an App Password for Gmail")
                print("Generate one at: https://myaccount.google.com/apppasswords")
            elif 'outlook' in email_address.lower() or 'hotmail' in email_address.lower():
                provider = 'outlook'
                print("✓ Detected Outlook account")
            else:
                provider = input("Email provider (gmail/outlook): ").strip().lower()
            
            password = input("Password (or App Password for Gmail): ").strip()
            
            # Set credentials
            EmailConfig.set_credentials(email_address, password, provider)
        
        # Initialize email processor
        self.email_processor = EmailProcessor(EmailConfig)
        
        # Test connection
        print("\n🔗 Testing email connection...")
        if self.email_processor.connect():
            print("✅ Successfully connected to email server!")
            return True
        else:
            print("❌ Failed to connect to email server")
            print("Please check your credentials and try again")
            return False
    
    def process_applications(self) -> List[Dict]:
        """Process job applications from email inbox"""
        print("\n" + "="*50)
        print("PROCESSING JOB APPLICATIONS")
        print("="*50)
        
        candidates = []
        
        try:
            # Fetch application emails
            print("📧 Fetching job application emails...")
            application_emails = self.email_processor.fetch_application_emails()
            
            if not application_emails:
                print("📪 No new job application emails found")
                return candidates
            
            print(f"📬 Found {len(application_emails)} application emails")
            
            # Process each application
            for i, email_data in enumerate(application_emails, 1):
                print(f"\n📝 Processing application {i}/{len(application_emails)}")
                print(f"   From: {email_data['sender']}")
                print(f"   Subject: {email_data['subject']}")
                
                # Extract resume text if attachments exist
                resume_text = ""
                if email_data['attachments']:
                    print(f"   📎 Found {len(email_data['attachments'])} attachment(s)")
                    
                    for attachment in email_data['attachments']:
                        text = self.resume_parser.extract_text(attachment['path'])
                        if text:
                            resume_text += text + "\n"
                            print(f"   ✓ Extracted text from {attachment['filename']}")
                        else:
                            print(f"   ❌ Failed to extract text from {attachment['filename']}")
                
                # Extract candidate information
                candidate_info = self.info_extractor.extract_candidate_info(resume_text, email_data)
                
                # Rate candidate
                rated_candidate = self.candidate_rater.rate_candidate(candidate_info)
                
                candidates.append(rated_candidate)
                
                print(f"   ✓ Processed: {rated_candidate['name']} ({rated_candidate['experience_level']})")
                
                # Mark email as read
                self.email_processor.mark_as_read(email_data['email_id'])
            
            print(f"\n✅ Successfully processed {len(candidates)} candidates")
            
        except Exception as e:
            logger.error(f"Error processing applications: {str(e)}")
            print(f"❌ Error processing applications: {str(e)}")
        
        finally:
            # Disconnect from email server
            if self.email_processor:
                self.email_processor.disconnect()
        
        return candidates
    
    def save_to_excel(self, candidates: List[Dict]) -> bool:
        """Save candidates to Excel file"""
        print("\n" + "="*50)
        print("SAVING TO EXCEL")
        print("="*50)
        
        if not candidates:
            print("📝 No candidates to save")
            return False
        
        try:
            # Save candidates
            success = self.excel_manager.save_candidates(candidates)
            
            if success:
                excel_path = self.excel_manager.get_file_path()
                print(f"✅ Successfully saved {len(candidates)} candidates to Excel")
                print(f"📄 File location: {excel_path}")
                
                # Print summary statistics
                self.print_summary_statistics(candidates)
                
                return True
            else:
                print("❌ Failed to save candidates to Excel")
                return False
                
        except Exception as e:
            logger.error(f"Error saving to Excel: {str(e)}")
            print(f"❌ Error saving to Excel: {str(e)}")
            return False
    
    def print_summary_statistics(self, candidates: List[Dict]):
        """Print summary statistics"""
        print("\n" + "="*50)
        print("SUMMARY STATISTICS")
        print("="*50)
        
        if not candidates:
            return
        
        # Get summary from rater
        summary = self.candidate_rater.get_rating_summary(candidates)
        
        print(f"📊 Total Candidates: {summary['total_candidates']}")
        print(f"📈 Average Score: {summary['average_score']:.1f}/100")
        
        print("\n📋 Experience Level Distribution:")
        for level, count in summary['level_counts'].items():
            percentage = summary['level_percentages'][level]
            print(f"   {level:12}: {count:3d} candidates ({percentage:5.1f}%)")
        
        # Top candidates
        sorted_candidates = sorted(candidates, key=lambda x: x.get('overall_score', 0), reverse=True)
        print(f"\n🏆 Top 5 Candidates:")
        for i, candidate in enumerate(sorted_candidates[:5], 1):
            name = candidate.get('name', 'Unknown')
            score = candidate.get('overall_score', 0)
            level = candidate.get('experience_level', 'Unknown')
            print(f"   {i}. {name} - {score}/100 ({level})")
    
    def run(self):
        """Run the complete HR Inbox Scanner process"""
        print("🚀 Starting HR Inbox Scanner")
        print("="*60)
        
        try:
            # Setup email connection
            if not self.setup_email_connection():
                return False
            
            # Process applications
            candidates = self.process_applications()
            
            if candidates:
                # Save to Excel
                success = self.save_to_excel(candidates)
                
                if success:
                    print("\n🎉 HR Inbox Scanner completed successfully!")
                    print("Check the Excel file for detailed candidate information.")
                    
                    # Ask if user wants to open Excel file
                    excel_path = self.excel_manager.get_file_path()
                    open_file = input(f"\nWould you like to open the Excel file? (y/n): ").strip().lower()
                    if open_file == 'y':
                        os.startfile(excel_path)  # Windows specific
                    
                    return True
                else:
                    print("\n❌ Failed to save results")
                    return False
            else:
                print("\n📭 No candidates found to process")
                return True
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Process interrupted by user")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            print(f"\n❌ Unexpected error: {str(e)}")
            return False

def main():
    """Main entry point"""
    scanner = HRInboxScanner()
    scanner.run()

if __name__ == "__main__":
    main()
