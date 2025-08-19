from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db, get_current_user_id
from schemas import ConsentCreate
from consent import Consent


router = APIRouter()


@router.post("", response_model=dict)
async def create_consent(payload: ConsentCreate, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    c = Consent(patient_id=payload.patient_id, visit_id=payload.visit_id, type=payload.type, content=payload.content, signed_by=payload.signed_by)
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return {"id": c.id}


@router.get("/patient/{patient_id}", response_model=list[dict])
async def list_consents(patient_id: int, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    rows = (await db.execute(select(Consent).where(Consent.patient_id == patient_id).order_by(Consent.signed_at.desc()))).scalars().all()
    return [{"id": c.id, "type": c.type, "signed_by": c.signed_by, "signed_at": c.signed_at.isoformat()} for c in rows]


