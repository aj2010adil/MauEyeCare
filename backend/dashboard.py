from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_session
from dependencies import get_current_user_id
from patient import Patient
from visit import Visit
from prescription import Prescription
from schemas import StatsResponse, MarketingResponse, OperationsResponse, PosSummaryResponse
from pos import PosOrder


router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
async def stats(db: AsyncSession = Depends(get_db_session), user_id: str = Depends(get_current_user_id)):
    today = datetime.utcnow().date()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())

    total_patients = (await db.execute(select(func.count()).select_from(Patient))).scalar() or 0
    today_visits = (
        (await db.execute(select(func.count()).select_from(Visit).where(Visit.visit_date >= start, Visit.visit_date <= end))).scalar()
        or 0
    )
    total_prescriptions = (await db.execute(select(func.count()).select_from(Prescription))).scalar() or 0

    return {
        "total_patients": total_patients,
        "today_visits": today_visits,
        "total_prescriptions": total_prescriptions,
    }


@router.get("/marketing", response_model=MarketingResponse)
async def marketing(db: AsyncSession = Depends(get_db_session), user_id: str = Depends(get_current_user_id)):
    rows = (await db.execute(select(Visit.issue, func.count().label("count")).group_by(Visit.issue))).all()
    issues = [{"issue": i or "", "count": int(c)} for i, c in rows if i]
    return {"top_issues": sorted(issues, key=lambda x: x["count"], reverse=True)[:10]}


@router.get("/operations", response_model=OperationsResponse)
async def operations(db: AsyncSession = Depends(get_db_session), user_id: str = Depends(get_current_user_id)):
    today = datetime.utcnow().date()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    rows = (
        (await db.execute(select(Visit).where(Visit.visit_date >= start, Visit.visit_date <= end).order_by(Visit.visit_date.desc())))
        .scalars()
        .all()
    )
    return {
        "today": [
            {
                "id": v.id,
                "patient_id": v.patient_id,
                "time": v.visit_date,
                "issue": v.issue,
                "advice": v.advice,
            }
            for v in rows
        ]
    }


@router.get("/pos-summary", response_model=PosSummaryResponse)
async def pos_summary(db: AsyncSession = Depends(get_db_session), user_id: str = Depends(get_current_user_id)):
    today = datetime.utcnow().date()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    rows = (await db.execute(select(PosOrder).where(PosOrder.created_at >= start, PosOrder.created_at <= end))).scalars().all()
    total = float(sum([float(getattr(x, "total", 0) or 0) for x in rows]))
    return {"total_today": total, "orders_today": len(rows)}
