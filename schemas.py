from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, constr


class PatientCreate(BaseModel):
    first_name: constr(strip_whitespace=True, min_length=1)
    last_name: Optional[constr(strip_whitespace=True)] = None
    phone: Optional[constr(strip_whitespace=True, min_length=5, max_length=32)] = None
    age: Optional[int] = Field(default=None, ge=0, le=120)
    gender: Optional[str] = Field(default=None, max_length=20)


class CreateResponse(BaseModel):
    id: int


class PatientRead(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class VisitCreate(BaseModel):
    patient_id: int
    issue: Optional[str] = None
    advice: Optional[str] = None
    metrics: Optional[Dict] = None


class VisitRead(BaseModel):
    id: int
    patient_id: int
    visit_date: datetime
    issue: Optional[str] = None
    advice: Optional[str] = None
    metrics: Optional[Dict] = None

    model_config = {"from_attributes": True}


class PrescriptionCreate(BaseModel):
    patient_id: int
    visit_id: Optional[int] = None
    rx_values: Optional[Dict] = None
    spectacles: Optional[List] = None
    medicines: Optional[Dict] = None
    totals: Optional[Dict] = None


class PrescriptionRead(BaseModel):
    id: int
    created_at: Optional[datetime] = None
    pdf_path: Optional[str] = None
    rx_values: Optional[Dict] = None
    spectacles: Optional[List] = None
    medicines: Optional[Dict] = None
    totals: Optional[Dict] = None
    visit_id: Optional[int] = None

    model_config = {"from_attributes": True}


class PrescriptionCreateResponse(BaseModel):
    id: int
    pdf_path: Optional[str] = None


class PosCartLine(BaseModel):
    product_id: int
    batch_id: Optional[int] = None
    quantity: int
    price: float
    gst_rate: float = 0
    discount_rate: float = 0


class PosCheckout(BaseModel):
    patient_id: Optional[int] = None
    lines: list[PosCartLine]
    payments: list[Dict]  # {method, amount, reference?}
    discount_amount: float = 0


class LabJobCreate(BaseModel):
    order_id: Optional[int] = None
    patient_id: Optional[int] = None
    frame_measurements: Optional[Dict] = None
    seg_heights: Optional[Dict] = None
    supplier: Optional[str] = None
    technician: Optional[str] = None


class LabJobRead(BaseModel):
    id: int
    status: str
    patient_id: Optional[int] = None
    order_id: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConsentCreate(BaseModel):
    patient_id: int
    visit_id: Optional[int] = None
    type: str
    content: Dict
    signed_by: str


class ConsentRead(BaseModel):
    id: int
    type: str
    signed_by: str
    signed_at: datetime

    model_config = {"from_attributes": True}


# Dashboard Schemas
class StatsResponse(BaseModel):
    total_patients: int
    today_visits: int
    total_prescriptions: int


class TopIssue(BaseModel):
    issue: str
    count: int


class MarketingResponse(BaseModel):
    top_issues: list[TopIssue]


class TodayVisit(BaseModel):
    id: int
    patient_id: int
    time: datetime
    issue: Optional[str] = None
    advice: Optional[str] = None


class OperationsResponse(BaseModel):
    today: list[TodayVisit]


# POS Schemas
class CheckoutResponse(BaseModel):
    order_id: int
    total: float
    paid: float


# Insights Schemas
class SuggestionsResponse(BaseModel):
    suggestions: list[str]


# POS Summary for dashboard
class PosSummaryResponse(BaseModel):
    total_today: float
    orders_today: int