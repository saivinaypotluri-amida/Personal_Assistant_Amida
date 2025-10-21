from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Dict, Any
import httpx
import json

from database import get_db
from models import User, Credential
from schemas import UserCreate, UserLogin, Token, UserResponse, OAuthConfig
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        is_admin=user_data.is_admin
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": db_user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user"""
    
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


# Google OAuth
@router.get("/google/url")
async def get_google_auth_url(current_user: User = Depends(get_current_user)):
    """Get Google OAuth authorization URL"""
    
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Google OAuth not configured")
    
    scopes = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/userinfo.email'
    ]
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope={' '.join(scopes)}&"
        f"access_type=offline&"
        f"prompt=consent&"
        f"state={current_user.id}"
    )
    
    return {"url": auth_url}


@router.get("/google/callback")
async def google_oauth_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=400, detail="Google OAuth not configured")
    
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
        
        tokens = response.json()
    
    # Save credentials
    user_id = int(state)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if credential exists
    credential = db.query(Credential).filter(
        Credential.user_id == user_id,
        Credential.service_name == "google"
    ).first()
    
    token_expiry = datetime.utcnow() + timedelta(seconds=tokens.get('expires_in', 3600))
    
    if credential:
        credential.access_token = tokens['access_token']
        credential.refresh_token = tokens.get('refresh_token', credential.refresh_token)
        credential.token_expiry = token_expiry
        credential.additional_data = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET
        }
    else:
        credential = Credential(
            user_id=user_id,
            service_name="google",
            access_token=tokens['access_token'],
            refresh_token=tokens.get('refresh_token'),
            token_expiry=token_expiry,
            additional_data={
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET
            }
        )
        db.add(credential)
    
    db.commit()
    
    return {"message": "Google account connected successfully", "redirect": f"{settings.FRONTEND_URL}/dashboard"}


# Slack OAuth
@router.get("/slack/url")
async def get_slack_auth_url(current_user: User = Depends(get_current_user)):
    """Get Slack OAuth authorization URL"""
    
    if not settings.SLACK_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Slack OAuth not configured")
    
    scopes = [
        'chat:write',
        'commands',
        'users:read',
        'users:read.email',
        'channels:history',
        'groups:history',
        'im:history',
        'mpim:history'
    ]
    
    auth_url = (
        f"https://slack.com/oauth/v2/authorize?"
        f"client_id={settings.SLACK_CLIENT_ID}&"
        f"redirect_uri={settings.SLACK_REDIRECT_URI}&"
        f"scope={','.join(scopes)}&"
        f"state={current_user.id}"
    )
    
    return {"url": auth_url}


@router.get("/slack/callback")
async def slack_oauth_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Slack OAuth callback"""
    
    if not settings.SLACK_CLIENT_ID or not settings.SLACK_CLIENT_SECRET:
        raise HTTPException(status_code=400, detail="Slack OAuth not configured")
    
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://slack.com/api/oauth.v2.access",
            data={
                "code": code,
                "client_id": settings.SLACK_CLIENT_ID,
                "client_secret": settings.SLACK_CLIENT_SECRET,
                "redirect_uri": settings.SLACK_REDIRECT_URI
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
        
        data = response.json()
        
        if not data.get('ok'):
            raise HTTPException(status_code=400, detail="Slack OAuth failed")
    
    # Save credentials
    user_id = int(state)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    credential = db.query(Credential).filter(
        Credential.user_id == user_id,
        Credential.service_name == "slack"
    ).first()
    
    if credential:
        credential.access_token = data['access_token']
        credential.additional_data = {
            'team_id': data.get('team', {}).get('id'),
            'team_name': data.get('team', {}).get('name'),
            'bot_user_id': data.get('bot_user_id')
        }
    else:
        credential = Credential(
            user_id=user_id,
            service_name="slack",
            access_token=data['access_token'],
            additional_data={
                'team_id': data.get('team', {}).get('id'),
                'team_name': data.get('team', {}).get('name'),
                'bot_user_id': data.get('bot_user_id')
            }
        )
        db.add(credential)
    
    db.commit()
    
    return {"message": "Slack workspace connected successfully", "redirect": f"{settings.FRONTEND_URL}/dashboard"}


# Azure OpenAI Configuration
@router.post("/azure/configure")
async def configure_azure_openai(
    config: OAuthConfig,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Configure Azure OpenAI credentials"""
    
    credential = db.query(Credential).filter(
        Credential.user_id == current_user.id,
        Credential.service_name == "azure_openai"
    ).first()
    
    if credential:
        credential.additional_data = config.additional_config
    else:
        credential = Credential(
            user_id=current_user.id,
            service_name="azure_openai",
            additional_data=config.additional_config
        )
        db.add(credential)
    
    db.commit()
    
    return {"message": "Azure OpenAI configured successfully"}


@router.get("/status")
async def get_auth_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get authentication status for all services"""
    
    credentials = db.query(Credential).filter(Credential.user_id == current_user.id).all()
    
    status = {
        'google': False,
        'slack': False,
        'azure_openai': False
    }
    
    for cred in credentials:
        status[cred.service_name] = True
    
    return status
