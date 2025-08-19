from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func, Integer, JSON, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column
import enum

from database import Base


class LabJobStatus(str, enum.Enum):
    created = "created"
    sent_to_lab = "sent_to_lab"
    in_process = "in_process"
    ready = "ready"
    delivered = "delivered"
    remake = "remake"


class LabJob(Base):
    __tablename__ = "lab_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[Optional[int]] = mapped_column(index=True)
    patient_id: Mapped[Optional[int]] = mapped_column(index=True)
    frame_measurements: Mapped[Optional[dict]] = mapped_column(JSON)
    seg_heights: Mapped[Optional[dict]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32), default=LabJobStatus.created.value, index=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    supplier: Mapped[Optional[str]] = mapped_column(String(100))
    technician: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class LabRemake(Base):
    __tablename__ = "lab_remakes"

    id: Mapped[int] = mapped_column(primary_key=True)
    lab_job_id: Mapped[int] = mapped_column(ForeignKey("lab_jobs.id", ondelete="CASCADE"), index=True)
    reason: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


