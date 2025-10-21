"""
LLM-powered command parser for natural language Slack commands
"""
from openai import AzureOpenAI
from config import settings
import json
from typing import Dict, Any, Optional


class CommandParser:
    def __init__(self, api_key: str = None, endpoint: str = None, deployment: str = None):
        self.client = AzureOpenAI(
            api_key=api_key or settings.AZURE_OPENAI_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=endpoint or settings.AZURE_OPENAI_ENDPOINT
        )
        self.deployment = deployment or settings.AZURE_OPENAI_DEPLOYMENT
    
    async def parse_email_summary_command(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language email summary command
        Examples:
        - "get my emails from the last 3 days"
        - "show me yesterday's emails"
        - "summarize emails from Jan 1 to Jan 5"
        - "7 days" or just "3"
        """
        
        prompt = f"""Parse this email summary command and extract the time range.

Command: "{text}"

Extract:
- Number of days (if relative like "last 3 days", "yesterday", etc.)
- Or specific start_date and end_date (format: YYYY-MM-DD)

If the command is empty or just says "today", use 1 day.
If it's a number like "7" or "3", that's the number of days.

Respond in JSON format:
{{
    "days": <number or null>,
    "start_date": "<YYYY-MM-DD or null>",
    "end_date": "<YYYY-MM-DD or null>"
}}

Examples:
"last 7 days" -> {{"days": 7, "start_date": null, "end_date": null}}
"yesterday" -> {{"days": 1, "start_date": null, "end_date": null}}
"3" -> {{"days": 3, "start_date": null, "end_date": null}}
"from Jan 1 to Jan 5" -> {{"days": null, "start_date": "2025-01-01", "end_date": "2025-01-05"}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that parses email commands. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            content = content.strip()
            
            result = json.loads(content)
            return result
        except Exception as e:
            print(f"Error parsing email command: {e}")
            # Default to 1 day if parsing fails
            return {"days": 1, "start_date": None, "end_date": None}
    
    async def parse_schedule_command(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language meeting scheduling command
        Examples:
        - "meeting with john@example.com for 30 minutes"
        - "schedule with john@ex.com and jane@ex.com for 1 hour tomorrow at 2pm called Team Sync"
        - "john@ex.com,jane@ex.com 30 Project Review"
        """
        
        prompt = f"""Parse this meeting scheduling command and extract the details.

Command: "{text}"

Extract:
- attendees: list of email addresses
- duration_minutes: meeting duration in minutes
- title: meeting title/subject (optional)
- date: specific date (format: YYYY-MM-DD) or null for next available
- time: specific time (format: HH:MM) or null for next available

Respond in JSON format:
{{
    "attendees": ["email1@example.com", "email2@example.com"],
    "duration_minutes": 30,
    "title": "Meeting Title",
    "date": "YYYY-MM-DD or null",
    "time": "HH:MM or null"
}}

If date/time not specified, use null (system will find next available slot).
Default duration is 30 minutes if not specified.
Default title is "Meeting" if not specified.

Examples:
"john@ex.com for 30 minutes" -> {{"attendees": ["john@ex.com"], "duration_minutes": 30, "title": "Meeting", "date": null, "time": null}}
"meeting with john@ex.com and jane@ex.com for 1 hour tomorrow at 2pm called Team Sync" -> {{"attendees": ["john@ex.com", "jane@ex.com"], "duration_minutes": 60, "title": "Team Sync", "date": "2025-10-22", "time": "14:00"}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that parses meeting scheduling commands. Always respond with valid JSON only. Today's date is 2025-10-21."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            content = content.strip()
            
            result = json.loads(content)
            
            # Validate attendees
            if not result.get('attendees') or not isinstance(result['attendees'], list):
                raise ValueError("No attendees found")
            
            # Set defaults
            result['duration_minutes'] = result.get('duration_minutes', 30)
            result['title'] = result.get('title', 'Meeting')
            
            return result
        except Exception as e:
            print(f"Error parsing schedule command: {e}")
            raise ValueError(f"Could not parse command. Please use format: 'email@example.com for 30 minutes' or 'email1,email2 30 Meeting Title'")
