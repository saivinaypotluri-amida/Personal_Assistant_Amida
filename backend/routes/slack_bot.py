from fastapi import APIRouter, Request, HTTPException
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from sqlalchemy.orm import Session
import os

from config import settings
from database import SessionLocal
from models import User, Credential
from services.slack_service import SlackService
from services.gmail_service import GmailService
from services.calendar_service import CalendarService
from services.llm_service import LLMService

router = APIRouter(prefix="/api/slack", tags=["Slack Bot"])

# Initialize Slack app (only if credentials are provided)
slack_app = None
handler = None

if os.getenv("SLACK_BOT_TOKEN") and settings.SLACK_SIGNING_SECRET:
    slack_app = AsyncApp(
        token=os.getenv("SLACK_BOT_TOKEN"),  # Bot token from workspace
        signing_secret=settings.SLACK_SIGNING_SECRET
    )
    handler = AsyncSlackRequestHandler(slack_app)
    
    # Register Slack commands and events
    slack_app.command("/emailsummary")(handle_email_summary)
    slack_app.command("/schedule")(handle_schedule_meeting)
    slack_app.event("app_mention")(handle_mention)


def get_user_by_slack_email(email: str, db: Session):
    """Get user by their Slack email"""
    return db.query(User).filter(User.email == email).first()


def get_credential(db: Session, user_id: int, service: str):
    """Get credential for a service"""
    return db.query(Credential).filter(
        Credential.user_id == user_id,
        Credential.service_name == service
    ).first()


# Slack command: /emailsummary  
async def handle_email_summary(ack, command, client):
    """Handle /emailsummary command"""
    await ack()
    
    db = SessionLocal()
    try:
        # Get Slack user email
        user_info = await client.users_info(user=command['user_id'])
        user_email = user_info['user']['profile']['email']
        
        # Find user in database
        user = get_user_by_slack_email(user_email, db)
        if not user:
            await client.chat_postMessage(
                channel=command['channel_id'],
                text="❌ You need to register in the Amida portal first!",
                thread_ts=command.get('thread_ts')
            )
            return
        
        # Get Google credentials
        google_cred = get_credential(db, user.id, "google")
        if not google_cred:
            await client.chat_postMessage(
                channel=command['channel_id'],
                text="❌ Please connect your Google account in the Amida portal first!",
                thread_ts=command.get('thread_ts')
            )
            return
        
        # Parse command text (e.g., "7 days" or "today")
        text = command.get('text', '').lower()
        days = 1  # default to today
        
        if 'days' in text:
            try:
                days = int(text.split()[0])
            except:
                days = 1
        
        # Post loading message
        response = await client.chat_postMessage(
            channel=command['channel_id'],
            text="🔄 Fetching and summarizing your emails... This may take a moment.",
            thread_ts=command.get('thread_ts')
        )
        
        # Initialize services
        gmail_service = GmailService({
            'access_token': google_cred.access_token,
            'refresh_token': google_cred.refresh_token,
            'client_id': google_cred.additional_data.get('client_id'),
            'client_secret': google_cred.additional_data.get('client_secret')
        })
        
        llm_service = LLMService()
        
        # Fetch and summarize emails
        emails = await gmail_service.get_emails(days=days)
        
        summaries = []
        for email in emails:
            summary_result = await llm_service.summarize_email(email)
            summaries.append({
                'subject': email['subject'],
                'from': email['from'],
                'date': email['date'],
                'summary': summary_result['summary'],
                'meeting_links': summary_result['meeting_links']
            })
        
        # Send email digest
        html_digest = await llm_service.format_email_digest(summaries)
        user_email_addr = await gmail_service.get_user_email()
        await gmail_service.send_email(
            to=user_email_addr,
            subject="Daily Email Digest",
            html_content=html_digest
        )
        
        # Format and post to Slack
        slack_blocks = await llm_service.format_slack_message(summaries)
        
        await client.chat_update(
            channel=command['channel_id'],
            ts=response['ts'],
            text=f"📧 Email summary for the last {days} day(s)",
            blocks=slack_blocks
        )
    
    finally:
        db.close()


