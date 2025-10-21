# Natural Language Slack Commands

## Overview

The Amida AI Assistant now uses **AI-powered natural language processing** to understand Slack commands. You can type commands naturally, and the LLM will parse them!

## Features Implemented

### 1. First User Auto-Admin ✅
- The **first person to register** automatically becomes an admin
- No need to manually set admin status in the database
- Subsequent users register as normal users

### 2. Natural Language Command Parsing ✅
- Slack commands now accept **natural language input**
- LLM (Azure OpenAI) parses the text to extract parameters
- Much more user-friendly than rigid syntax!

---

## Slack Command Examples

### `/emailsummary` Command

**Old rigid syntax:**
```
/emailsummary 7 days
```

**New natural language (all work!):**
```
/emailsummary
/emailsummary last 3 days
/emailsummary yesterday
/emailsummary from the last week
/emailsummary show me emails from Jan 1 to Jan 5
/emailsummary 7
```

**How it works:**
1. User types natural language
2. LLM extracts: `days`, `start_date`, `end_date`
3. System fetches and summarizes emails
4. Sends digest via email + Slack reply

---

### `/schedule` Command

**Old rigid syntax:**
```
/schedule john@example.com,jane@example.com 30 Team Sync
```

**New natural language (all work!):**
```
/schedule meeting with john@example.com for 30 minutes
/schedule john@example.com and jane@example.com for 1 hour called Team Sync
/schedule john@ex.com,jane@ex.com 30 Project Review
/schedule meeting with john@ex.com for 45 minutes tomorrow at 2pm called Sprint Planning
```

**How it works:**
1. User types natural language
2. LLM extracts:
   - `attendees`: List of email addresses
   - `duration_minutes`: Meeting duration
   - `title`: Meeting subject
   - `date` and `time`: If specified (otherwise finds next available)
3. System schedules meeting
4. Posts confirmation to Slack

---

## Technical Implementation

### Command Parser Service

Created `backend/services/command_parser.py`:

```python
class CommandParser:
    async def parse_email_summary_command(text: str) -> Dict:
        # Uses Azure OpenAI to parse natural language
        # Returns: {"days": 3, "start_date": null, "end_date": null}
    
    async def parse_schedule_command(text: str) -> Dict:
        # Uses Azure OpenAI to parse natural language
        # Returns: {
        #   "attendees": ["john@ex.com"],
        #   "duration_minutes": 30,
        #   "title": "Meeting",
        #   "date": null,
        #   "time": null
        # }
```

### Updated Slack Bot

Modified `backend/routes/slack_bot.py`:
- Shows parsing feedback: "🤖 Understanding your request..."
- Processes with LLM
- Updates message with results
- Handles errors gracefully

---

## Examples in Action

### Email Summary Examples

```
User: /emailsummary get my emails from the last 3 days
Bot:  🤖 Understanding your request: 'get my emails from the last 3 days'...
      🔄 Fetching and summarizing your emails...
      📧 Email summary for the last 3 day(s)
      [Shows formatted email list]
```

```
User: /emailsummary yesterday
Bot:  🤖 Understanding your request: 'yesterday'...
      🔄 Fetching and summarizing your emails...
      📧 Email summary for the last 1 day(s)
      [Shows formatted email list]
```

### Meeting Scheduling Examples

```
User: /schedule meeting with john@example.com and jane@example.com for 1 hour called Team Sync
Bot:  🤖 Understanding your request: 'meeting with john@example.com...'
      🔄 Scheduling 'Team Sync' with john@example.com, jane@example.com...
      ✅ Meeting Scheduled Successfully!
      [Shows meeting details and Google Meet link]
```

```
User: /schedule john@ex.com for 30 minutes
Bot:  🤖 Understanding your request: 'john@ex.com for 30 minutes'...
      🔄 Scheduling 'Meeting' with john@ex.com...
      ✅ Meeting Scheduled Successfully!
```

---

## Error Handling

### Invalid Email Command
```
User: /emailsummary some gibberish
Bot:  Falls back to default (today's emails)
```

### Invalid Schedule Command
```
User: /schedule some text without emails
Bot:  ❌ Could not parse command. Please use format: 'email@example.com for 30 minutes'
      
      Examples:
      • /schedule john@example.com for 30 minutes
      • /schedule john@ex.com and jane@ex.com for 1 hour called Team Sync
```

### Missing Google Account
```
Bot: ❌ Please connect your Google account in the Amida portal first!
```

---

## Benefits

✅ **User-Friendly**: Natural language instead of rigid syntax
✅ **Flexible**: Multiple ways to express the same command
✅ **Intelligent**: LLM understands context and variations
✅ **Error-Tolerant**: Gracefully handles parsing failures
✅ **Feedback**: Shows what it's doing at each step

---

## First User Admin Feature

### How It Works

```python
# In register endpoint
user_count = db.query(User).count()
is_first_user = user_count == 0

db_user = User(
    email=user_data.email,
    username=user_data.username,
    hashed_password=get_password_hash(user_data.password),
    is_admin=user_data.is_admin or is_first_user  # First user is always admin
)
```

### Testing

1. **Start fresh** (delete database if needed):
   ```powershell
   # In backend directory
   rm amida_assistant.db
   ```

2. **Start backend**:
   ```powershell
   python main.py
   ```

3. **Register first user**:
   - Go to http://localhost:5173
   - Click "Sign up"
   - Create account
   - ✅ You're automatically an admin!
   - You'll see "Admin" button in dashboard

4. **Register second user**:
   - Logout
   - Register another account
   - ❌ This user is NOT an admin
   - No "Admin" button for them

---

## Required Configuration

To use natural language commands, you need:

1. **Azure OpenAI** configured in `.env`:
   ```env
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_KEY=your-key
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   ```

2. **Slack App** set up with bot token

3. **Google OAuth** connected for each user

---

## What to Test

### Backend
```powershell
# Restart backend to apply changes
python main.py
```

### Test First User Admin
1. Delete database: `rm amida_assistant.db`
2. Register first user
3. Check for "Admin" button
4. Register second user
5. Verify they don't have admin access

### Test Natural Language Commands (in Slack)
1. Connect Google account in portal
2. In Slack: `/emailsummary last 3 days`
3. In Slack: `/schedule meeting with colleague@example.com for 30 minutes`
4. Verify LLM parses correctly

---

## Files Modified

| File | Changes |
|------|---------|
| `backend/routes/auth_routes.py` | First user auto-admin logic |
| `backend/services/command_parser.py` | **NEW** - LLM command parser |
| `backend/routes/slack_bot.py` | Natural language processing for commands |

---

## Next Steps

1. ✅ Restart backend
2. ✅ Test first user registration
3. ✅ Configure Azure OpenAI (if not already)
4. ✅ Test Slack commands with natural language
5. ✅ Enjoy the improved UX!

---

**Your Slack bot is now much smarter!** 🧠🤖
