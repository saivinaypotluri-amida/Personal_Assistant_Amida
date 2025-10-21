from openai import AzureOpenAI
from config import settings
from typing import List, Dict, Any
import json


class LLMService:
    def __init__(self, api_key: str = None, endpoint: str = None, deployment: str = None):
        self.client = AzureOpenAI(
            api_key=api_key or settings.AZURE_OPENAI_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=endpoint or settings.AZURE_OPENAI_ENDPOINT
        )
        self.deployment = deployment or settings.AZURE_OPENAI_DEPLOYMENT
    
    async def summarize_email(self, email_content: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize email content in 30-40 words and extract meeting links"""
        
        prompt = f"""Analyze the following email and provide:
1. A concise summary in 30-40 words
2. Extract any meeting links (Zoom, Google Meet, Teams, etc.) found in the email

Email Details:
Subject: {email_content.get('subject', 'N/A')}
From: {email_content.get('from', 'N/A')}
Body: {email_content.get('body', 'N/A')[:2000]}

Respond in JSON format:
{{
    "summary": "your 30-40 word summary here",
    "meeting_links": ["link1", "link2"]
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a helpful email assistant that summarizes emails concisely and extracts meeting information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            tokens_used = response.usage.total_tokens
            
            return {
                "summary": result.get("summary", ""),
                "meeting_links": result.get("meeting_links", []),
                "tokens_used": tokens_used
            }
        except Exception as e:
            print(f"Error in summarize_email: {e}")
            return {
                "summary": "Error summarizing email.",
                "meeting_links": [],
                "tokens_used": 0
            }
    
    async def format_email_digest(self, summaries: List[Dict[str, Any]]) -> str:
        """Format email summaries into a nice HTML email digest"""
        
        html = """
        <html>
        <head>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }
                .email-item {
                    background: #f8f9fa;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 5px;
                }
                .email-header {
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 5px;
                }
                .email-meta {
                    color: #7f8c8d;
                    font-size: 0.9em;
                    margin-bottom: 10px;
                }
                .email-summary {
                    margin: 10px 0;
                }
                .meeting-links {
                    margin-top: 10px;
                    padding: 10px;
                    background: #e8f4f8;
                    border-radius: 3px;
                }
                .meeting-links a {
                    color: #3498db;
                    text-decoration: none;
                    display: block;
                    margin: 5px 0;
                }
                .meeting-links a:hover {
                    text-decoration: underline;
                }
                .footer {
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #7f8c8d;
                    font-size: 0.9em;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <h1>📧 Daily Email Digest</h1>
        """
        
        if not summaries:
            html += "<p>No emails found for the specified period.</p>"
        else:
            html += f"<p>You have <strong>{len(summaries)}</strong> emails to review:</p>"
            
            for idx, email in enumerate(summaries, 1):
                html += f"""
                <div class="email-item">
                    <div class="email-header">{idx}. {email.get('subject', 'No Subject')}</div>
                    <div class="email-meta">From: {email.get('from', 'Unknown')} | Date: {email.get('date', 'N/A')}</div>
                    <div class="email-summary">{email.get('summary', 'No summary available')}</div>
                """
                
                if email.get('meeting_links'):
                    html += '<div class="meeting-links"><strong>📅 Meeting Links:</strong><br>'
                    for link in email['meeting_links']:
                        html += f'<a href="{link}" target="_blank">{link}</a>'
                    html += '</div>'
                
                html += "</div>"
        
        html += """
            <div class="footer">
                <p>This digest was generated by Amida AI Personal Assistant</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    async def format_slack_message(self, summaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format email summaries for Slack using Block Kit"""
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📧 Daily Email Digest",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"You have *{len(summaries)}* emails to review:"
                }
            },
            {"type": "divider"}
        ]
        
        for idx, email in enumerate(summaries[:10], 1):  # Limit to 10 for Slack
            email_block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{idx}. {email.get('subject', 'No Subject')}*\n"
                            f"_From: {email.get('from', 'Unknown')} | {email.get('date', 'N/A')}_\n"
                            f"{email.get('summary', 'No summary available')}"
                }
            }
            blocks.append(email_block)
            
            if email.get('meeting_links'):
                links_text = "\n".join([f"• <{link}|Join Meeting>" for link in email['meeting_links']])
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"📅 *Meeting Links:*\n{links_text}"
                    }
                })
            
            blocks.append({"type": "divider"})
        
        if len(summaries) > 10:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_...and {len(summaries) - 10} more emails_"
                }
            })
        
        return blocks
