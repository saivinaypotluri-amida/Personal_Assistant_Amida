# User-Specific OAuth Configuration Guide

## Overview

Each user can now configure their **own OAuth credentials** through the portal UI. This allows:
- ✅ Each user to use their own Google/Slack apps
- ✅ Complete isolation between users
- ✅ No shared credentials in `.env` file
- ✅ Multi-tenant support

---

## How It Works

### 1. User Configures Credentials
```
User logs in → Dashboard → "Configure Credentials" button
  ↓
Credential configuration form
  ↓
Enters Client ID, Client Secret, etc.
  ↓
Saves to database (oauth_configs table)
```

### 2. User Connects Service
```
Dashboard → "Connect" button → OAuth flow
  ↓
Uses user's saved credentials for OAuth
  ↓
Tokens stored in database (credentials table)
```

---

## User Journey

### Step 1: Login to Portal

Go to http://localhost:5173 and login.

### Step 2: Click "Configure Credentials"

On the dashboard, find the "Connected Services" section and click the **"Configure Credentials"** button.

### Step 3: Configure Each Service

You'll see tabs for:
- **Google Workspace**
- **Slack**
- **Azure OpenAI**

#### For Google Workspace:

1. Get your credentials from [Google Cloud Console](https://console.cloud.google.com)
2. Enter:
   - **Client ID**: `123456789-abc...apps.googleusercontent.com`
   - **Client Secret**: `GOCSPX-abc...`
   - **Redirect URI**: `http://localhost:8000/api/auth/google/callback`
3. Click "Save Google Configuration"
4. ✅ Success message appears!

#### For Slack:

1. Get your credentials from [Slack API](https://api.slack.com/apps)
2. Enter:
   - **Client ID**: `1234567890.1234567890`
   - **Client Secret**: `abc123...`
   - **Signing Secret**: `abc123...`
   - **Bot Token**: `xoxb-...` (optional, for bot features)
   - **Redirect URI**: `http://localhost:8000/api/auth/slack/callback`
3. Click "Save Slack Configuration"
4. ✅ Success message appears!

#### For Azure OpenAI:

1. Get your credentials from [Azure Portal](https://portal.azure.com)
2. Enter:
   - **Endpoint**: `https://your-resource.openai.azure.com/`
   - **API Key**: `abc123...`
   - **Deployment Name**: `gpt-4`
   - **API Version**: `2024-02-15-preview`
3. Click "Save Azure Configuration"
4. ✅ Success message appears!

### Step 4: Return to Dashboard

Click "Back to Dashboard"

### Step 5: Connect Services

Now you can click the **"Connect"** buttons:

1. **Google Workspace**: Click "Connect" → Authorize on Google → Redirected back ✅
2. **Slack**: Click "Connect" → Authorize on Slack → Redirected back ✅

---

## Database Structure

### oauth_configs Table

Stores user-specific OAuth app credentials:

```sql
CREATE TABLE oauth_configs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,  -- Which user owns this config
    service_name TEXT,  -- 'google', 'slack', 'azure_openai'
    client_id TEXT,  -- OAuth Client ID
    client_secret TEXT,  -- OAuth Client Secret
    additional_config JSON,  -- Service-specific settings
    is_configured BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### credentials Table

Stores OAuth access tokens (after successful connection):

```sql
CREATE TABLE credentials (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    service_name TEXT,
    access_token TEXT,  -- OAuth access token
    refresh_token TEXT,  -- OAuth refresh token
    token_expiry TIMESTAMP,
    additional_data JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## API Endpoints

### Save OAuth Configuration
```http
POST /api/auth/config/save
Authorization: Bearer <token>
Content-Type: application/json

{
  "service": "google",
  "client_id": "123456789-abc...apps.googleusercontent.com",
  "client_secret": "GOCSPX-abc...",
  "additional_config": {
    "redirect_uri": "http://localhost:8000/api/auth/google/callback"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "service": "google",
  "client_id": "123456789-...",
  "is_configured": true,
  "created_at": "2025-10-21T10:00:00"
}
```

### Get OAuth Configuration
```http
GET /api/auth/config/{service}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "service": "google",
  "client_id": "123456789-...",  // Masked for security
  "is_configured": true,
  "created_at": "2025-10-21T10:00:00"
}
```

### Get Auth Status
```http
GET /api/auth/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "google": {
    "configured": true,  // Has OAuth config
    "connected": true   // Has valid tokens
  },
  "slack": {
    "configured": true,
    "connected": false
  },
  "azure_openai": {
    "configured": false,
    "connected": false
  }
}
```

---

## OAuth Flow with User Credentials

### Before (Shared Credentials):
```
User clicks "Connect"
  ↓
Uses credentials from .env file (shared by all users)
  ↓
OAuth flow
  ↓
Tokens stored
```

### After (Per-User Credentials):
```
User clicks "Connect"
  ↓
Backend fetches user's oauth_config from database
  ↓
Uses user's own Client ID & Secret for OAuth
  ↓
OAuth flow with user's app
  ↓
Tokens stored for that user
```

---

## Security Features

### 1. Client Secret Masking

When displaying configurations, Client Secrets are masked:
```javascript
// Display: "GOCSPX-abc..."
// Stored: Full secret in database
```

### 2. Show/Hide Toggle

UI has eye icon to show/hide secrets:
```jsx
<input type={showSecret ? "text" : "password"} />
<button onClick={() => setShowSecret(!showSecret)}>
  {showSecret ? <EyeOff /> : <Eye />}
</button>
```

### 3. Per-User Isolation

Each user's credentials are completely isolated:
- User A's Google app ≠ User B's Google app
- Tokens are user-specific
- No credential sharing

---

## Migration from Shared to Per-User

If you have existing shared credentials in `.env`:

### Option 1: Keep Shared (Fallback)

Backend can fall back to `.env` if user hasn't configured:

```python
# In auth_routes.py
oauth_config = get_user_config(user_id, "google")
if not oauth_config:
    # Fallback to .env
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
else:
    # Use user's config
    client_id = oauth_config.client_id
    client_secret = oauth_config.client_secret
```

### Option 2: Require User Config

Force all users to configure (current implementation):

```python
if not oauth_config:
    raise HTTPException(
        status_code=400,
        detail="Please configure your OAuth credentials first"
    )
```

---

## Testing

### 1. Start Fresh

```powershell
# Delete database to test from scratch
cd backend
rm amida_assistant.db

# Restart backend
python main.py
```

### 2. Register First User

- Go to http://localhost:5173
- Register account
- ✅ You're automatically admin (first user)

### 3. Configure Credentials

- Click "Configure Credentials"
- Add Google OAuth credentials
- Add Slack OAuth credentials
- Add Azure OpenAI credentials
- All saved!

### 4. Connect Services

- Return to dashboard
- Click "Connect" for Google
- Authorize on Google
- ✅ Connected!
- Repeat for Slack

### 5. Test Features

- Try "Email Summary"
- Try "Schedule Meeting"
- Try Slack commands: `/emailsummary`

---

## Advantages

✅ **Multi-Tenant**: Each user has own OAuth apps
✅ **Secure**: Credentials isolated per user
✅ **Flexible**: Users can use different Google/Slack workspaces
✅ **No Shared Secrets**: No credentials in `.env` to leak
✅ **Scalable**: Supports unlimited users with their own apps
✅ **Compliance**: Better for enterprise/regulated industries

---

## Files Changed

### Backend:
- `models.py` - Added `OAuthConfig` model
- `schemas.py` - Added OAuth config schemas
- `routes/auth_routes.py` - User-specific OAuth flow
- `database.py` - Auto-creates new table

### Frontend:
- `pages/ConfigureOAuth.jsx` - NEW credential configuration UI
- `pages/Dashboard.jsx` - Added "Configure Credentials" button
- `App.jsx` - Added route for `/configure-oauth`

---

## Next Steps

1. ✅ Restart backend (to create new table)
2. ✅ Restart frontend
3. ✅ Login to portal
4. ✅ Click "Configure Credentials"
5. ✅ Enter your OAuth credentials
6. ✅ Save and connect services
7. ✅ Test email summary and meetings!

---

**Now each user configures their own credentials!** 🎉
