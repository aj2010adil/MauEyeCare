from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db, get_current_user_id
from visit import Visit
from schemas import VisitCreate


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
    payload: VisitCreate,
    db: AsyncSession = Depends(get_db),
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


