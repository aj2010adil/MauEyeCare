from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, DateTime, func, Boolean, Enum, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column
import enum

from database import Base


class ProductCategory(str, enum.Enum):
    frame = "frame"
    lens = "lens"
    coating = "coating"
    contact_lens = "contact_lens"
    medicine = "medicine"
    service = "service"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    category: Mapped[str] = mapped_column(String(32), index=True)
    hsn_sac: Mapped[Optional[str]] = mapped_column(String(16))
    brand: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    color: Mapped[Optional[str]] = mapped_column(String(50))
    eye_size: Mapped[Optional[str]] = mapped_column(String(16))
    gst_rate: Mapped[float] = mapped_column(Numeric(5,2), default=0)
    mrp: Mapped[float] = mapped_column(Numeric(10,2), default=0)
    price: Mapped[float] = mapped_column(Numeric(10,2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    schedule_h: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        Index("ix_products_cat_brand", "category", "brand"),
    )


