from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), index=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    gender: Mapped[Optional[str]] = mapped_column(String(20))
    age: Mapped[Optional[int]]
    phone: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    visits: Mapped[list["Visit"]] = relationship(back_populates="patient", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_patients_phone", "phone"),
        Index("ix_patients_name", "first_name", "last_name"),
    )


