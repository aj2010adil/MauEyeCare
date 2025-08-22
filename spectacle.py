from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, func, Boolean, JSON, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Spectacle(Base):
    __tablename__ = "spectacles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    frame_material: Mapped[Optional[str]] = mapped_column(String(100))
    frame_shape: Mapped[Optional[str]] = mapped_column(String(50))
    lens_type: Mapped[Optional[str]] = mapped_column(String(50))
    gender: Mapped[Optional[str]] = mapped_column(String(20))
    age_group: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    specifications: Mapped[Optional[dict]] = mapped_column(JSON)
    quantity: Mapped[int] = mapped_column(default=0)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())