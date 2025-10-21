from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re


class GmailService:
    def __init__(self, credentials_dict: Dict[str, Any]):
        """Initialize Gmail service with OAuth credentials"""
        creds = Credentials(
            token=credentials_dict.get('access_token'),
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=credentials_dict.get('client_id'),
            client_secret=credentials_dict.get('client_secret')
        )
        self.service = build('gmail', 'v1', credentials=creds)
    
    async def get_emails(self, days: Optional[int] = None, 
                        start_date: Optional[str] = None, 
                        end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail based on date range"""
        
        # Build query
        query = ""
        
        if days:
            after_date = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
            query = f"after:{after_date}"
        elif start_date and end_date:
            query = f"after:{start_date} before:{end_date}"
        elif start_date:
            query = f"after:{start_date}"
        else:
            # Default to today
            after_date = datetime.now().strftime('%Y/%m/%d')
            query = f"after:{after_date}"
        
        query += " -in:sent -in:draft -in:spam -in:trash"
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=100
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email_data = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                headers = email_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                # Extract body
                body = self._get_email_body(email_data['payload'])
                
                emails.append({
                    'id': msg['id'],
                    'subject': subject,
                    'from': from_email,
                    'date': date,
                    'body': body
                })
            
            return emails
        
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def _get_email_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        html_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        # Strip HTML tags for summary
                        body = re.sub('<[^<]+?>', '', html_body)
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body[:2000]  # Limit body length
    
    async def send_email(self, to: str, subject: str, html_content: str) -> bool:
        """Send an email via Gmail"""
        
        try:
            message = MIMEMultipart('alternative')
            message['to'] = to
            message['subject'] = subject
            
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            return True
        
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    async def get_user_email(self) -> str:
        """Get the authenticated user's email address"""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile['emailAddress']
        except Exception as e:
            print(f"Error getting user email: {e}")
            return ""
