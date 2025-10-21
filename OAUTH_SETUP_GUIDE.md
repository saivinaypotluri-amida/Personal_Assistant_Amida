# OAuth Setup Guide - Google Workspace & Slack

This guide shows you how to configure Google Workspace and Slack credentials through the Amida AI Assistant portal.

## Overview

The portal uses **OAuth 2.0** flow - you don't enter credentials directly. Instead:
1. You click "Connect" in the portal
2. You're redirected to Google/Slack to authorize
3. They redirect back with tokens
4. Tokens are stored securely in the database

---

## Prerequisites

Before you can connect services in the portal, you need to:

### For Google Workspace:
1. ✅ Google Cloud Project created
2. ✅ Gmail API & Calendar API enabled
3. ✅ OAuth credentials configured
4. ✅ Credentials added to backend `.env` file

### For Slack:
1. ✅ Slack App created
2. ✅ OAuth scopes configured
3. ✅ Slash commands created
4. ✅ Credentials added to backend `.env` file

---

## Part 1: Configure Backend `.env` File

### Step 1: Navigate to Backend Directory

```powershell
cd backend
```

### Step 2: Edit `.env` File

Open `.env` in your text editor and add your credentials:

```env
# Google OAuth Credentials
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-AbCdEfGhIjKlMnOpQrStUvWx
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Slack OAuth Credentials
SLACK_CLIENT_ID=1234567890.1234567890
SLACK_CLIENT_SECRET=abcdef1234567890abcdef1234567890
SLACK_SIGNING_SECRET=abcdef1234567890abcdef1234567890abcd
SLACK_REDIRECT_URI=http://localhost:8000/api/auth/slack/callback
SLACK_BOT_TOKEN=xoxb-YOUR-SLACK-BOT-TOKEN

# Azure OpenAI (for LLM features)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Step 3: Restart Backend

```powershell
python main.py
```

---

## Part 2: Get Google OAuth Credentials

### Step 1: Go to Google Cloud Console

1. Visit: https://console.cloud.google.com
2. Sign in with your Google account

### Step 2: Create a Project (if you don't have one)

1. Click project dropdown at top
2. Click "New Project"
3. Name: "Amida AI Assistant"
4. Click "Create"

### Step 3: Enable APIs

1. Go to "APIs & Services" → "Library"
2. Search and enable:
   - **Gmail API**
   - **Google Calendar API**
   - **Google People API** (optional)

### Step 4: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" (or "Internal" if using Google Workspace)
3. Fill in:
   - **App name**: Amida AI Assistant
   - **User support email**: your-email@gmail.com
   - **Developer contact**: your-email@gmail.com
4. Click "Save and Continue"

5. **Add Scopes**:
   - Click "Add or Remove Scopes"
   - Add these scopes:
     ```
     https://www.googleapis.com/auth/gmail.readonly
     https://www.googleapis.com/auth/gmail.send
     https://www.googleapis.com/auth/calendar
     https://www.googleapis.com/auth/userinfo.email
     ```
   - Click "Update" then "Save and Continue"

6. **Test Users** (if using External):
   - Add your email address as a test user
   - Click "Save and Continue"

### Step 5: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: **Web application**
4. Name: "Amida AI Web Client"
5. **Authorized redirect URIs**:
   ```
   http://localhost:8000/api/auth/google/callback
   ```
   (Add your production URL later: `https://yourdomain.com/api/auth/google/callback`)
6. Click "Create"

### Step 6: Copy Credentials

A dialog shows your credentials:
- **Client ID**: `123456789-abc...apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-AbC...`

**Copy both and add to `.env` file!**

---

## Part 3: Get Slack Credentials

### Step 1: Go to Slack API

1. Visit: https://api.slack.com/apps
2. Sign in to your Slack workspace

### Step 2: Create a Slack App

1. Click "Create New App"
2. Choose "From scratch"
3. **App Name**: Amida AI Assistant
4. **Workspace**: Select your workspace
5. Click "Create App"

### Step 3: Configure OAuth & Permissions

