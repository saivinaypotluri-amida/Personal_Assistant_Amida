from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Dict, Any
import httpx
import json

from database import get_db
from models import User, Credential, OAuthConfig as OAuthConfigModel
from schemas import UserCreate, UserLogin, Token, UserResponse, OAuthConfigCreate, OAuthConfigResponse
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
    
    # Check if this is the first user - if so, make them admin
    user_count = db.query(User).count()
    is_first_user = user_count == 0
    
    # Create new user
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        is_admin=user_data.is_admin or is_first_user  # First user is always admin
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token (sub must be string)
    access_token = create_access_token(
        data={"sub": str(db_user.id)},
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
        data={"sub": str(user.id)},
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


# Save OAuth Configuration
@router.post("/config/save", response_model=OAuthConfigResponse)
async def save_oauth_config(
    config: OAuthConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save OAuth configuration for a service"""
    
    # Check if config already exists
    existing = db.query(OAuthConfigModel).filter(
        OAuthConfigModel.user_id == current_user.id,
        OAuthConfigModel.service_name == config.service
    ).first()
    
    if existing:
        # Update existing
        existing.client_id = config.client_id
        existing.client_secret = config.client_secret
        existing.additional_config = config.additional_config
        existing.is_configured = True
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        oauth_config = existing
    else:
        # Create new
        oauth_config = OAuthConfigModel(
            user_id=current_user.id,
            service_name=config.service,
            client_id=config.client_id,
            client_secret=config.client_secret,
            additional_config=config.additional_config,
            is_configured=True
        )
        db.add(oauth_config)
        db.commit()
        db.refresh(oauth_config)
    
    # Return masked client_id for security
    response = OAuthConfigResponse(
        id=oauth_config.id,
        service=oauth_config.service_name,
        client_id=oauth_config.client_id[:10] + "..." if len(oauth_config.client_id) > 10 else oauth_config.client_id,
        is_configured=oauth_config.is_configured,
        created_at=oauth_config.created_at
    )
    
    return response


@router.get("/config/{service}", response_model=OAuthConfigResponse)
async def get_oauth_config(
    service: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get OAuth configuration for a service"""
    
    config = db.query(OAuthConfigModel).filter(
        OAuthConfigModel.user_id == current_user.id,
        OAuthConfigModel.service_name == service
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail=f"{service} configuration not found")
    
    # Return masked client_id for security
    return OAuthConfigResponse(
        id=config.id,
        service=config.service_name,
        client_id=config.client_id[:10] + "..." if len(config.client_id) > 10 else config.client_id,
        is_configured=config.is_configured,
        created_at=config.created_at
    )


# Google OAuth
@router.get("/google/url")
async def get_google_auth_url(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Google OAuth authorization URL using user's configured credentials"""
    
    # Get user's OAuth config
    oauth_config = db.query(OAuthConfigModel).filter(
        OAuthConfigModel.user_id == current_user.id,
        OAuthConfigModel.service_name == "google"
    ).first()
    
    if not oauth_config or not oauth_config.is_configured:
        raise HTTPException(
            status_code=400, 
            detail="Please configure your Google OAuth credentials first"
        )
    
    scopes = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/userinfo.email'
    ]
    
    # Use user's redirect URI or default
    redirect_uri = oauth_config.additional_config.get('redirect_uri', settings.GOOGLE_REDIRECT_URI) if oauth_config.additional_config else settings.GOOGLE_REDIRECT_URI
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={oauth_config.client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={' '.join(scopes)}&"
        f"access_type=offline&"
        f"prompt=consent&"
        f"state={current_user.id}"
    )
    
    return {"url": auth_url}


@router.get("/google/callback")
async def google_oauth_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback using user's configured credentials"""
    
    user_id = int(state)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's OAuth config
    oauth_config = db.query(OAuthConfigModel).filter(
        OAuthConfigModel.user_id == user_id,
        OAuthConfigModel.service_name == "google"
    ).first()
    
    if not oauth_config:
        raise HTTPException(status_code=400, detail="Google OAuth not configured for this user")
    
    redirect_uri = oauth_config.additional_config.get('redirect_uri', settings.GOOGLE_REDIRECT_URI) if oauth_config.additional_config else settings.GOOGLE_REDIRECT_URI
    
    # Exchange code for tokens using user's credentials
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": oauth_config.client_id,
                "client_secret": oauth_config.client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
        
        tokens = response.json()
    
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
            'client_id': oauth_config.client_id,
            'client_secret': oauth_config.client_secret
        }
    else:
        credential = Credential(
            user_id=user_id,
            service_name="google",
            access_token=tokens['access_token'],
            refresh_token=tokens.get('refresh_token'),
            token_expiry=token_expiry,
            additional_data={
                'client_id': oauth_config.client_id,
                'client_secret': oauth_config.client_secret
            }
        )
        db.add(credential)
    
    db.commit()
    
    # Redirect back to frontend dashboard
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?google=connected")


# Slack OAuth
@router.get("/slack/url")
async def get_slack_auth_url(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Slack OAuth authorization URL using user's configured credentials"""
    
    # Get user's OAuth config
    oauth_config = db.query(OAuthConfigModel).filter(
        OAuthConfigModel.user_id == current_user.id,
        OAuthConfigModel.service_name == "slack"
    ).first()
    
    if not oauth_config or not oauth_config.is_configured:
        raise HTTPException(
            status_code=400,
            detail="Please configure your Slack OAuth credentials first"
        )
    
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
    
    redirect_uri = oauth_config.additional_config.get('redirect_uri', settings.SLACK_REDIRECT_URI) if oauth_config.additional_config else settings.SLACK_REDIRECT_URI
    
    auth_url = (
        f"https://slack.com/oauth/v2/authorize?"
        f"client_id={oauth_config.client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={','.join(scopes)}&"
        f"state={current_user.id}"
    )
    
    return {"url": auth_url}


@router.get("/slack/callback")
async def slack_oauth_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Slack OAuth callback using user's configured credentials"""
    
    user_id = int(state)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's OAuth config
    oauth_config = db.query(OAuthConfigModel).filter(
        OAuthConfigModel.user_id == user_id,
        OAuthConfigModel.service_name == "slack"
    ).first()
    
    if not oauth_config:
        raise HTTPException(status_code=400, detail="Slack OAuth not configured for this user")
    
    redirect_uri = oauth_config.additional_config.get('redirect_uri', settings.SLACK_REDIRECT_URI) if oauth_config.additional_config else settings.SLACK_REDIRECT_URI
    
    # Exchange code for tokens using user's credentials
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://slack.com/api/oauth.v2.access",
            data={
                "code": code,
                "client_id": oauth_config.client_id,
                "client_secret": oauth_config.client_secret,
                "redirect_uri": redirect_uri
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
        
        data = response.json()
        
        if not data.get('ok'):
            raise HTTPException(status_code=400, detail="Slack OAuth failed")
    
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
    
    # Redirect back to frontend dashboard
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?slack=connected")


# Azure OpenAI Configuration  
@router.post("/azure/configure")
async def configure_azure_openai(
    config: OAuthConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Configure Azure OpenAI credentials"""
    
    # Store in oauth_configs table
    oauth_config = db.query(OAuthConfigModel).filter(
        OAuthConfigModel.user_id == current_user.id,
        OAuthConfigModel.service_name == "azure_openai"
    ).first()
    
    if oauth_config:
        oauth_config.client_id = config.additional_config.get('endpoint', '')  # Store endpoint as client_id
        oauth_config.client_secret = config.client_secret  # API key
        oauth_config.additional_config = config.additional_config
        oauth_config.is_configured = True
        oauth_config.updated_at = datetime.utcnow()
    else:
        oauth_config = OAuthConfigModel(
            user_id=current_user.id,
            service_name="azure_openai",
            client_id=config.additional_config.get('endpoint', ''),
            client_secret=config.client_secret,
            additional_config=config.additional_config,
            is_configured=True
        )
        db.add(oauth_config)
    
    db.commit()
    
    return {"message": "Azure OpenAI configured successfully"}


@router.get("/status")
async def get_auth_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get authentication status for all services"""
    
    credentials = db.query(Credential).filter(Credential.user_id == current_user.id).all()
    oauth_configs = db.query(OAuthConfigModel).filter(OAuthConfigModel.user_id == current_user.id).all()
    
    status = {
        'google': {
            'configured': False,
            'connected': False
        },
        'slack': {
            'configured': False,
            'connected': False
        },
        'azure_openai': {
            'configured': False,
            'connected': False
        }
    }
    
    # Check OAuth configs
    for config in oauth_configs:
        if config.service_name in status:
            status[config.service_name]['configured'] = config.is_configured
    
    # Check credentials (tokens)
    for cred in credentials:
        if cred.service_name in status:
            status[cred.service_name]['connected'] = True
    
    return status
