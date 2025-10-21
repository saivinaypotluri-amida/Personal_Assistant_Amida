# Amida AI Personal Assistant

A comprehensive agentic AI personal assistant designed for organizations, featuring email summarization, meeting scheduling, and multi-platform integration (Portal & Slack).

## 🌟 Features

### Core Capabilities
1. **Email Management**
   - Automatic email summarization (30-40 words per email)
   - Meeting link extraction from emails
   - Daily digest generation and delivery
   - Support for date range queries

2. **Meeting Scheduling**
   - Smart availability detection
   - Conflict checking
   - Google Meet integration
   - Next available slot finder
   - Multi-attendee support

3. **Multi-Platform Access**
   - Web Portal with modern UI
   - Slack integration with custom commands
   - OAuth-based authentication

### User Roles
- **Regular Users**: Access to email summaries and meeting scheduling
- **Admins**: Full access plus user management, activity logs, and cost tracking

### Integrations
- **Google Workspace**: Gmail & Google Calendar
- **Slack**: Bot with slash commands
- **Azure OpenAI**: LLM for email summarization

## 🏗️ Architecture

```
amida-assistant/
├── backend/                 # FastAPI Backend
│   ├── routes/             # API Routes
│   ├── services/           # Business Logic
│   ├── models.py           # Database Models
│   └── main.py             # Application Entry
├── frontend/               # React Frontend
│   └── src/
│       ├── pages/          # React Pages
│       └── context/        # React Context
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Cloud Project (for Gmail/Calendar API)
- Slack Workspace (for Slack integration)
- Azure OpenAI Account

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials:
# - GOOGLE_CLIENT_ID & GOOGLE_CLIENT_SECRET
# - SLACK_CLIENT_ID, SLACK_CLIENT_SECRET & SLACK_SIGNING_SECRET
# - AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY & AZURE_OPENAI_DEPLOYMENT

# Run the backend
python main.py
```

The backend will run on `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will run on `http://localhost:5173`

### 3. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable APIs:
   - Gmail API
   - Google Calendar API
   - Google+ API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8000/api/auth/google/callback`
5. Copy Client ID and Client Secret to `.env`

### 4. Slack App Setup

1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app (from scratch)
3. Configure OAuth & Permissions:
   - Add scopes: `chat:write`, `commands`, `users:read`, `users:read.email`
   - Add Redirect URL: `http://localhost:8000/api/auth/slack/callback`
4. Create Slash Commands:
   - `/emailsummary` → `http://localhost:8000/api/slack/commands`
   - `/schedule` → `http://localhost:8000/api/slack/commands`
5. Enable Events:
   - Request URL: `http://localhost:8000/api/slack/events`
   - Subscribe to: `app_mention`
6. Install app to workspace
7. Copy credentials to `.env`

### 5. Azure OpenAI Setup

1. Create Azure OpenAI resource in Azure Portal
2. Deploy a model (e.g., GPT-4)
3. Copy endpoint, key, and deployment name to `.env`

## 📖 Usage Guide

### Web Portal

1. **Registration**: Create an account at `/register`
2. **Login**: Access the portal at `/login`
3. **Connect Services**:
   - Click "Connect" for Google Workspace
   - Click "Connect" for Slack
4. **Email Summary**:
   - Enter number of days
   - Click "Get Email Summary"
   - Email digest will be sent to your inbox
5. **Schedule Meeting**:
   - Enter attendee emails (comma-separated)
   - Set duration and title
   - Click "Schedule Meeting"

### Slack Commands

```bash
# Get today's email summary
/emailsummary

# Get email summary for last 7 days
/emailsummary 7 days

# Schedule a 30-minute meeting
/schedule john@company.com,jane@company.com 30 Team Sync

# Mention the bot for help
@Amida Assistant help
```

### Admin Dashboard

Access at `/admin` (admin users only)

