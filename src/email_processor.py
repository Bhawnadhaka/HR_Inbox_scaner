"""
Email processing module for fetching and parsing emails
"""
import imaplib
import email
import os
import re
from datetime import datetime
from typing import List, Dict, Tuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailProcessor:
    """Handles email fetching and processing operations"""
    
    def __init__(self, config):
        """Initialize with email configuration"""
        self.config = config
        self.imap_conn = None
        
    def connect(self) -> bool:
        """Connect to email server using IMAP"""
        try:
            logger.info(f"Connecting to {self.config.IMAP_HOST}...")
            self.imap_conn = imaplib.IMAP4_SSL(self.config.IMAP_HOST, self.config.IMAP_PORT)
            self.imap_conn.login(self.config.EMAIL_ADDRESS, self.config.EMAIL_PASSWORD)
            logger.info("Successfully connected to email server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to email server: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from email server"""
        if self.imap_conn:
            try:
                self.imap_conn.close()
                self.imap_conn.logout()
                logger.info("Disconnected from email server")
            except:
                pass
    
    def fetch_application_emails(self) -> List[Dict]:
        """Fetch emails that appear to be job applications"""
        if not self.imap_conn:
            logger.error("Not connected to email server")
            return []
        
        try:
            # Select inbox
            self.imap_conn.select(self.config.INBOX_FOLDER)
            
            # Search for unread emails
            status, messages = self.imap_conn.search(None, self.config.SEARCH_CRITERIA)
            
            if status != 'OK':
                logger.error("Failed to search emails")
                return []
            
            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} unread emails")
            
            application_emails = []
            
            for email_id in email_ids:
                try:
                    # Fetch email
                    status, msg_data = self.imap_conn.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    email_msg = email.message_from_bytes(msg_data[0][1])
                    
                    # Check if this looks like a job application
                    if self._is_job_application(email_msg):
                        email_data = self._extract_email_data(email_msg, email_id)
                        if email_data:
                            application_emails.append(email_data)
                            logger.info(f"Found application email from: {email_data['sender']}")
                
                except Exception as e:
                    logger.error(f"Error processing email {email_id}: {str(e)}")
                    continue
            
            logger.info(f"Found {len(application_emails)} job application emails")
            return application_emails
            
        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            return []
    
    def _is_job_application(self, email_msg) -> bool:
        """Check if email appears to be a job application"""
        # Check subject line
        subject = email_msg.get('Subject', '').lower()
        
        # Check for application keywords in subject
        for keyword in self.config.APPLICATION_KEYWORDS:
            if keyword in subject:
                return True
        
        # Check email body (first part only for performance)
        body = self._get_email_body(email_msg).lower()
        
        # Count keyword matches in body
        keyword_count = sum(1 for keyword in self.config.APPLICATION_KEYWORDS if keyword in body)
        
        # Consider it an application if multiple keywords are present
        return keyword_count >= 2
    
    def _extract_email_data(self, email_msg, email_id) -> Dict:
        """Extract relevant data from email message"""
        try:
            email_data = {
                'email_id': email_id.decode() if isinstance(email_id, bytes) else email_id,
                'sender': email_msg.get('From', ''),
                'subject': email_msg.get('Subject', ''),
                'date': email_msg.get('Date', ''),
                'body': self._get_email_body(email_msg),
                'attachments': []
            }
            
            # Extract attachments
            for part in email_msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename and any(filename.lower().endswith(ext) for ext in self.config.RESUME_EXTENSIONS):
                        # Save attachment
                        attachment_path = self._save_attachment(part, filename, email_data['email_id'])
                        if attachment_path:
                            email_data['attachments'].append({
                                'filename': filename,
                                'path': attachment_path
                            })
            
            return email_data
            
        except Exception as e:
            logger.error(f"Error extracting email data: {str(e)}")
            return None
    
    def _get_email_body(self, email_msg) -> str:
        """Extract email body text"""
        body = ""
        
        if email_msg.is_multipart():
            for part in email_msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))
                
                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8')
                        break
                    except:
                        continue
        else:
            try:
                body = email_msg.get_payload(decode=True).decode('utf-8')
            except:
                body = str(email_msg.get_payload())
        
        return body
    
    def _save_attachment(self, part, filename: str, email_id: str) -> str:
        """Save email attachment to disk"""
        try:
            # Create unique filename to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{email_id}_{timestamp}_{filename}"
            
            # Ensure data directory exists
            data_dir = os.path.join(os.getcwd(), 'data', 'processed_emails')
            os.makedirs(data_dir, exist_ok=True)
            
            filepath = os.path.join(data_dir, safe_filename)
            
            # Save file
            with open(filepath, 'wb') as f:
                f.write(part.get_payload(decode=True))
            
            logger.info(f"Saved attachment: {safe_filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving attachment {filename}: {str(e)}")
            return None
    
    def mark_as_read(self, email_id: str):
        """Mark email as read"""
        try:
            if self.imap_conn:
                self.imap_conn.store(email_id, '+FLAGS', '\\Seen')
        except Exception as e:
            logger.error(f"Error marking email {email_id} as read: {str(e)}")
