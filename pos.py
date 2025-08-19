from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func, Integer, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class LoyaltyAccount(Base):
    __tablename__ = "loyalty_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(index=True)
    points: Mapped[int] = mapped_column(Integer, default=0)


class PosOrder(Base):
    __tablename__ = "pos_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[Optional[int]] = mapped_column(index=True)
    order_no: Mapped[str] = mapped_column(String(32), index=True)
    subtotal: Mapped[float] = mapped_column(Numeric(10,2), default=0)
    gst_amount: Mapped[float] = mapped_column(Numeric(10,2), default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(10,2), default=0)
    total: Mapped[float] = mapped_column(Numeric(10,2), default=0)
    paid_amount: Mapped[float] = mapped_column(Numeric(10,2), default=0)
    loyalty_points_earned: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class PosOrderLine(Base):
    __tablename__ = "pos_order_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("pos_orders.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(index=True)
    batch_id: Mapped[Optional[int]] = mapped_column(index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Numeric(10,2))
    gst_rate: Mapped[float] = mapped_column(Numeric(5,2), default=0)
    discount_rate: Mapped[float] = mapped_column(Numeric(5,2), default=0)


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("pos_orders.id", ondelete="CASCADE"), index=True)
    method: Mapped[str] = mapped_column(String(32), index=True)  # cash, card, upi
    amount: Mapped[float] = mapped_column(Numeric(10,2))
    reference: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