1. In left sidebar, click "OAuth & Permissions"
2. Scroll to "Scopes" → "Bot Token Scopes"
3. Add these scopes:
   ```
   chat:write
   commands
   users:read
   users:read.email
   channels:history
   groups:history
   im:history
   mpim:history
   ```

4. Scroll to "Redirect URLs"
5. Click "Add New Redirect URL"
6. Enter: `http://localhost:8000/api/auth/slack/callback`
7. Click "Save URLs"

### Step 4: Create Slash Commands

1. In left sidebar, click "Slash Commands"
2. Click "Create New Command"

**Command 1: /emailsummary**
- **Command**: `/emailsummary`
- **Request URL**: `http://localhost:8000/api/slack/commands`
- **Short Description**: Get email summary digest
- **Usage Hint**: `[natural language, e.g., "last 3 days"]`
- Click "Save"

**Command 2: /schedule**
- **Command**: `/schedule`
- **Request URL**: `http://localhost:8000/api/slack/commands`
- **Short Description**: Schedule a meeting
- **Usage Hint**: `[natural language, e.g., "meeting with john@example.com for 30 minutes"]`
- Click "Save"

### Step 5: Enable Events (Optional)

1. In left sidebar, click "Event Subscriptions"
2. Toggle "Enable Events" to **On**
3. **Request URL**: `http://localhost:8000/api/slack/events`
   
   **Note**: For local development, use ngrok:
   ```powershell
   ngrok http 8000
   ```
   Then use: `https://your-id.ngrok.io/api/slack/events`

4. Subscribe to bot events:
   - `app_mention`
5. Click "Save Changes"

### Step 6: Install App to Workspace

1. In left sidebar, click "Install App"
2. Click "Install to Workspace"
3. Review permissions
4. Click "Allow"

### Step 7: Get Credentials

After installation, you'll see:

1. **OAuth & Permissions** page shows:
   - **Bot User OAuth Token**: `xoxb-123...` (COPY THIS!)

2. **Basic Information** page shows:
   - **Client ID**: `1234567890.1234567890`
   - **Client Secret**: `abc123...`
   - **Signing Secret**: `abc123...`

**Copy all and add to `.env` file!**

---

## Part 4: Connect Services in Portal

### Step 1: Start Your Application

**Backend:**
```powershell
cd backend
python main.py
```

**Frontend:**
```powershell
cd frontend
npm run dev
```

### Step 2: Open Portal

Go to: http://localhost:5173

### Step 3: Login/Register

1. Create account or login
2. You'll see the Dashboard

### Step 4: Connect Google Workspace

1. Look for "Connected Services" section
2. Find "Google Workspace" row
3. Click **"Connect"** button

**What happens:**
```
Portal → Redirects to Google
Google → Shows: "Amida AI Assistant wants to access your Google Account"
        → Shows permissions (Gmail, Calendar)
You → Click "Allow"
Google → Redirects back to Portal
Portal → Shows "✓ Connected" (green checkmark)
```

**Behind the scenes:**
- Portal requests: `GET /api/auth/google/url`
- Backend generates OAuth URL
- User authorizes on Google
- Google redirects to: `/api/auth/google/callback?code=...`
- Backend exchanges code for tokens
- Tokens stored in database
- User redirected back to dashboard

### Step 5: Connect Slack

1. In "Connected Services" section
2. Find "Slack" row
3. Click **"Connect"** button

**What happens:**
```
Portal → Redirects to Slack
Slack → Shows: "Amida AI Assistant wants to access your workspace"
       → Shows permissions
You → Click "Allow"
Slack → Redirects back to Portal
Portal → Shows "✓ Connected" (green checkmark)
```

**Behind the scenes:**
- Portal requests: `GET /api/auth/slack/url`
- Backend generates OAuth URL
- User authorizes on Slack
- Slack redirects to: `/api/auth/slack/callback?code=...`
- Backend exchanges code for tokens
- Tokens stored in database
- User redirected back to dashboard

---

## Part 5: Verify Connection

