from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from database import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    brand = Column(String(100))
    category = Column(String(100))
    dosage = Column(String(100))
    price = Column(Float, nullable=False)
    image_url = Column(String(500))
    description = Column(Text)
    specifications = Column(JSON)
    quantity = Column(Integer, default=0)
    in_stock = Column(Boolean, default=True)
    prescription_required = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
