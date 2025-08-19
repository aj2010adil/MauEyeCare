from __future__ import annotations

from typing import Optional, List, Dict
from pydantic import BaseModel, Field, constr


class PatientCreate(BaseModel):
    first_name: constr(strip_whitespace=True, min_length=1)
    last_name: Optional[constr(strip_whitespace=True)] = None
    phone: Optional[constr(strip_whitespace=True, min_length=5, max_length=32)] = None
    age: Optional[int] = Field(default=None, ge=0, le=120)
    gender: Optional[str] = Field(default=None, max_length=20)


class VisitCreate(BaseModel):
    patient_id: int
    issue: Optional[str] = None
    advice: Optional[str] = None
    metrics: Optional[Dict] = None


class PrescriptionCreate(BaseModel):
    patient_id: int
    visit_id: Optional[int] = None
    rx_values: Optional[Dict] = None
    spectacles: Optional[List] = None
    medicines: Optional[Dict] = None
    totals: Optional[Dict] = None