# Slack command: /schedule
async def handle_schedule_meeting(ack, command, client):
    """Handle /schedule command"""
    await ack()
    
    db = SessionLocal()
    try:
        # Get Slack user email
        user_info = await client.users_info(user=command['user_id'])
        user_email = user_info['user']['profile']['email']
        
        # Find user in database
        user = get_user_by_slack_email(user_email, db)
        if not user:
            await client.chat_postMessage(
                channel=command['channel_id'],
                text="❌ You need to register in the Amida portal first!",
                thread_ts=command.get('thread_ts')
            )
            return
        
        # Get Google credentials
        google_cred = get_credential(db, user.id, "google")
        if not google_cred:
            await client.chat_postMessage(
                channel=command['channel_id'],
                text="❌ Please connect your Google account in the Amida portal first!",
                thread_ts=command.get('thread_ts')
            )
            return
        
        # Parse command text
        # Format: /schedule email1@example.com,email2@example.com 30 "Meeting Title"
        text = command.get('text', '')
        parts = text.split()
        
        if len(parts) < 2:
            await client.chat_postMessage(
                channel=command['channel_id'],
                text="❌ Usage: `/schedule email1,email2 duration_minutes [title]`\nExample: `/schedule john@amida.com,jane@amida.com 30 Team Sync`",
                thread_ts=command.get('thread_ts')
            )
            return
        
        attendees = parts[0].split(',')
        try:
            duration = int(parts[1])
        except:
            duration = 30
        
        title = ' '.join(parts[2:]) if len(parts) > 2 else "Meeting"
        
        # Post loading message
        response = await client.chat_postMessage(
            channel=command['channel_id'],
            text="🔄 Finding available time slot and scheduling meeting...",
            thread_ts=command.get('thread_ts')
        )
        
        # Initialize calendar service
        calendar_service = CalendarService({
            'access_token': google_cred.access_token,
            'refresh_token': google_cred.refresh_token,
            'client_id': google_cred.additional_data.get('client_id'),
            'client_secret': google_cred.additional_data.get('client_secret')
        })
        
        # Find next available slot
        slot = await calendar_service.find_next_available_slot(attendees, duration)
        
        if not slot:
            await client.chat_update(
                channel=command['channel_id'],
                ts=response['ts'],
                text="❌ No available time slots found in the next 7 days for all attendees."
            )
            return
        
        # Create meeting
        meeting = await calendar_service.create_meeting(
            title=title,
            description=f"Meeting scheduled via Slack by {user_email}",
            attendees=attendees,
            start_time=slot['start'],
            end_time=slot['end']
        )
        
        if meeting:
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ *Meeting Scheduled Successfully!*\n\n"
                               f"*Title:* {title}\n"
                               f"*Attendees:* {', '.join(attendees)}\n"
                               f"*Duration:* {duration} minutes\n"
                               f"*Time:* {slot['start']}"
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
            
            await client.chat_update(
                channel=command['channel_id'],
                ts=response['ts'],
                text="Meeting scheduled!",
                blocks=blocks
            )
        else:
            await client.chat_update(
                channel=command['channel_id'],
                ts=response['ts'],
                text="❌ Failed to create meeting. Please try again."
            )
    
    finally:
        db.close()


# Mention handler
async def handle_mention(event, client):
    """Handle @mentions of the bot"""
    
    text = event.get('text', '').lower()
    channel = event['channel']
    thread_ts = event.get('ts')
    
    if 'email' in text or 'summary' in text:
        await client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text="To get your email summary, use the command: `/emailsummary` or `/emailsummary 7 days`"
        )
    elif 'schedule' in text or 'meeting' in text:
        await client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text="To schedule a meeting, use the command: `/schedule email1,email2 30 Meeting Title`"
        )
    else:
        await client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text="👋 Hi! I'm the Amida AI Assistant. I can help you with:\n\n"
                 "• `/emailsummary` - Get your daily email digest\n"
                 "• `/schedule` - Schedule meetings with colleagues\n\n"
                 "Make sure you've connected your accounts in the Amida portal first!"
        )


@router.post("/events")
async def slack_events(request: Request):
    """Handle Slack events"""
    if not handler:
        return {"error": "Slack bot not configured"}
    return await handler.handle(request)


@router.post("/commands")
async def slack_commands(request: Request):
    """Handle Slack slash commands"""
    if not handler:
        return {"error": "Slack bot not configured"}
    return await handler.handle(request)
