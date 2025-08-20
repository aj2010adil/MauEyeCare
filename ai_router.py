from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from database import get_db_session
from dependencies import get_current_user_id
from modules.ai_doctor_tools import analyze_symptoms_ai, suggest_medications_ai, analyze_prescription_interactions, generate_patient_education_ai


router = APIRouter()


class NotesPayload(BaseModel):
    symptoms: str
    age: Optional[int] = None
    gender: Optional[str] = None
    medical_history: Optional[str] = None


@router.post('/notes/interpret', response_model=dict)
async def interpret_notes(payload: NotesPayload, db: AsyncSession = Depends(get_db_session), user_id: str = Depends(get_current_user_id)):
    text = analyze_symptoms_ai(payload.symptoms, payload.age or '', payload.gender or '', payload.medical_history or '')
    return {"analysis": text}


class RxSuggestPayload(BaseModel):
    diagnosis: str
    age: Optional[int] = None
    allergies: Optional[str] = None


@router.post('/prescriptions/suggest', response_model=dict)
async def suggest_rx(payload: RxSuggestPayload, db: AsyncSession = Depends(get_db_session), user_id: str = Depends(get_current_user_id)):
    text = suggest_medications_ai(payload.diagnosis, payload.age or '', payload.allergies or '')
    return {"suggestion": text}


class InteractionPayload(BaseModel):
    medications: List[str]


@router.post('/prescriptions/interactions', response_model=dict)
async def check_interactions(payload: InteractionPayload, db: AsyncSession = Depends(get_db_session), user_id: str = Depends(get_current_user_id)):
    text = analyze_prescription_interactions(payload.medications)
    return {"interactions": text}


class EducationPayload(BaseModel):
    condition: str
    treatment: str


@router.post('/education', response_model=dict)
async def patient_education(payload: EducationPayload, db: AsyncSession = Depends(get_db_session), user_id: str = Depends(get_current_user_id)):
    text = generate_patient_education_ai(payload.condition, payload.treatment)
    return {"education": text}


