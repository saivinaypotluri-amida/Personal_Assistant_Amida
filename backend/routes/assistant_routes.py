from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from database import get_db
from models import User, Credential, ActivityLog, CostTracking, OAuthConfig as OAuthConfigModel
from schemas import (
    EmailSummaryRequest,
    EmailSummaryResponse,
    EmailSummary,
    MeetingScheduleRequest,
    MeetingScheduleResponse
)
from auth import get_current_user
from services.gmail_service import GmailService
from services.calendar_service import CalendarService
from services.llm_service import LLMService
from services.slack_service import SlackService

router = APIRouter(prefix="/api/assistant", tags=["Assistant"])


def get_credential(db: Session, user_id: int, service: str) -> Credential:
    """Get user credential for a service"""
    cred = db.query(Credential).filter(
        Credential.user_id == user_id,
        Credential.service_name == service
    ).first()
    
    if not cred:
        raise HTTPException(status_code=400, detail=f"{service} not connected. Please authenticate first.")
    
    return cred


def log_activity(db: Session, user_id: int, action: str, source: str, status: str, details: dict = None):
    """Log user activity"""
    log = ActivityLog(
        user_id=user_id,
        action=action,
        source=source,
        status=status,
        details=details
    )
    db.add(log)
    db.commit()


def track_cost(db: Session, user_id: int, service: str, operation: str, tokens: int):
    """Track API costs"""
    # Rough estimate: $0.002 per 1K tokens for GPT-4
    cost = (tokens / 1000) * 0.002
    
    cost_entry = CostTracking(
        user_id=user_id,
        service=service,
        operation=operation,
        tokens_used=tokens,
        estimated_cost=cost
    )
    db.add(cost_entry)
    db.commit()


