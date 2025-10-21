#!/usr/bin/env python3
"""
Quick test to verify JWT token creation and validation
"""
import sys
sys.path.insert(0, '/workspace/backend')

from auth import create_access_token, get_password_hash, verify_password
from jose import jwt
from config import settings

# Test token creation (sub must be string)
user_id = 1
token = create_access_token(data={"sub": str(user_id)})
print(f"Created token: {token[:50]}...")

# Decode and verify
try:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    print(f"Token payload: {payload}")
    print(f"User ID from token: {payload.get('sub')}")
    print(f"User ID type: {type(payload.get('sub'))}")
except Exception as e:
    print(f"Error decoding token: {e}")

# Test password hashing
password = "testpass123"
hashed = get_password_hash(password)
print(f"\nPassword hash: {hashed[:50]}...")
print(f"Verification: {verify_password(password, hashed)}")
