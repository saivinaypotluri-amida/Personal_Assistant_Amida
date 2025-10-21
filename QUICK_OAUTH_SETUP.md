# Quick OAuth Setup - TL;DR Version

## The Simple Answer

You **don't enter credentials in the portal directly**. Instead:

1. ✅ Configure credentials in **backend `.env` file**
2. ✅ Click **"Connect"** button in portal
3. ✅ Authorize on Google/Slack
4. ✅ Done!

---

## 5-Minute Setup

### Step 1: Edit `.env` File (Backend)

```powershell
cd backend
notepad .env   # or use your editor
```

Add your credentials:

```env
# Get from Google Cloud Console
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret-here

# Get from Slack App Dashboard
SLACK_CLIENT_ID=1234567890.1234567890
SLACK_CLIENT_SECRET=your-slack-secret-here
SLACK_SIGNING_SECRET=your-signing-secret-here
SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Get from Azure Portal
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-openai-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

### Step 2: Restart Backend

```powershell
python main.py
```

### Step 3: Connect in Portal

1. Go to http://localhost:5173
2. Login
3. See "Connected Services" section
4. Click **"Connect"** next to Google Workspace
5. Click **"Allow"** on Google's authorization page
6. Click **"Connect"** next to Slack
7. Click **"Allow"** on Slack's authorization page
8. ✅ Both show green checkmarks!

---

## Where to Get Credentials

### Google (5 minutes)

1. Go to: https://console.cloud.google.com
2. Create project → Enable Gmail & Calendar APIs
3. Create OAuth Client → Copy Client ID & Secret
4. **Detailed guide**: See [OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md) Part 2

### Slack (5 minutes)

1. Go to: https://api.slack.com/apps
2. Create App → Configure OAuth scopes
3. Install to workspace → Copy tokens
4. **Detailed guide**: See [OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md) Part 3

### Azure OpenAI (5 minutes)

1. Go to: https://portal.azure.com
2. Create Azure OpenAI resource
3. Deploy model (GPT-4)
4. Copy endpoint & key
5. **Detailed guide**: See [SETUP_GUIDE.md](SETUP_GUIDE.md) Step 4

---

## Visual Flow

```
┌─────────────────────────────────────────────────┐
│  1. YOU: Edit backend/.env file                │
│     Add Google/Slack/Azure credentials         │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  2. YOU: Restart backend                       │
│     python main.py                             │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  3. YOU: Open portal (localhost:5173)          │
│     Login to your account                      │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  4. PORTAL: Shows "Connected Services"         │
│     ┌────────────────────────────────────┐    │
│     │ Google Workspace    [Connect]      │    │
│     │ Slack              [Connect]       │    │
│     └────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  5. YOU: Click "Connect" for Google            │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  6. GOOGLE: "Amida AI wants access..."         │
│     YOU: Click "Allow"                         │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  7. PORTAL: Google Workspace [✓] Connected!    │
└─────────────────────────────────────────────────┘
                    ↓
        (Repeat for Slack)
                    ↓
┌─────────────────────────────────────────────────┐
│  8. DONE! Both services connected ✅           │
│     ┌────────────────────────────────────┐    │
│     │ Google Workspace    [✓]            │    │
│     │ Slack              [✓]             │    │
│     └────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

---

## What You'll See in Portal

### Before Connection:
```
Connected Services
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┌─────────────────────────────────────┐
│ Google Workspace          [Connect] │
│ Slack                     [Connect] │
└─────────────────────────────────────┘
```

### After Connection:
```
Connected Services
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┌─────────────────────────────────────┐
│ Google Workspace          [✓]       │ ← Green checkmark
│ Slack                     [✓]       │ ← Green checkmark
└─────────────────────────────────────┘
```

---

## Common Questions

### Q: Do I enter credentials in the portal?
**A:** No! Credentials go in `backend/.env` file. Portal just has "Connect" buttons.

### Q: What does "Connect" button do?
**A:** Opens Google/Slack authorization page. You click "Allow", they send tokens back, tokens stored in database.

### Q: Where are tokens stored?
**A:** SQLite database (`amida_assistant.db`), in the `credentials` table.

### Q: Do I need to reconnect every time?
**A:** No! Once connected, tokens are saved. Only reconnect if they expire.

### Q: What if "Connect" doesn't work?
**A:** Check:
1. `.env` file has correct credentials
2. Backend is running
3. Redirect URIs match in OAuth config

---

## Testing Connection

### Test Google Connection:

1. In portal, "Email Summary" section
2. Enter: `1` (day)
3. Click "Get Email Summary"
4. ✅ Should fetch your emails!

### Test Slack Connection:

1. In Slack, type: `/emailsummary`
2. ✅ Should show email digest!

---

## Need Help?

- **Detailed guide**: [OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md)
- **Google setup**: [OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md) Part 2
- **Slack setup**: [OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md) Part 3
- **Troubleshooting**: [OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md) Troubleshooting section

---

## TL;DR

1. Edit `backend/.env` ← Put credentials here
2. Restart backend
3. Click "Connect" in portal ← Just click, don't type anything
4. Click "Allow" on Google/Slack
5. ✅ Done!

**That's it!** The portal doesn't have credential input fields. It's all OAuth flow with "Connect" buttons.
