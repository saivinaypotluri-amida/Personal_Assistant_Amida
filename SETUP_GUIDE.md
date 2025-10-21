# Amida AI Assistant - Complete Setup Guide

This guide will walk you through setting up the Amida AI Personal Assistant from scratch.

## Prerequisites Checklist

- [ ] Python 3.9 or higher installed
- [ ] Node.js 18 or higher installed
- [ ] Google Cloud Platform account
- [ ] Slack workspace (admin access)
- [ ] Azure account with OpenAI access

## Step 1: Clone and Install

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install
```

## Step 2: Google Cloud Platform Setup

### Create OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project:
   - Click "Select a project" → "New Project"
   - Name: "Amida AI Assistant"
   - Click "Create"

3. Enable Required APIs:
   - Go to "APIs & Services" → "Library"
   - Search and enable:
     * Gmail API
     * Google Calendar API
     * Google People API

4. Create OAuth Consent Screen:
   - Go to "APIs & Services" → "OAuth consent screen"
   - User Type: External (or Internal if using Google Workspace)
   - App name: "Amida AI Assistant"
   - User support email: your email
   - Developer contact: your email
   - Scopes: Add these scopes:
     * .../auth/gmail.readonly
     * .../auth/gmail.send
     * .../auth/calendar
     * .../auth/userinfo.email
   - Save and Continue

5. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Web application"
   - Name: "Amida AI Web Client"
   - Authorized redirect URIs:
     * `http://localhost:8000/api/auth/google/callback`
     * (Add production URL when deploying)
   - Click "Create"
   - **Save the Client ID and Client Secret**

6. Update `.env` file:
   ```bash
   GOOGLE_CLIENT_ID=your-client-id-here
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   ```

## Step 3: Slack App Setup

### Create Slack App

