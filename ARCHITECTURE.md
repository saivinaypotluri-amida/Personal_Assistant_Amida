# Amida AI Assistant - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐              ┌──────────────────────┐        │
│  │  Web Portal  │              │   Slack Workspace    │        │
│  │   (React)    │              │   (Slash Commands)   │        │
│  │ Port: 5173   │              │   (Bot Messages)     │        │
│  └──────┬───────┘              └──────────┬───────────┘        │
│         │                                 │                     │
└─────────┼─────────────────────────────────┼─────────────────────┘
          │                                 │
          ▼                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (NGINX)                        │
│                   (Reverse Proxy + SSL)                         │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FastAPI Backend (Port: 8000)                │  │
│  │                                                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │  │
│  │  │   Auth      │  │  Assistant  │  │   Admin     │    │  │
│  │  │   Routes    │  │   Routes    │  │   Routes    │    │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │  │
│  │                                                          │  │
│  │  ┌─────────────┐                                        │  │
│  │  │  Slack Bot  │                                        │  │
│  │  │   Routes    │                                        │  │
│  │  └─────────────┘                                        │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       SERVICE LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │   Gmail    │  │  Calendar  │  │    Slack   │  │   LLM    │ │
│  │  Service   │  │  Service   │  │  Service   │  │ Service  │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  SQLite Database                         │  │
│  │                                                          │  │
│  │  ┌───────┐  ┌──────────┐  ┌────────┐  ┌──────────┐    │  │
│  │  │ Users │  │Credentials│  │ Logs  │  │  Costs   │    │  │
│  │  └───────┘  └──────────┘  └────────┘  └──────────┘    │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │     Google     │  │    Slack     │  │  Azure OpenAI    │   │
│  │   Workspace    │  │      API     │  │       API        │   │
│  │  (Gmail + Cal) │  │              │  │     (GPT-4)      │   │
│  └────────────────┘  └──────────────┘  └──────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### Email Summary Flow

```
User (Portal/Slack)
       │
       ▼
POST /api/assistant/email-summary
       │
       ▼
Verify JWT Token
       │
       ▼
Get Google Credentials from DB
       │
       ▼
Gmail Service → Fetch Emails from Gmail API
       │
       ▼
LLM Service → Summarize each email via Azure OpenAI
       │
       ▼
Format as HTML (for email) or Slack Blocks
       │
       ▼
Gmail Service → Send digest email
       │
       ▼
[If Slack] Slack Service → Post to channel
       │
       ▼
Log Activity + Track Cost
       │
       ▼
Return Response to User
```

### Meeting Scheduling Flow

```
User (Portal/Slack)
       │
       ▼
POST /api/assistant/schedule-meeting
       │
       ▼
Verify JWT Token
       │
       ▼
Get Google Credentials from DB
       │
       ▼
Calendar Service
       │
       ├─→ [If next_available] Find next free slot
       │         │
       │         ├─→ Query all attendees' calendars
       │         ├─→ Find common free time
       │         └─→ Return time slot
       │
       └─→ [If specific time] Check for conflicts
                 │
                 └─→ Query attendees' availability
       │
       ▼
Create Calendar Event
       │
       ├─→ Add attendees
       ├─→ Create Google Meet link
       └─→ Send invites
       │
       ▼
[If Slack] Post confirmation to channel
       │
       ▼
Log Activity
       │
       ▼
Return Meeting Link
```

### OAuth Flow

```
User clicks "Connect Google/Slack"
       │
       ▼
GET /api/auth/{service}/url
       │
       ▼
Generate OAuth URL with scopes
       │
       ▼
Redirect to OAuth Provider
       │
       ▼
User authorizes application
       │
       ▼
Redirect to /api/auth/{service}/callback?code=...
       │
       ▼
Exchange code for tokens
       │
       ▼
Store tokens in database
       │
       ├─→ access_token
       ├─→ refresh_token
       ├─→ expiry
       └─→ additional_data
       │
       ▼
Redirect to Dashboard with success message
```

## Component Breakdown

### Backend Components

#### 1. Authentication Module
```python
auth.py
├── verify_password()         # Bcrypt verification
├── get_password_hash()       # Bcrypt hashing
├── create_access_token()     # JWT generation
├── get_current_user()        # JWT validation
└── get_current_admin_user()  # Admin authorization
```

#### 2. API Routes
```python
routes/
├── auth_routes.py
│   ├── /register          POST
│   ├── /login            POST
│   ├── /me               GET
│   ├── /google/url       GET
│   ├── /google/callback  GET
│   ├── /slack/url        GET
│   ├── /slack/callback   GET
│   └── /status           GET
│
├── assistant_routes.py
│   ├── /email-summary        POST
│   └── /schedule-meeting     POST
│
├── admin_routes.py
│   ├── /users                GET, POST
│   ├── /users/{id}           DELETE
│   ├── /users/{id}/toggle    PATCH
│   ├── /logs                 GET
│   ├── /costs                GET
│   └── /stats/overall        GET
│
└── slack_bot.py
    ├── /events           POST
    └── /commands         POST
```

