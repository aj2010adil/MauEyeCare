from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_session
from dependencies import get_current_user_id
from schemas import LabJobCreate, CreateResponse
from lab import LabJob, LabJobStatus, LabRemake


router = APIRouter()


@router.post("/jobs", response_model=dict)
@router.post("/jobs", response_model=CreateResponse)
async def create_job(payload: LabJobCreate, db: AsyncSession = Depends(get_db_session), user_id: str = Depends(get_current_user_id)):
    job = LabJob(order_id=payload.order_id, patient_id=payload.patient_id, frame_measurements=payload.frame_measurements, seg_heights=payload.seg_heights, supplier=payload.supplier, technician=payload.technician)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return {"id": job.id}


@router.get("/jobs", response_model=list[dict])
async def list_jobs(db: AsyncSession = Depends(get_db_session), user_id: str = Depends(get_current_user_id)):
    rows = (await db.execute(select(LabJob).order_by(LabJob.created_at.desc()).limit(200))).scalars().all()
    return [{"id": j.id, "status": j.status, "patient_id": j.patient_id, "order_id": j.order_id, "created_at": j.created_at.isoformat()} for j in rows]
