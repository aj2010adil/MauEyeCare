from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_session
from dependencies import get_current_user_id
from visit import Visit
from schemas import VisitCreate, VisitRead, CreateResponse


router = APIRouter()


@router.get("/patient/{patient_id}", response_model=list[VisitRead])
async def list_patient_visits(
    patient_id: int,
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    stmt = select(Visit).where(Visit.patient_id == patient_id).order_by(Visit.visit_date.desc())
    rows = (await db.execute(stmt)).scalars().all()
    return rows


@router.post("", response_model=CreateResponse)
async def create_visit(
    payload: VisitCreate,
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    visit = Visit(
        patient_id=payload.patient_id,
        issue=payload.issue,
        advice=payload.advice,
        metrics=payload.metrics,
    )
    db.add(visit)
    await db.commit()
    await db.refresh(visit)
    return {"id": visit.id}