### Check in Portal

On the dashboard, you should see:

```
Connected Services
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┌─────────────────────────────────────┐
│ Google Workspace          [✓]       │
│ Slack                     [✓]       │
└─────────────────────────────────────┘
```

Green checkmarks = Connected! ✅

### Test Email Summary

1. In "Email Summary" section
2. Enter number of days (e.g., 1)
3. Click "Get Email Summary"
4. ✅ Should fetch and display your emails!

### Test in Slack

Open Slack and try:
```
/emailsummary last 3 days
/schedule meeting with colleague@example.com for 30 minutes
```

---

## Troubleshooting

### "Connect" Button Does Nothing

**Cause**: `.env` file not configured or backend not restarted

**Fix**:
1. Check `.env` has Google/Slack credentials
2. Restart backend: `python main.py`
3. Check backend logs for errors

---

### Redirect URI Mismatch Error

**Error from Google/Slack**: "redirect_uri_mismatch"

**Cause**: Redirect URI in OAuth config doesn't match backend

**Fix**:
1. **Google**: Go to Cloud Console → Credentials → Edit OAuth client
   - Add: `http://localhost:8000/api/auth/google/callback`
2. **Slack**: Go to Slack App → OAuth & Permissions
   - Add: `http://localhost:8000/api/auth/slack/callback`

---

### Connection Shows "✗" (Red X)

**Cause**: Not connected yet or tokens expired

**Fix**:
1. Click "Connect" button
2. Complete OAuth flow
3. Check backend logs for errors

---

### Backend Errors

**Check logs**:
```powershell
# In backend terminal, look for:
ERROR: ...
Traceback ...
```

**Common issues**:
- Missing credentials in `.env`
- Invalid Client ID/Secret
- API not enabled in Google Cloud

---

## Environment Variables Reference

### Complete `.env` Example

```env
# Application Settings
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///./amida_assistant.db
FRONTEND_URL=http://localhost:5173

# Google OAuth
GOOGLE_CLIENT_ID=123456789-abc...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abc123...
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Slack OAuth
SLACK_CLIENT_ID=1234567890.1234567890
SLACK_CLIENT_SECRET=abc123def456...
SLACK_SIGNING_SECRET=abc123def456...
SLACK_REDIRECT_URI=http://localhost:8000/api/auth/slack/callback
SLACK_BOT_TOKEN=xoxb-YOUR-SLACK-BOT-TOKEN...

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=abc123def456...
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

---

## Security Notes

### Never Commit `.env` File

The `.env` file contains secrets. It's in `.gitignore` - never commit it!

### Production Setup

For production:
1. Use environment variables instead of `.env` file
2. Update redirect URIs to production URLs:
   ```
   https://yourdomain.com/api/auth/google/callback
   https://yourdomain.com/api/auth/slack/callback
   ```
3. Use HTTPS (not HTTP)
4. Enable only required OAuth scopes

---

## Quick Reference

### Where to Get Credentials

| Service | Where to Get |
|---------|--------------|
| Google Client ID/Secret | Google Cloud Console → APIs & Services → Credentials |
| Slack Client ID/Secret | Slack API → Your App → Basic Information |
| Slack Bot Token | Slack API → Your App → OAuth & Permissions |
| Slack Signing Secret | Slack API → Your App → Basic Information |

### Required Scopes

**Google:**
- `gmail.readonly` - Read emails
- `gmail.send` - Send digest emails
- `calendar` - Schedule meetings
- `userinfo.email` - Get user email

**Slack:**
- `chat:write` - Post messages
- `commands` - Slash commands
- `users:read` - Get user info
- `users:read.email` - Get user email

---

## Next Steps

1. ✅ Configure `.env` file with all credentials
2. ✅ Restart backend
3. ✅ Login to portal
4. ✅ Click "Connect" for Google Workspace
5. ✅ Click "Connect" for Slack
6. ✅ Test email summary feature
7. ✅ Test Slack commands

---

**You're all set!** 🎉

Your portal is now connected to Google Workspace and Slack!
