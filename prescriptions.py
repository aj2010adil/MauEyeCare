from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from dependencies import get_db, get_current_user_id
from patient import Patient
from visit import Visit
from prescription import Prescription


router = APIRouter()


def _ensure_prescription_dir(now: datetime) -> str:
    year_dir = os.path.join(settings.prescription_root, str(now.year))
    day_dir = os.path.join(year_dir, now.strftime("%m-%d"))
    os.makedirs(day_dir, exist_ok=True)
    return day_dir


@router.get("/patient/{patient_id}", response_model=list[dict])
async def list_patient_prescriptions(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    stmt = select(Prescription).where(Prescription.patient_id == patient_id).order_by(Prescription.created_at.desc())
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": p.id,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "pdf_path": p.pdf_path,
            "rx_values": p.rx_values,
            "spectacles": p.spectacles,
            "medicines": p.medicines,
            "totals": p.totals,
            "visit_id": p.visit_id,
        }
        for p in rows
    ]


@router.post("", response_model=dict)
async def create_prescription(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    patient_id = payload.get("patient_id")
    visit_id = payload.get("visit_id")
    if not patient_id:
        raise HTTPException(status_code=422, detail="patient_id is required")

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

    from pdf_generator import render_prescription_pdf

    pdf_bytes = await render_prescription_pdf(
        patient_id=patient_id,
        visit_id=visit_id,
        rx_values=payload.get("rx_values"),
        spectacles=payload.get("spectacles"),
        medicines=payload.get("medicines"),
        totals=payload.get("totals"),
    )
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    pres = Prescription(
        patient_id=patient_id,
        visit_id=visit_id,
        pdf_path=file_path,
        rx_values=payload.get("rx_values"),
        spectacles=payload.get("spectacles"),
        medicines=payload.get("medicines"),
        totals=payload.get("totals"),
    )
    db.add(pres)
    await db.commit()
    await db.refresh(pres)
    return {"id": pres.id, "pdf_path": pres.pdf_path}


