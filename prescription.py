from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), index=True)
    visit_id: Mapped[Optional[int]] = mapped_column(ForeignKey("visits.id", ondelete="SET NULL"), index=True)
    pdf_path: Mapped[Optional[str]] = mapped_column(String(500))
    rx_values: Mapped[Optional[dict]] = mapped_column(JSON)
    spectacles: Mapped[Optional[list]] = mapped_column(JSON)
    medicines: Mapped[Optional[dict]] = mapped_column(JSON)
    totals: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    patient: Mapped["Patient"] = relationship()
    visit: Mapped[Optional["Visit"]] = relationship(back_populates="prescriptions")


