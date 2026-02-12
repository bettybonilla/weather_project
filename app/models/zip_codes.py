from sqlalchemy import Column, Integer, String, Float, DateTime, Text, func

from app.models.base import Base


class ZipCode(Base):
    __tablename__ = "zip_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    zip_code = Column(Text, nullable=False, unique=True)
    latitude = Column(Float(5), nullable=False)
    longitude = Column(Float(5), nullable=False)
    country_code = Column(String(2), nullable=False)
    state = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
