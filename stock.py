from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, String, func, Integer, Numeric, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class StockBatch(Base):
    __tablename__ = "stock_batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    batch_no: Mapped[str] = mapped_column(String(64), index=True)
    expiry_date: Mapped[Optional[date]]
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    cost_price: Mapped[float] = mapped_column(Numeric(10,2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_schedule_h: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    __table_args__ = (
        Index("ix_stock_expiry", "expiry_date"),
    )


class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"

    id: Mapped[int] = mapped_column(primary_key=True)
    vendor_name: Mapped[str] = mapped_column(String(255))
    invoice_no: Mapped[Optional[str]] = mapped_column(String(64))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class GoodsReceiptLine(Base):
    __tablename__ = "goods_receipt_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    goods_receipt_id: Mapped[int] = mapped_column(ForeignKey("goods_receipts.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), index=True)
    batch_no: Mapped[str] = mapped_column(String(64))
    expiry_date: Mapped[Optional[date]]
    quantity: Mapped[int] = mapped_column(Integer)
    cost_price: Mapped[float] = mapped_column(Numeric(10,2))


