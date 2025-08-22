from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO
import qrcode
import base64
from database import get_db_session
from dependencies import get_current_user_id
from patient import Patient
from config import settings
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


@router.get("/{patient_id}/verify", response_model=dict)
async def verify_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    p = await db.get(Patient, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    last_initial = (p.last_name[0] + ".") if p.last_name else ""
    phone_masked = None
    if p.phone:
        ph = ''.join([c for c in p.phone if c.isdigit()])
        phone_masked = f"***-***-{ph[-4:]}" if len(ph) >= 4 else "***"
    return {
        "id": p.id,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "first_name": p.first_name,
        "last_initial": last_initial,
        "phone_masked": phone_masked,
    }


@router.get("/{patient_id}/qr")
async def get_patient_qr(
    patient_id: int,
    size: int = 200,
    foreground_color: str = "#000000",
    background_color: str = "#FFFFFF",
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    p = await db.get(Patient, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    url = f"http://localhost:5173/patient?id={patient_id}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=foreground_color, back_color=background_color)
    buf = BytesIO(); img.save(buf, format='PNG'); img_str = base64.b64encode(buf.getvalue()).decode()
    return {"qr_code": f"data:image/png;base64,{img_str}", "url": url, "patient_id": patient_id}


@router.get("/{patient_id}/qr.png")
async def get_patient_qr_image(
    patient_id: int,
    size: int = 200,
    foreground_color: str = "#000000",
    background_color: str = "#FFFFFF",
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    p = await db.get(Patient, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    url = f"http://localhost:5173/patient?id={patient_id}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=foreground_color, back_color=background_color)
    buf = BytesIO(); img.save(buf, format='PNG'); buf.seek(0)
    return StreamingResponse(buf, media_type='image/png')
