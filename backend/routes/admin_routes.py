from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from database import get_db
from models import User, ActivityLog, CostTracking
from schemas import (
    UserResponse,
    ActivityLogResponse,
    CostTrackingResponse,
    UserStats,
    UserCreate
)
from auth import get_current_admin_user, get_password_hash

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query(User).all()
    return users


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        is_admin=user_data.is_admin
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)"""
    
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}


@router.patch("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Toggle user active status (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = not user.is_active
    db.commit()
    
    return {"message": f"User {'activated' if user.is_active else 'deactivated'} successfully"}


@router.get("/logs", response_model=List[ActivityLogResponse])
async def get_activity_logs(
    user_id: int = None,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get activity logs (admin only)"""
    
    query = db.query(ActivityLog)
    
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    
    logs = query.order_by(ActivityLog.timestamp.desc()).limit(limit).all()
    return logs


@router.get("/costs", response_model=List[CostTrackingResponse])
async def get_cost_tracking(
    user_id: int = None,
    days: int = 30,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get cost tracking data (admin only)"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(CostTracking).filter(CostTracking.timestamp >= start_date)
    
    if user_id:
        query = query.filter(CostTracking.user_id == user_id)
    
    costs = query.order_by(CostTracking.timestamp.desc()).all()
    return costs


@router.get("/stats/user/{user_id}", response_model=UserStats)
async def get_user_stats(
    user_id: int,
    days: int = 30,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get user statistics (admin only)"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total operations
    total_ops = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.user_id == user_id,
        ActivityLog.timestamp >= start_date
    ).scalar()
    
    # Total cost
    total_cost = db.query(func.sum(CostTracking.estimated_cost)).filter(
        CostTracking.user_id == user_id,
        CostTracking.timestamp >= start_date
    ).scalar() or 0.0
    
    # Operations by type
    ops_by_type = db.query(
        ActivityLog.action,
        func.count(ActivityLog.id)
    ).filter(
        ActivityLog.user_id == user_id,
        ActivityLog.timestamp >= start_date
    ).group_by(ActivityLog.action).all()
    
    ops_dict = {action: count for action, count in ops_by_type}
    
    return UserStats(
        total_operations=total_ops,
        total_cost=total_cost,
        operations_by_type=ops_dict
    )


@router.get("/stats/overall")
async def get_overall_stats(
    days: int = 30,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get overall system statistics (admin only)"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    
    total_ops = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.timestamp >= start_date
    ).scalar()
    
    total_cost = db.query(func.sum(CostTracking.estimated_cost)).filter(
        CostTracking.timestamp >= start_date
    ).scalar() or 0.0
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_operations": total_ops,
        "total_cost": total_cost,
        "period_days": days
    }
