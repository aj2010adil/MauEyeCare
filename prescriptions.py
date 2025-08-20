from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse

from config import settings
from pdf_generator import render_prescription_pdf
from database import get_db_session
from dependencies import get_current_user_id
from patient import Patient
from visit import Visit
from prescription import Prescription
from schemas import PrescriptionCreate, PrescriptionRead, PrescriptionCreateResponse


router = APIRouter()


def _ensure_prescription_dir(now: datetime) -> str:
    year_dir = os.path.join(settings.prescription_root, str(now.year))
    day_dir = os.path.join(year_dir, now.strftime("%m-%d"))
    os.makedirs(day_dir, exist_ok=True)
    return day_dir


@router.get("/patient/{patient_id}", response_model=list[PrescriptionRead])
async def list_patient_prescriptions(
    patient_id: int,
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    stmt = select(Prescription).where(Prescription.patient_id == patient_id).order_by(Prescription.created_at.desc())
    return (await db.execute(stmt)).scalars().all()


@router.post("", response_model=PrescriptionCreateResponse)
async def create_prescription(
    payload: PrescriptionCreate,
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    patient_id = payload.patient_id
    visit_id = payload.visit_id
    # Validate patient/visit existence
    if visit_id:
        v = await db.get(Visit, visit_id)
        if not v or v.patient_id != patient_id:
            raise HTTPException(status_code=404, detail="Visit not found")

    # Build PDF contents and write file
    now = datetime.now()
    file_dir = _ensure_prescription_dir(now)
    file_name = f"RX_{now.strftime('%Y%m%d_%H%M%S')}_{patient_id}.pdf"
    file_path = os.path.join(file_dir, file_name)

    pdf_bytes = await render_prescription_pdf(
        patient_id=patient_id,
        visit_id=visit_id,
        rx_values=payload.rx_values,
        spectacles=payload.spectacles,
        medicines=payload.medicines,
        totals=payload.totals,
    )
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    pres = Prescription(
        patient_id=patient_id,
        visit_id=visit_id,
        pdf_path=file_path,
        rx_values=payload.rx_values,
        spectacles=payload.spectacles,
        medicines=payload.medicines,
        totals=payload.totals,
    )
    db.add(pres)
    await db.commit()
    await db.refresh(pres)
    return pres


@router.get("/{prescription_id}/pdf")
async def get_prescription_pdf(prescription_id: int, db: AsyncSession = Depends(get_db_session), user_id: str = Depends(get_current_user_id)):
    pres = await db.get(Prescription, prescription_id)
    if not pres or not pres.pdf_path:
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(path=pres.pdf_path, media_type="application/pdf", filename=os.path.basename(pres.pdf_path))
