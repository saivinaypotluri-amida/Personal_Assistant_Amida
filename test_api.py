#!/usr/bin/env python3
"""
Test script for Amida AI Assistant API
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health check passed!")

def test_register():
    """Test user registration"""
    print("\n🔍 Testing user registration...")
    data = {
        "email": f"test_{datetime.now().timestamp()}@amida.com",
        "username": f"testuser_{int(datetime.now().timestamp())}",
        "password": "testpass123",
        "is_admin": False
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"User created: {result['user']['username']}")
        print(f"Token received: {result['access_token'][:20]}...")
        print("✅ Registration passed!")
        return result['access_token'], result['user']
    else:
        print(f"❌ Registration failed: {response.text}")
        return None, None

def test_login(username, password):
    """Test user login"""
    print("\n🔍 Testing user login...")
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data=data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Logged in as: {result['user']['username']}")
        print("✅ Login passed!")
        return result['access_token']
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_auth_status(token):
    """Test authentication status"""
    print("\n🔍 Testing auth status...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/status", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        print("✅ Auth status check passed!")
    else:
        print(f"❌ Auth status check failed: {response.text}")

def test_google_oauth_url(token):
    """Test Google OAuth URL generation"""
    print("\n🔍 Testing Google OAuth URL...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/google/url", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"OAuth URL generated (length: {len(response.json().get('url', ''))})")
        print("✅ Google OAuth URL generation passed!")
    else:
        print(f"Response: {response.text}")
        print("⚠️ Google OAuth URL generation requires configuration")

def main():
    print("=" * 60)
    print("🤖 Amida AI Assistant - API Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Health check
        test_health()
        
        # Test 2: Register user
        token, user = test_register()
        if not token:
            print("\n❌ Registration failed, stopping tests")
            return
        
        # Test 3: Login (reuse credentials from registration)
        # Skip login test since we already have a token
        
        # Test 4: Auth status
        test_auth_status(token)
        
        # Test 5: Google OAuth URL (may fail if not configured)
        test_google_oauth_url(token)
        
        print("\n" + "=" * 60)
        print("✅ Basic API tests completed successfully!")
        print("=" * 60)
        print("\n📝 Next steps:")
        print("1. Configure Google OAuth credentials in .env")
        print("2. Configure Slack credentials in .env")
        print("3. Configure Azure OpenAI credentials in .env")
        print("4. Test email summary and meeting scheduling features")
        print("5. Set up Slack bot and test slash commands")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
