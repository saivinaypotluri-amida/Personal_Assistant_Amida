# HTTPS Redirect URLs Configuration Guide

## Overview

Google and Slack require **HTTPS** redirect URLs for OAuth. Since you're developing locally, you need to use **ngrok** to get HTTPS URLs.

---

## ✅ **Changes Made**

All redirect URLs have been updated to use **HTTPS** instead of HTTP:

### Backend:
- ✅ `config.py` - Default redirect URIs now use HTTPS
- ✅ `.env.example` - Updated with ngrok placeholder
- ✅ `.env` - Updated with ngrok placeholder
- ✅ OAuth callback handlers - Return proper HTTP redirects

### Frontend:
- ✅ `ConfigureOAuth.jsx` - Default redirect URIs use HTTPS placeholder

---

## 🚀 **How to Set Up HTTPS Redirect URLs**

### **Step 1: Get Your Ngrok URL**

Check your ngrok terminal. You should see:
```
Forwarding    https://unpresidential-leontine-eighthly.ngrok-free.dev -> http://localhost:8000
```

Copy that HTTPS URL: `https://unpresidential-leontine-eighthly.ngrok-free.dev`

---

### **Step 2: Configure in Slack App**

#### **A. Add Redirect URL**

1. Go to: https://api.slack.com/apps
2. Click your app
3. Click **"OAuth & Permissions"** (left sidebar)
4. Scroll to **"Redirect URLs"**
5. Click **"Add New Redirect URL"**
6. Paste:
   ```
   https://unpresidential-leontine-eighthly.ngrok-free.dev/api/auth/slack/callback
   ```
7. Click **"Add"**
8. Click **"Save URLs"** at the bottom ← **MUST DO THIS!**

#### **B. Verify Event Subscriptions URL**

While you're here, also verify:

1. Click **"Event Subscriptions"** (left sidebar)
2. Check **"Request URL"** shows:
   ```
   https://unpresidential-leontine-eighthly.ngrok-free.dev/api/slack/events
   ```
3. Should show ✓ "Verified"

---

### **Step 3: Configure in Google Cloud Console**

1. Go to: https://console.cloud.google.com
2. Select your project
3. Go to **"APIs & Services"** → **"Credentials"**
4. Click on your OAuth 2.0 Client ID
5. Under **"Authorized redirect URIs"**, click **"+ ADD URI"**
6. Paste:
   ```
   https://unpresidential-leontine-eighthly.ngrok-free.dev/api/auth/google/callback
   ```
7. Click **"Save"**

---

### **Step 4: Configure in Portal**

Now configure the credentials in your portal:

1. Go to: http://localhost:5173
2. Login
3. Click **"Configure Credentials"** button

#### **For Slack:**

1. Click **"Slack"** tab
2. Fill in:
   - **Client ID**: (from Slack app → Basic Information)
   - **Client Secret**: (from Slack app → Basic Information)
   - **Signing Secret**: (from Slack app → Basic Information)
   - **Bot Token**: (from Slack app → OAuth & Permissions) - Optional
   - **Redirect URI**: `https://unpresidential-leontine-eighthly.ngrok-free.dev/api/auth/slack/callback`
3. Click **"Save Slack Configuration"**
4. ✅ Success!

#### **For Google:**

1. Click **"Google Workspace"** tab
2. Fill in:
   - **Client ID**: (from Google Cloud Console)
   - **Client Secret**: (from Google Cloud Console)
   - **Redirect URI**: `https://unpresidential-leontine-eighthly.ngrok-free.dev/api/auth/google/callback`
3. Click **"Save Google Configuration"**
4. ✅ Success!

---

### **Step 5: Restart Backend (Important!)**

In your PowerShell where backend is running:

```powershell
# Press Ctrl+C to stop backend

# Restart it:
cd backend
python main.py
```

---

### **Step 6: Try Connecting**

1. Go to Dashboard
2. Click **"Connect"** for Slack
3. ✅ Should work now!

---

## 🎯 **Summary of URLs to Configure**

Replace `unpresidential-leontine-eighthly.ngrok-free.dev` with your actual ngrok URL:

### **In Slack App (https://api.slack.com/apps):**

| Location | URL |
|----------|-----|
| OAuth & Permissions → Redirect URLs | `https://unpresidential-leontine-eighthly.ngrok-free.dev/api/auth/slack/callback` |
| Event Subscriptions → Request URL | `https://unpresidential-leontine-eighthly.ngrok-free.dev/api/slack/events` |

### **In Google Cloud Console:**

| Location | URL |
|----------|-----|
| Credentials → OAuth Client → Authorized redirect URIs | `https://unpresidential-leontine-eighthly.ngrok-free.dev/api/auth/google/callback` |

### **In Portal (Configure Credentials):**

| Service | Redirect URI Field |
|---------|-------------------|
| Google Workspace | `https://unpresidential-leontine-eighthly.ngrok-free.dev/api/auth/google/callback` |
| Slack | `https://unpresidential-leontine-eighthly.ngrok-free.dev/api/auth/slack/callback` |

---

## ⚠️ **Important: Ngrok URL Changes**

Every time you restart ngrok, the URL changes! You'll need to:

1. Update Slack app redirect URLs
2. Update Google Cloud redirect URIs
3. Update portal configuration
4. Restart backend

### **Solution: Use Ngrok Static Domain (Free)**

```powershell
# Sign up at ngrok.com for free account
# Get your authtoken from dashboard

ngrok config add-authtoken YOUR_AUTH_TOKEN

# Use static domain (free tier gets one)
ngrok http 8000 --domain=your-static-name.ngrok-free.app
```

Then your URL never changes! 🎉

---

## 🧪 **Testing**

After configuring everything:

```powershell
# Test Slack redirect URI is accepted
curl -I "https://unpresidential-leontine-eighthly.ngrok-free.dev/api/auth/slack/callback"

# Should return 405 or similar (not 404)
```

---

## ✅ **Action Items**

1. ✅ Code updated to use HTTPS
2. ✅ Pushed to GitHub
3. 🔧 **YOU NEED TO DO**: Add HTTPS redirect URL in Slack app settings
4. 🔧 **YOU NEED TO DO**: Add HTTPS redirect URI in Google Cloud Console
5. 🔧 **YOU NEED TO DO**: Configure in portal with ngrok HTTPS URLs
6. 🔧 **YOU NEED TO DO**: Restart backend

---

**The code is ready for HTTPS! Now just add the ngrok URLs to Slack and Google settings.** 🚀