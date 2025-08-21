from __future__ import annotations

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from config import settings
from security import verify_password, hash_password, create_access_token, create_refresh_token, decode_refresh_token
from user import User
from dependencies import get_current_user

router = APIRouter()


@router.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db_session)):
    stmt = select(User).where(User.email == form_data.username, User.is_active == True)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


@router.post("/refresh", response_model=dict)
async def refresh_token(payload: dict):
    token = payload.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="refresh_token required")
    data = decode_refresh_token(token)
    sub = data.get("sub")
    access = create_access_token(str(sub))
    return {"access_token": access, "token_type": "bearer"}


@router.post("/bootstrap", response_model=dict)
async def bootstrap_admin(db: AsyncSession = Depends(get_db_session)):
    """Idempotent: ensure a default doctor account exists."""
    email = settings.bootstrap_admin_email
    stmt = select(User).where(User.email == email)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if user:
        return {"created": False, "message": "Default user already exists."}
    
    user = User(
        email=email,
        full_name="Default Doctor",
        role="doctor",
        password_hash=hash_password(settings.bootstrap_admin_password),
    )
    db.add(user)
    await db.commit()
    return {"created": True, "message": f"Default user '{email}' created."}


@router.get("/me", response_model=dict)
async def me(user: User = Depends(get_current_user)):
    """Return current authenticated user's profile."""
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
    }
