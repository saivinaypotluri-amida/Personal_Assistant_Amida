# 🚀 Amida AI Assistant - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- ✅ Python 3.9+ installed
- ✅ Node.js 18+ installed
- ✅ Git installed

## Step 1: Installation (2 minutes)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

## Step 2: Start the Application (1 minute)

### Terminal 1 - Start Backend
```bash
cd backend
export PATH="$PATH:/home/ubuntu/.local/bin"
python3 main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Terminal 2 - Start Frontend
```bash
cd frontend
npm run dev
```

You should see:
```
➜  Local:   http://localhost:5173/
```

## Step 3: Create Your Account (1 minute)

1. Open your browser to `http://localhost:5173`
2. Click "Sign up"
3. Fill in your details:
   - Email: your-email@company.com
   - Username: your-username
   - Password: your-password
4. Click "Create Account"

🎉 **You're in!** You'll be redirected to the dashboard.

## Step 4: Connect Services (Optional)

### To use email features:
1. Get Google OAuth credentials from [Google Cloud Console](https://console.cloud.google.com)
2. Update `backend/.env`:
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```
3. Restart backend
4. Click "Connect" for Google Workspace in the dashboard

### To use Slack:
1. Create a Slack app at [Slack API](https://api.slack.com/apps)
2. Update `backend/.env` with Slack credentials
3. Restart backend
4. Click "Connect" for Slack in the dashboard

### To use AI features:
1. Get Azure OpenAI credentials
2. Update `backend/.env`:
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_KEY=your-key
   AZURE_OPENAI_DEPLOYMENT=your-deployment
   ```
3. Restart backend

## Features You Can Use Right Now

### Without API Configuration:
- ✅ User authentication
- ✅ Admin dashboard (if you're an admin)
- ✅ Activity logging
- ✅ User management

### With Google OAuth:
- ✅ Email summarization
- ✅ Meeting scheduling
- ✅ Daily digest emails

### With Slack:
- ✅ `/emailsummary` command
- ✅ `/schedule` command
- ✅ Slack notifications

## Make Yourself an Admin

```bash
# In a new terminal
cd backend
sqlite3 amida_assistant.db
UPDATE users SET is_admin = 1 WHERE username = 'your-username';
.exit
```

Refresh the dashboard and you'll see an "Admin" button!

## Troubleshooting

### "Cannot connect to backend"
- Make sure backend is running on port 8000
- Check terminal for error messages

### "Module not found" errors
```bash
cd backend
pip install -r requirements.txt
```

### Frontend won't start
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

## What's Next?

1. ✅ Check out the full [README.md](README.md) for detailed documentation
2. ✅ Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for production deployment
3. ✅ Configure all integrations for full functionality
4. ✅ Invite team members to create accounts

## Need Help?

- 📖 Full documentation: `README.md`
- 🔧 Setup guide: `SETUP_GUIDE.md`
- 🐛 Issues: Create a GitHub issue
- 📧 Email: support@amida.com

---

**Congratulations! Your Amida AI Assistant is ready to use!** 🎊
