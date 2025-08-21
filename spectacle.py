from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from database import Base


class Spectacle(Base):
    __tablename__ = "spectacles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    brand = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    image_url = Column(String(500))
    frame_material = Column(String(100))
    frame_shape = Column(String(50))
    lens_type = Column(String(50))
    gender = Column(String(20))
    age_group = Column(String(50))
    description = Column(Text)
    specifications = Column(JSON)
    quantity = Column(Integer, default=0)
    in_stock = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
