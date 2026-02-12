from sqlalchemy import Column, Integer, Date, UniqueConstraint, Text, func

from app.models.base import Base


class HourlyWeatherAggregate(Base):
    __tablename__ = "hourly_weather_aggregates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    zip_code = Column(Text, nullable=False)
    date = Column(Date, nullable=False)
    hour = Column(Integer, nullable=False)
    avg_temp = Column(Integer, nullable=False)
    avg_rain_prob = Column(Integer, nullable=False)
    created_at = Column(Date, nullable=False, server_default=func.now())
    updated_at = Column(Date, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('zip_code', 'date', 'hour', name='unique_zip_date_hour'),
    )
