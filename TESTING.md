# Testing Guide for Amida AI Assistant

## Automated Testing

### Backend API Tests

Start the backend server in one terminal:
```bash
cd backend
export PATH="$PATH:/home/ubuntu/.local/bin"
python3 main.py
```

In another terminal, run the test script:
```bash
python3 test_api.py
```

This will test:
- ✅ Health endpoint
- ✅ User registration
- ✅ Authentication
- ✅ OAuth URL generation

## Manual Testing

### 1. Authentication Flow

**Test Registration:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@amida.com",
    "username": "testuser",
    "password": "testpass123",
    "is_admin": false
  }'
```

Expected response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "test@amida.com",
    "username": "testuser",
    "is_admin": false,
    "is_active": true
  }
}
```

**Test Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"
```

### 2. Protected Endpoints

**Get Current User:**
```bash
# Replace TOKEN with your actual token
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

**Get Auth Status:**
```bash
curl -X GET http://localhost:8000/api/auth/status \
  -H "Authorization: Bearer TOKEN"
```

### 3. Email Summary (Requires Google OAuth)

```bash
curl -X POST http://localhost:8000/api/assistant/email-summary \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "days": 1,
    "source": "portal"
  }'
```

Expected response:
```json
{
  "summaries": [
    {
      "subject": "Meeting tomorrow",
      "from_email": "colleague@company.com",
      "date": "Mon, 21 Oct 2025 10:00:00",
      "summary": "Brief summary of the email...",
      "meeting_links": ["https://meet.google.com/abc-def-ghi"]
    }
  ],
  "total_emails": 1,
  "digest_sent": true
}
```

### 4. Meeting Scheduling (Requires Google OAuth)

```bash
curl -X POST http://localhost:8000/api/assistant/schedule-meeting \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "attendees": ["colleague@company.com"],
    "duration_minutes": 30,
    "title": "Test Meeting",
    "next_available": true,
    "source": "portal"
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Meeting scheduled successfully!",
  "meeting_link": "https://meet.google.com/abc-def-ghi"
}
```

### 5. Admin Endpoints (Requires Admin Role)

**Get All Users:**
```bash
curl -X GET http://localhost:8000/api/admin/users \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Get Activity Logs:**
```bash
curl -X GET http://localhost:8000/api/admin/logs \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Get Cost Tracking:**
```bash
curl -X GET http://localhost:8000/api/admin/costs \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Get Overall Stats:**
```bash
curl -X GET http://localhost:8000/api/admin/stats/overall \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## Frontend Testing

### 1. User Interface Testing

**Login Page:**
- Navigate to `http://localhost:5173/login`
- Enter credentials
- Click "Sign In"
- Should redirect to dashboard

**Registration Page:**
- Navigate to `http://localhost:5173/register`
- Fill in form
- Click "Create Account"
- Should redirect to dashboard

**Dashboard:**
- Check "Connected Services" section
- Try "Email Summary" (requires Google OAuth)
- Try "Schedule Meeting" (requires Google OAuth)
- Check Slack integration info

**Admin Dashboard (Admin Only):**
- Click "Admin" button
- Check all tabs:
  - Users
  - Activity Logs
  - Cost Tracking
  - Statistics

### 2. Integration Testing

**Google OAuth Flow:**
1. Click "Connect" for Google Workspace
2. Authorize the application
3. Should redirect back with success message
4. Status should show green checkmark

**Slack OAuth Flow:**
1. Click "Connect" for Slack
2. Authorize the application
3. Should redirect back with success message
4. Status should show green checkmark

## Slack Bot Testing

### Prerequisites
- Slack app installed to workspace
- Slack bot token configured
- ngrok or similar for local development

### Test Commands

**In any Slack channel:**

```
/emailsummary
```
Expected: Email digest posted to Slack thread

```
/emailsummary 7 days
```
Expected: Email digest for last 7 days

```
/schedule john@company.com,jane@company.com 30 Team Sync
```
Expected: Meeting scheduled, confirmation message posted

**Mention the bot:**
```
@Amida Assistant help
```
Expected: Help message with available commands

## Load Testing

### Using Apache Bench (ab)

```bash
# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Test registration endpoint
ab -n 100 -c 5 -p register_data.json \
   -T application/json \
   http://localhost:8000/api/auth/register
```

### Using Python

```python
import asyncio
import aiohttp

async def test_endpoint(session, url):
    async with session.get(url) as response:
        return await response.json()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [test_endpoint(session, 'http://localhost:8000/health') for _ in range(100)]
        results = await asyncio.gather(*tasks)
        print(f"Completed {len(results)} requests")

asyncio.run(main())
```

## Database Testing

### Check Database Contents

```bash
cd backend
sqlite3 amida_assistant.db

# List all users
SELECT * FROM users;

# List all credentials
SELECT * FROM credentials;

# List recent activity
SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT 10;

# Check cost tracking
SELECT SUM(estimated_cost) as total_cost FROM cost_tracking;

# Exit
.exit
```

### Reset Database

```bash
cd backend
rm amida_assistant.db
python3 main.py  # Will recreate the database
```

## Performance Benchmarks

### Expected Response Times

- Health check: < 10ms
- User registration: < 100ms
- Login: < 100ms
- Email summary: 2-5 seconds (depends on email count)
- Meeting scheduling: 1-3 seconds
- Admin dashboard: < 200ms

### Expected Throughput

- Health endpoint: 1000+ req/s
- Authentication: 100+ req/s
- AI operations: 10+ req/s (limited by Azure OpenAI)

## Security Testing

### Test Invalid Authentication

```bash
# No token
curl -X GET http://localhost:8000/api/auth/me

# Invalid token
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer invalid_token"
```

Both should return 401 Unauthorized.

### Test Admin Access

```bash
# Non-admin user accessing admin endpoint
curl -X GET http://localhost:8000/api/admin/users \
  -H "Authorization: Bearer NON_ADMIN_TOKEN"
```

Should return 403 Forbidden.

## Troubleshooting Tests

### Backend not responding
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check logs
cd backend
tail -f logs/app.log  # if logging is enabled
```

### Database errors
```bash
# Check database file exists
ls -la backend/amida_assistant.db

# Check database integrity
sqlite3 backend/amida_assistant.db "PRAGMA integrity_check;"
```

### OAuth errors
- Verify redirect URIs match in OAuth config
- Check credentials are set in .env
- Verify APIs are enabled in Google/Slack console

## CI/CD Testing

### GitHub Actions Example

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: python3 test_api.py
```

## Test Coverage

Target coverage goals:
- API endpoints: 80%+
- Business logic: 90%+
- UI components: 70%+

## Reporting Issues

When reporting bugs, include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/logs
- Environment details (OS, Python version, etc.)

---

Happy Testing! 🧪
