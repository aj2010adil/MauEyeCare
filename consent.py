from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Consent(Base):
    __tablename__ = "consents"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(index=True)
    visit_id: Mapped[Optional[int]] = mapped_column(index=True)
    type: Mapped[str] = mapped_column(String(64))
    content: Mapped[dict] = mapped_column(JSON)
    signed_by: Mapped[str] = mapped_column(String(100))
    signed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


