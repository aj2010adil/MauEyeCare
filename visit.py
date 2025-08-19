from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), index=True)
    visit_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    issue: Mapped[Optional[str]] = mapped_column(String(255))
    advice: Mapped[Optional[str]] = mapped_column(String(255))
    metrics: Mapped[Optional[dict]] = mapped_column(JSON)

    patient: Mapped["Patient"] = relationship(back_populates="visits")
    prescriptions: Mapped[list["Prescription"]] = relationship(back_populates="visit", cascade="all, delete-orphan")