#### 3. Services
```python
services/
├── gmail_service.py
│   ├── get_emails()          # Fetch emails
│   ├── send_email()          # Send email
│   └── get_user_email()      # Get user email
│
├── calendar_service.py
│   ├── find_next_available_slot()
│   ├── check_conflicts()
│   └── create_meeting()
│
├── llm_service.py
│   ├── summarize_email()
│   ├── format_email_digest()
│   └── format_slack_message()
│
└── slack_service.py
    ├── post_message()
    └── get_user_info()
```

#### 4. Database Models
```python
models.py
├── User
│   ├── id, email, username
│   ├── hashed_password
│   ├── is_admin, is_active
│   └── relationships
│
├── Credential
│   ├── id, user_id, service_name
│   ├── access_token, refresh_token
│   └── token_expiry, additional_data
│
├── ActivityLog
│   ├── id, user_id, action
│   ├── source, status
│   └── details, timestamp
│
└── CostTracking
    ├── id, user_id, service
    ├── operation, tokens_used
    └── estimated_cost, timestamp
```

### Frontend Components

```
src/
├── App.jsx                    # Main app with routing
├── context/
│   └── AuthContext.jsx       # Global auth state
│
└── pages/
    ├── Login.jsx             # Login form
    ├── Register.jsx          # Registration form
    ├── Dashboard.jsx         # User dashboard
    │   ├── Service connection status
    │   ├── Email summary form
    │   ├── Meeting scheduling form
    │   └── Slack integration info
    │
    └── AdminDashboard.jsx    # Admin panel
        ├── User management table
        ├── Activity logs table
        ├── Cost tracking table
        └── Statistics cards
```

## Security Architecture

### Authentication Flow
```
Client Request
     │
     ▼
JWT Token in Authorization Header
     │
     ▼
Verify Token Signature (JWT)
     │
     ├─→ Valid → Extract user_id
     │              │
     │              ▼
     │         Query User from DB
     │              │
     │              ├─→ User exists → Allow access
     │              └─→ User not found → 401
     │
     └─→ Invalid → 401 Unauthorized
```

### OAuth Token Storage
```
Tokens stored in database with:
├── Encryption at rest (database level)
├── Access token (temporary)
├── Refresh token (long-lived)
├── Expiry timestamp
└── Service-specific data
```

## Scalability Considerations

### Horizontal Scaling
```
Load Balancer
     │
     ├─→ Backend Instance 1
     ├─→ Backend Instance 2
     ├─→ Backend Instance 3
     └─→ Backend Instance N
            │
            ▼
     Shared Database
```

### Database Scaling
```
Primary Database (Write)
     │
     ├─→ Read Replica 1
     ├─→ Read Replica 2
     └─→ Read Replica N
```

### Caching Layer (Future)
```
Client Request
     │
     ▼
Redis Cache
     │
     ├─→ Cache Hit → Return cached data
     └─→ Cache Miss → Query database
                       └─→ Store in cache
```

## Technology Stack

### Backend
- **Runtime**: Python 3.9+
- **Framework**: FastAPI 0.115.0
- **Server**: Uvicorn (ASGI)
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: JWT (python-jose)
- **Password**: Bcrypt (passlib)

### Frontend
- **Runtime**: Node.js 18+
- **Framework**: React 18
- **Build Tool**: Vite 5
- **Routing**: React Router 6
- **HTTP Client**: Axios
- **Icons**: Lucide React

### External APIs
- **Email**: Gmail API
- **Calendar**: Google Calendar API
- **Chat**: Slack API & Slack Bolt
- **AI**: Azure OpenAI (GPT-4)

## Deployment Architecture

### Development
```
Localhost:5173 (Frontend) → Localhost:8000 (Backend) → SQLite
```

### Production
```
CDN (Frontend) → Load Balancer → Backend Servers → PostgreSQL
                                      │
                                      ├─→ Redis Cache
                                      ├─→ File Storage
                                      └─→ External APIs
```

## Monitoring & Logging

### Application Metrics
- Request rate
- Response time
- Error rate
- Active users

### Business Metrics
- Email summaries generated
- Meetings scheduled
- API costs
- User activity

### Infrastructure Metrics
- CPU usage
- Memory usage
- Disk I/O
- Network traffic

## Performance Targets

- **API Response Time**: < 200ms (p95)
- **Email Summary**: < 5s per request
- **Meeting Scheduling**: < 3s per request
- **Database Queries**: < 50ms (p95)
- **Concurrent Users**: 100+
- **Uptime**: 99.9%

---

This architecture supports:
✅ High availability
✅ Horizontal scaling
✅ Security best practices
✅ Monitoring & observability
✅ Future enhancements
