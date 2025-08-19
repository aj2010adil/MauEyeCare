from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db, get_current_user_id
from patient import Patient


router = APIRouter()


@router.get("", response_model=list[dict])
async def list_patients(
    q: Optional[str] = Query(None, description="Search by name or phone"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    stmt = select(Patient)
    if q:
        like = f"%{q}%"
        stmt = stmt.where((Patient.first_name.ilike(like)) | (Patient.last_name.ilike(like)) | (Patient.phone.ilike(like)))
    stmt = stmt.order_by(Patient.created_at.desc()).limit(100)
    res = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": p.id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "phone": p.phone,
            "age": p.age,
            "gender": p.gender,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in res
    ]


@router.post("", response_model=dict)
async def create_patient(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    first_name = (payload.get("first_name") or "").strip()
    if not first_name:
        raise HTTPException(status_code=422, detail="first_name is required")
    patient = Patient(
        first_name=first_name,
        last_name=(payload.get("last_name") or "").strip() or None,
        phone=(payload.get("phone") or "").strip() or None,
        age=payload.get("age"),
        gender=(payload.get("gender") or None),
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return {"id": patient.id}


