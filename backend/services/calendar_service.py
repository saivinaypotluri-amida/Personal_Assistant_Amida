from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pytz


class CalendarService:
    def __init__(self, credentials_dict: Dict[str, Any]):
        """Initialize Google Calendar service with OAuth credentials"""
        creds = Credentials(
            token=credentials_dict.get('access_token'),
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=credentials_dict.get('client_id'),
            client_secret=credentials_dict.get('client_secret')
        )
        self.service = build('calendar', 'v3', credentials=creds)
    
    async def find_next_available_slot(self, attendees: List[str], 
                                      duration_minutes: int) -> Optional[Dict[str, Any]]:
        """Find the next available time slot for all attendees"""
        
        # Check business hours for the next 7 days
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=7)).isoformat() + 'Z'
        
        # Get free/busy information for all attendees
        body = {
            "timeMin": time_min,
            "timeMax": time_max,
            "items": [{"id": email} for email in attendees]
        }
        
        try:
            freebusy = self.service.freebusy().query(body=body).execute()
            
            # Find common free slots
            start_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            
            # Only check business hours (9 AM - 5 PM)
            for day in range(7):
                check_date = start_time + timedelta(days=day)
                
                for hour in range(9, 17):  # 9 AM to 5 PM
                    slot_start = check_date.replace(hour=hour)
                    slot_end = slot_start + timedelta(minutes=duration_minutes)
                    
                    # Skip if slot extends beyond business hours
                    if slot_end.hour >= 17:
                        continue
                    
                    # Check if slot is free for all attendees
                    is_free = True
                    for attendee in attendees:
                        busy_times = freebusy['calendars'].get(attendee, {}).get('busy', [])
                        
                        for busy in busy_times:
                            busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                            busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                            
                            # Check for overlap
                            if (slot_start < busy_end.replace(tzinfo=None) and 
                                slot_end > busy_start.replace(tzinfo=None)):
                                is_free = False
                                break
                        
                        if not is_free:
                            break
                    
                    if is_free and slot_start > datetime.utcnow():
                        return {
                            'start': slot_start.isoformat() + 'Z',
                            'end': slot_end.isoformat() + 'Z'
                        }
            
            return None
        
        except Exception as e:
            print(f"Error finding available slot: {e}")
            return None
    
    async def check_conflicts(self, attendees: List[str], 
                             start_time: str, end_time: str) -> List[str]:
        """Check for scheduling conflicts for given attendees"""
        
        conflicts = []
        
        body = {
            "timeMin": start_time,
            "timeMax": end_time,
            "items": [{"id": email} for email in attendees]
        }
        
        try:
            freebusy = self.service.freebusy().query(body=body).execute()
            
            for attendee in attendees:
                busy_times = freebusy['calendars'].get(attendee, {}).get('busy', [])
                if busy_times:
                    conflicts.append(attendee)
            
            return conflicts
        
        except Exception as e:
            print(f"Error checking conflicts: {e}")
            return []
    
    async def create_meeting(self, title: str, description: str, 
                           attendees: List[str], start_time: str, 
                           end_time: str) -> Optional[Dict[str, Any]]:
        """Create a calendar event/meeting"""
        
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
            'attendees': [{'email': email} for email in attendees],
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{datetime.utcnow().timestamp()}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        
        try:
            event = self.service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()
            
            return {
                'id': event['id'],
                'link': event.get('htmlLink'),
                'hangout_link': event.get('hangoutLink')
            }
        
        except Exception as e:
            print(f"Error creating meeting: {e}")
            return None
