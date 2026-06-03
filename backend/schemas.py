# =============================================================
# schemas.py
#
# PURPOSE: Define the shape of data coming IN and going OUT
#          of our API using Pydantic models.
#
# Think of schemas as a contract:
# - "I promise every reading I return will have these fields"
# - "I promise every reading submitted to me will have these fields"
#
# FastAPI uses these to:
# 1. Automatically validate incoming data
# 2. Automatically generate API documentation
# 3. Serialize Python objects to JSON
# =============================================================

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SensorReadingBase(BaseModel):
    """
    Base schema — fields shared by create and response schemas.
    We never use this directly, it's a parent class.
    """
    pm25:         float = Field(..., ge=0, description="PM2.5 in µg/m³")
    pm10:         float = Field(..., ge=0, description="PM10 in µg/m³")
    co2:          float = Field(..., ge=0, description="CO₂ in ppm")
    temperature:  float = Field(..., description="Temperature in °C")
    humidity:     float = Field(..., ge=0, le=100, description="Humidity %")
    aqi:          int   = Field(..., ge=0, description="Air Quality Index")
    aqi_category: str   = Field(..., description="AQI category label")
    is_anomaly:   bool  = Field(default=False)


class SensorReadingCreate(SensorReadingBase):
    """
    Schema for CREATING a new reading (POST request).
    Inherits all fields from SensorReadingBase.
    No id or timestamp — database assigns those automatically.
    """
    pass


class SensorReadingResponse(SensorReadingBase):
    """
    Schema for RETURNING a reading (GET response).
    Includes id and timestamp which the database assigns.
    """
    id:            int
    timestamp:     datetime
    anomaly_score: Optional[float] = None

    class Config:
        # This tells Pydantic to work with SQLAlchemy objects
        # Without this, it only works with plain dictionaries
        from_attributes = True


class StatsResponse(BaseModel):
    """
    Schema for the /stats endpoint.
    Returns summary statistics about recent readings.
    """
    total_readings:   int
    anomaly_count:    int
    avg_aqi:          float
    avg_pm25:         float
    avg_co2:          float
    avg_temperature:  float
    avg_humidity:     float
    latest_aqi:       int
    latest_category:  str