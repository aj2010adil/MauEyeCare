from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, func, Boolean, JSON, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(100))
    category: Mapped[Optional[str]] = mapped_column(String(100))
    dosage: Mapped[Optional[str]] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    specifications: Mapped[Optional[dict]] = mapped_column(JSON)
    quantity: Mapped[int] = mapped_column(default=0)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    prescription_required: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())