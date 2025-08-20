from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_session
from dependencies import get_current_user_id
from patient import Patient
from schemas import PatientCreate, CreateResponse, PatientRead


router = APIRouter()


@router.get("", response_model=list[PatientRead])
async def list_patients(
    q: Optional[str] = Query(None, description="Search by name or phone"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    stmt = select(Patient)
    if q:
        like = f"%{q}%"
        stmt = stmt.where((Patient.first_name.ilike(like)) | (Patient.last_name.ilike(like)) | (Patient.phone.ilike(like)))
    stmt = stmt.order_by(Patient.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    return (await db.execute(stmt)).scalars().all()


@router.post("", response_model=CreateResponse)
async def create_patient(
    payload: PatientCreate,
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    patient = Patient(
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        age=payload.age,
        gender=payload.gender,
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return {"id": patient.id}