@router.post("/email-summary", response_model=EmailSummaryResponse)
async def summarize_emails(
    request: EmailSummaryRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Summarize emails and send daily digest"""
    
    try:
        # Get credentials
        google_cred = get_credential(db, current_user.id, "google")
        
        # Initialize services
        gmail_service = GmailService({
            'access_token': google_cred.access_token,
            'refresh_token': google_cred.refresh_token,
            'client_id': google_cred.additional_data.get('client_id'),
            'client_secret': google_cred.additional_data.get('client_secret')
        })
        
        # Check if user has Azure OpenAI configured
        azure_config = db.query(Credential).filter(
            Credential.user_id == current_user.id,
            Credential.service_name == "azure_openai"
        ).first()
        
        # Initialize LLM service with user's config or None
        if azure_config and azure_config.additional_data:
            llm_service = LLMService(
                api_key=azure_config.additional_data.get('api_key'),
                endpoint=azure_config.additional_data.get('endpoint'),
                deployment=azure_config.additional_data.get('deployment')
            )
        else:
            # Use default config (may be None - will use fallback)
            llm_service = LLMService()
        
        # Fetch emails
        emails = await gmail_service.get_emails(
            days=request.days,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        # Summarize each email
        summaries = []
        total_tokens = 0
        
        for email in emails:
            summary_result = await llm_service.summarize_email(email)
            
            summaries.append({
                'subject': email['subject'],
                'from_email': email['from'],
                'date': email['date'],
                'summary': summary_result['summary'],
                'meeting_links': summary_result['meeting_links']
            })
            
            total_tokens += summary_result['tokens_used']
        
        # Track cost
        track_cost(db, current_user.id, "azure_openai", "email_summary", total_tokens)
        
        # Format digest
        html_digest = await llm_service.format_email_digest(summaries)
        
        # Send email digest
        user_email = await gmail_service.get_user_email()
        digest_sent = await gmail_service.send_email(
            to=user_email,
            subject="Daily Email Digest",
            html_content=html_digest
        )
        
        # If invoked from Slack, also post to Slack
        if request.source == "slack" and request.slack_channel:
            try:
                slack_cred = get_credential(db, current_user.id, "slack")
                slack_service = SlackService(slack_cred.access_token)
                
                slack_blocks = await llm_service.format_slack_message(summaries)
                await slack_service.post_message(
                    channel=request.slack_channel,
                    blocks=slack_blocks,
                    thread_ts=request.slack_thread_ts
                )
            except Exception as e:
                print(f"Error posting to Slack: {e}")
        
        # Log activity
        log_activity(
            db, current_user.id, "email_summary", request.source, "success",
            {"total_emails": len(summaries), "tokens_used": total_tokens}
        )
        
        return EmailSummaryResponse(
            summaries=[EmailSummary(**s) for s in summaries],
            total_emails=len(summaries),
            digest_sent=digest_sent
        )
    
    except Exception as e:
        log_activity(db, current_user.id, "email_summary", request.source, "failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule-meeting", response_model=MeetingScheduleResponse)
async def schedule_meeting(
    request: MeetingScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Schedule a meeting with attendees"""
    
    try:
        # Get credentials
        google_cred = get_credential(db, current_user.id, "google")
        
        # Initialize calendar service
        calendar_service = CalendarService({
            'access_token': google_cred.access_token,
            'refresh_token': google_cred.refresh_token,
            'client_id': google_cred.additional_data.get('client_id'),
            'client_secret': google_cred.additional_data.get('client_secret')
        })
        
        conflicts = []
        meeting_time = None
        
        if request.next_available:
            # Find next available slot
            slot = await calendar_service.find_next_available_slot(
                request.attendees,
                request.duration_minutes
            )
            
            if not slot:
                log_activity(db, current_user.id, "schedule_meeting", request.source, "failed",
                           {"error": "No available slots found"})
                return MeetingScheduleResponse(
                    success=False,
                    message="No available time slots found in the next 7 days for all attendees."
                )
            
            meeting_time = slot
        else:
            # Use specified time
            if not request.date or not request.time:
                raise HTTPException(status_code=400, detail="Date and time required when not using next_available")
            
            start_dt = datetime.fromisoformat(f"{request.date}T{request.time}")
            end_dt = start_dt + timedelta(minutes=request.duration_minutes)
            
            meeting_time = {
                'start': start_dt.isoformat() + 'Z',
                'end': end_dt.isoformat() + 'Z'
            }
            
            # Check for conflicts
            conflicts = await calendar_service.check_conflicts(
                request.attendees,
                meeting_time['start'],
                meeting_time['end']
            )
            
            if conflicts:
                conflict_message = f"Time conflict detected with: {', '.join(conflicts)}"
                
                # Post to Slack if invoked from there
                if request.source == "slack" and request.slack_channel:
                    try:
                        slack_cred = get_credential(db, current_user.id, "slack")
                        slack_service = SlackService(slack_cred.access_token)
                        await slack_service.post_message(
                            channel=request.slack_channel,
                            text=f"⚠️ {conflict_message}",
                            thread_ts=request.slack_thread_ts
                        )
                    except Exception as e:
                        print(f"Error posting to Slack: {e}")
                
                log_activity(db, current_user.id, "schedule_meeting", request.source, "failed",
                           {"conflicts": conflicts})
                
                return MeetingScheduleResponse(
                    success=False,
                    message=conflict_message,
                    conflicts=conflicts
                )
        
        # Create the meeting
        meeting = await calendar_service.create_meeting(
            title=request.title,
            description=request.description,
            attendees=request.attendees,
            start_time=meeting_time['start'],
            end_time=meeting_time['end']
        )
        
        if not meeting:
            raise HTTPException(status_code=500, detail="Failed to create meeting")
        
        success_message = f"Meeting scheduled successfully! Link: {meeting.get('hangout_link') or meeting.get('link')}"
        
        # Post to Slack if invoked from there
        if request.source == "slack" and request.slack_channel:
            try:
                slack_cred = get_credential(db, current_user.id, "slack")
                slack_service = SlackService(slack_cred.access_token)
                
                blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"✅ *Meeting Scheduled Successfully!*\n\n"
                                   f"*Title:* {request.title}\n"
                                   f"*Attendees:* {', '.join(request.attendees)}\n"
                                   f"*Duration:* {request.duration_minutes} minutes\n"
                                   f"*Time:* {meeting_time['start']}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"🔗 <{meeting.get('hangout_link') or meeting.get('link')}|Join Meeting>"
                        }
                    }
                ]
                
                await slack_service.post_message(
                    channel=request.slack_channel,
                    blocks=blocks,
                    thread_ts=request.slack_thread_ts
                )
            except Exception as e:
                print(f"Error posting to Slack: {e}")
        
        # Log activity
        log_activity(db, current_user.id, "schedule_meeting", request.source, "success",
                   {"meeting_id": meeting['id'], "attendees": request.attendees})
        
        return MeetingScheduleResponse(
            success=True,
            message=success_message,
            meeting_link=meeting.get('hangout_link') or meeting.get('link')
        )
    
    except Exception as e:
        log_activity(db, current_user.id, "schedule_meeting", request.source, "failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
