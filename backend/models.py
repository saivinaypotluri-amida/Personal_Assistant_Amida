from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    credentials = relationship("Credential", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    costs = relationship("CostTracking", back_populates="user", cascade="all, delete-orphan")


class Credential(Base):
    __tablename__ = "credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_name = Column(String, nullable=False)  # 'google', 'slack', 'azure_openai'
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="credentials")


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # 'email_summary', 'schedule_meeting', etc.
    source = Column(String, nullable=False)  # 'portal', 'slack'
    status = Column(String, nullable=False)  # 'success', 'failed'
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="logs")


class CostTracking(Base):
    __tablename__ = "cost_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service = Column(String, nullable=False)  # 'azure_openai'
    operation = Column(String, nullable=False)  # 'email_summary', 'schedule_meeting'
    tokens_used = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="costs")
