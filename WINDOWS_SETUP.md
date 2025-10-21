# Windows Setup Guide for Amida AI Assistant

## Issue Fix: Bcrypt Compatibility Error

If you encounter this error:
```
(trapped) error reading bcrypt version
ValueError: password cannot be longer than 72 bytes
```

### Solution:

**In your virtual environment, run:**

```powershell
# Uninstall bcrypt
pip uninstall bcrypt -y

# Install compatible version
pip install bcrypt==3.2.2

# Restart the backend
python main.py
```

## Complete Windows Setup

### 1. Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Git for Windows

### 2. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt

# If bcrypt error occurs, fix it:
pip uninstall bcrypt -y
pip install bcrypt==3.2.2
```

### 3. Frontend Setup

```powershell
# Navigate to frontend directory (in a new PowerShell window)
cd frontend

# Install dependencies
npm install
```

### 4. Start the Application

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### 5. Access the Application

Open your browser to: `http://localhost:5173`

## Common Windows Issues

### Issue 1: PowerShell Execution Policy

**Error:** "cannot be loaded because running scripts is disabled"

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 2: Port Already in Use

**Error:** "Address already in use"

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Issue 3: Module Not Found

**Error:** "ModuleNotFoundError: No module named..."

**Solution:**
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 4: bcrypt Version Error

**Error:** "(trapped) error reading bcrypt version"

**Solution:**
```powershell
pip uninstall bcrypt -y
pip install bcrypt==3.2.2
```

### Issue 5: SQLite Database Locked

**Error:** "database is locked"

**Solution:**
- Close all connections to the database
- Delete `amida_assistant.db` and restart
- The database will be recreated automatically

## Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Application Settings
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///./amida_assistant.db
FRONTEND_URL=http://localhost:5173

# Google OAuth (Leave empty until configured)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Slack OAuth (Leave empty until configured)
SLACK_CLIENT_ID=
SLACK_CLIENT_SECRET=
SLACK_SIGNING_SECRET=
SLACK_REDIRECT_URI=http://localhost:8000/api/auth/slack/callback
SLACK_BOT_TOKEN=

# Azure OpenAI (Leave empty until configured)
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## Testing the Installation

### Test Backend API

```powershell
# In a new PowerShell window
python test_api.py
```

### Test with curl (if available)

```powershell
# Health check
curl http://localhost:8000/health

# API docs
# Open browser to: http://localhost:8000/docs
```

## Development Tips for Windows

### Use Windows Terminal

Download from Microsoft Store for better terminal experience:
- Multiple tabs
- Better copy/paste
- Unicode support

### Use VS Code

Recommended extensions:
- Python
- Pylance
- ESLint
- Prettier
- REST Client

### File Paths

Remember to use backslashes `\` or forward slashes `/` in paths:
```powershell
# Both work
cd C:\Users\YourName\project
cd C:/Users/YourName/project
```

## Next Steps

1. ✅ Backend and frontend running
2. 🔧 Configure OAuth credentials (optional)
3. 👤 Create your first user account
4. 🚀 Start using the assistant!

## Getting Help

- Check main [README.md](README.md) for features
- Review [SETUP_GUIDE.md](SETUP_GUIDE.md) for OAuth setup
- See [TESTING.md](TESTING.md) for testing procedures
- Read [QUICKSTART.md](QUICKSTART.md) for quick overview

## Troubleshooting Checklist

- [ ] Python version 3.9+ (`python --version`)
- [ ] Virtual environment activated (see `(venv)` in prompt)
- [ ] All dependencies installed (`pip list`)
- [ ] Correct bcrypt version (`pip show bcrypt` should show 3.2.2)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] No firewall blocking ports
- [ ] `.env` file exists in backend directory

---

**Windows-specific setup complete!** 🎉

Your Amida AI Assistant should now be running on Windows without issues.
