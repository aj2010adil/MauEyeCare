from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db, get_current_user_id
from visit import Visit


router = APIRouter()


@router.get("/patient/{patient_id}", response_model=list[dict])
async def list_patient_visits(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    stmt = select(Visit).where(Visit.patient_id == patient_id).order_by(Visit.visit_date.desc())
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": v.id,
            "patient_id": v.patient_id,
            "visit_date": v.visit_date.isoformat(),
            "issue": v.issue,
            "advice": v.advice,
            "metrics": v.metrics,
        }
        for v in rows
    ]


@router.post("", response_model=dict)
async def create_visit(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    patient_id = payload.get("patient_id")
    if not patient_id:
        raise HTTPException(status_code=422, detail="patient_id is required")
    visit = Visit(
        patient_id=patient_id,
        issue=(payload.get("issue") or None),
        advice=(payload.get("advice") or None),
        metrics=payload.get("metrics"),
    )
    db.add(visit)
    await db.commit()
    await db.refresh(visit)
    return {"id": visit.id}