Features:
- **User Management**: Create, activate/deactivate, delete users
- **Activity Logs**: Monitor all user actions
- **Cost Tracking**: View API usage and estimated costs
- **Statistics**: Overall system metrics

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- OAuth 2.0 for third-party integrations
- SQLite database with credential encryption
- CORS protection

## 💾 Database Schema

### Users
- id, email, username, hashed_password
- is_admin, is_active
- created_at, updated_at

### Credentials
- id, user_id, service_name
- access_token, refresh_token, token_expiry
- additional_data (JSON)

### Activity Logs
- id, user_id, action, source
- status, details (JSON), timestamp

### Cost Tracking
- id, user_id, service, operation
- tokens_used, estimated_cost, timestamp

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user
- `GET /api/auth/google/url` - Get Google OAuth URL
- `GET /api/auth/slack/url` - Get Slack OAuth URL
- `GET /api/auth/status` - Get service connection status

### Assistant
- `POST /api/assistant/email-summary` - Get email summary
- `POST /api/assistant/schedule-meeting` - Schedule meeting

### Admin (Admin Only)
- `GET /api/admin/users` - List all users
- `POST /api/admin/users` - Create user
- `DELETE /api/admin/users/{id}` - Delete user
- `PATCH /api/admin/users/{id}/toggle-active` - Toggle user status
- `GET /api/admin/logs` - Get activity logs
- `GET /api/admin/costs` - Get cost tracking
- `GET /api/admin/stats/overall` - Get system statistics

### Slack
- `POST /api/slack/events` - Slack event webhook
- `POST /api/slack/commands` - Slack command webhook

## 📊 Cost Tracking

The system tracks Azure OpenAI API usage:
- Tokens used per operation
- Estimated cost (based on $0.002 per 1K tokens)
- Per-user and overall statistics
- 30-day cost reports

## 🎨 UI Features

- **Modern Design**: Clean, professional interface
- **Responsive**: Works on desktop and mobile
- **Real-time Updates**: Instant feedback on actions
- **Rich Email Digest**: Beautiful HTML email formatting
- **Slack Block Kit**: Native Slack message formatting

## 🧪 Testing

### Create Test User

```bash
# Register via UI or use API
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@amida.com",
    "username": "testuser",
    "password": "password123",
    "is_admin": false
  }'
```

### Test Email Summary

```bash
# Via API (requires authentication token)
curl -X POST http://localhost:8000/api/assistant/email-summary \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "days": 1,
    "source": "portal"
  }'
```

## 🐛 Troubleshooting

### Backend won't start
- Check Python version (3.9+)
- Verify all dependencies installed
- Check `.env` file exists

### OAuth redirect fails
- Verify redirect URIs match in OAuth config
- Check backend is running on correct port
- Ensure HTTPS in production

### Slack commands not working
- Verify Slack app is installed to workspace
- Check webhook URLs are publicly accessible (use ngrok for local dev)
- Verify signing secret matches

### Email summary returns no results
- Check Google OAuth is connected
- Verify Gmail API is enabled
- Check date range parameters

## 📝 Development

### Run Backend in Dev Mode
```bash
cd backend
uvicorn main:app --reload
```

### Run Frontend in Dev Mode
```bash
cd frontend
npm run dev
```

### Build for Production
```bash
# Frontend
cd frontend
npm run build

# Backend (use gunicorn or similar)
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🚀 Deployment

### Environment Variables (Production)
- Set `SECRET_KEY` to a strong random value
- Update `FRONTEND_URL` to production URL
- Update OAuth redirect URIs
- Use HTTPS for all endpoints
- Consider PostgreSQL instead of SQLite

### Slack Bot Token
For production, you need to set `SLACK_BOT_TOKEN` environment variable with the bot token from your Slack app.

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Support

For issues and questions:
- Create an issue on GitHub
- Contact support@amida.com

## 🎉 Credits

Built with:
- FastAPI
- React
- Google APIs
- Slack SDK
- Azure OpenAI
- SQLAlchemy

---

Made with ❤️ for Amida Organization