1. Go to [Slack API](https://api.slack.com/apps)
2. Click "Create New App"
3. Choose "From scratch"
4. App Name: "Amida AI Assistant"
5. Pick your workspace
6. Click "Create App"

### Configure OAuth & Permissions

1. In your app settings, go to "OAuth & Permissions"
2. Under "Scopes" → "Bot Token Scopes", add:
   - `chat:write`
   - `commands`
   - `users:read`
   - `users:read.email`
   - `channels:history`
   - `groups:history`
   - `im:history`
   - `mpim:history`

3. Under "Redirect URLs", add:
   - `http://localhost:8000/api/auth/slack/callback`
   - (Add production URL when deploying)

### Create Slash Commands

1. Go to "Slash Commands"
2. Click "Create New Command"

**Command 1: /emailsummary**
- Command: `/emailsummary`
- Request URL: `http://localhost:8000/api/slack/commands`
- Short Description: "Get email summary digest"
- Usage Hint: "[number] days"

**Command 2: /schedule**
- Command: `/schedule`
- Request URL: `http://localhost:8000/api/slack/commands`
- Short Description: "Schedule a meeting"
- Usage Hint: "email1,email2 duration title"

### Enable Events

1. Go to "Event Subscriptions"
2. Turn on "Enable Events"
3. Request URL: `http://localhost:8000/api/slack/events`
   - **Note**: For local development, use [ngrok](https://ngrok.com) to expose localhost
   - Run: `ngrok http 8000`
   - Use the ngrok URL: `https://your-id.ngrok.io/api/slack/events`

4. Subscribe to bot events:
   - `app_mention`

5. Click "Save Changes"

### Install App to Workspace

1. Go to "Install App"
2. Click "Install to Workspace"
3. Review permissions and click "Allow"
4. **Copy the Bot User OAuth Token**

### Update .env File

```bash
SLACK_CLIENT_ID=your-client-id
SLACK_CLIENT_SECRET=your-client-secret
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_REDIRECT_URI=http://localhost:8000/api/auth/slack/callback
```

You can find these in your Slack app settings:
- Client ID & Secret: "Basic Information" → "App Credentials"
- Signing Secret: "Basic Information" → "App Credentials"
- Bot Token: "OAuth & Permissions" → "Bot User OAuth Token"

## Step 4: Azure OpenAI Setup

### Create Azure OpenAI Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Azure OpenAI"
4. Click "Create"
5. Fill in:
   - Subscription: Your subscription
   - Resource group: Create new or use existing
   - Region: Choose available region
   - Name: "amida-openai"
   - Pricing tier: Standard S0
6. Click "Review + Create" → "Create"

### Deploy a Model

1. Go to your Azure OpenAI resource
2. Click "Go to Azure OpenAI Studio"
3. Go to "Deployments"
4. Click "Create new deployment"
5. Select model: "gpt-4" or "gpt-35-turbo"
6. Deployment name: "amida-gpt4" (or your choice)
7. Click "Create"

### Get Credentials

1. In Azure Portal, go to your OpenAI resource
2. Go to "Keys and Endpoint"
3. Copy:
   - Endpoint (e.g., `https://amida-openai.openai.azure.com/`)
   - Key 1

### Update .env File

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=amida-gpt4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## Step 5: Run the Application

### Start Backend

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Start Frontend

```bash
cd frontend
npm run dev
```

You should see:
```
VITE v5.0.8  ready in 500 ms
➜  Local:   http://localhost:5173/
```

## Step 6: Create Admin Account

1. Open browser to `http://localhost:5173`
2. Click "Sign up"
3. Fill in registration form:
   - Email: admin@amida.com
   - Username: admin
   - Password: (your secure password)
4. Login with credentials

**To make this user an admin**, you need to update the database directly:

```bash
# In backend directory
sqlite3 amida_assistant.db

# Run this SQL
UPDATE users SET is_admin = 1 WHERE username = 'admin';

# Exit
.exit
```

Refresh the page and you should see the "Admin" button.

## Step 7: Connect Services

1. Login to the portal
2. In the "Connected Services" section:
   - Click "Connect" for Google Workspace
   - Authorize the app
   - Click "Connect" for Slack
   - Authorize the app

## Step 8: Test the Features

### Test Email Summary

1. Go to the Dashboard
2. In "Email Summary" section:
   - Enter number of days (e.g., 1)
   - Click "Get Email Summary"
3. Check your email for the Daily Digest
4. Results will also show in the portal

### Test Meeting Scheduling

1. In "Schedule Meeting" section:
   - Enter attendee emails (comma-separated)
   - Set duration (e.g., 30 minutes)
   - Enter meeting title
   - Click "Schedule Meeting"
2. Meeting will be created in Google Calendar
3. All attendees will receive calendar invites

### Test Slack Commands

1. In Slack, go to any channel
2. Type `/emailsummary`
   - You should get your email digest
3. Type `/schedule john@example.com,jane@example.com 30 Team Sync`
   - Meeting should be scheduled

### Test Admin Features

1. Click "Admin" button
2. Check different tabs:
   - Users: View all users
   - Activity Logs: See all actions
   - Cost Tracking: View API usage costs
   - Statistics: Overall metrics

## Troubleshooting

### Backend Issues

**"Module not found" errors**
```bash
pip install -r requirements.txt
```

**"Database locked" error**
- Close all connections to SQLite
- Delete `amida_assistant.db` and restart

**OAuth redirect errors**
- Verify redirect URIs match exactly in OAuth configs
- Check that backend is running on port 8000

### Frontend Issues

**"Cannot connect to backend"**
- Verify backend is running on port 8000
- Check CORS settings in backend

**OAuth popups blocked**
- Allow popups in browser
- Try in incognito/private mode

### Slack Issues

**Commands not responding**
- For local development, use ngrok: `ngrok http 8000`
- Update Slack event URLs with ngrok URL
- Verify Slack app is installed to workspace

**"User not found" in Slack**
- Make sure user's Slack email matches their portal email
- Register in portal first before using Slack

### Google API Issues

**"Access blocked" error**
- Make sure OAuth consent screen is configured
- Add your email as a test user if using External user type
- Enable required APIs in Google Cloud Console

**"Invalid grant" error**
- Token may have expired
- Reconnect Google account in portal

## Production Deployment

### Environment Variables

Update these for production:

```bash
SECRET_KEY=use-a-strong-random-secret-key
FRONTEND_URL=https://your-domain.com
GOOGLE_REDIRECT_URI=https://your-domain.com/api/auth/google/callback
SLACK_REDIRECT_URI=https://your-domain.com/api/auth/slack/callback
```

### Database

Consider using PostgreSQL instead of SQLite:

```bash
DATABASE_URL=postgresql://user:password@localhost/amida_db
```

### Hosting Options

**Backend:**
- AWS EC2 / ECS
- Google Cloud Run
- Heroku
- DigitalOcean

**Frontend:**
- Vercel
- Netlify
- AWS S3 + CloudFront
- Firebase Hosting

### Security Checklist

- [ ] Change SECRET_KEY to a strong random value
- [ ] Use HTTPS for all endpoints
- [ ] Update OAuth redirect URIs to production URLs
- [ ] Enable rate limiting
- [ ] Set up proper logging and monitoring
- [ ] Regular backups of database
- [ ] Environment variables in secure vault

## Need Help?

- Check the main README.md for more details
- Review API documentation at `http://localhost:8000/docs`
- Create an issue on GitHub

---

Congratulations! Your Amida AI Assistant is now set up and running! 🎉
