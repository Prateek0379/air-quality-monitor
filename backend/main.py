# =============================================================
# main.py
#
# PURPOSE: Define all API endpoints for the air quality system.
#
# This is the heart of our backend. FastAPI reads these
# functions and automatically:
# - Routes HTTP requests to the right function
# - Validates request data using our schemas
# - Generates interactive docs at /docs
# - Returns proper error messages for invalid data
# =============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from database.database import get_db
from database.models import SensorReading
from backend.schemas import (
    SensorReadingCreate,
    SensorReadingResponse,
    StatsResponse
)
from data.sensor_simulator import generate_reading

# -------------------------------------------------------------
# CREATE THE FASTAPI APP
# title and description appear in the auto-generated docs
# -------------------------------------------------------------
app = FastAPI(
    title="Air Quality Monitoring API",
    description="REST API for air quality sensor data and anomaly detection",
    version="1.0.0"
)

# -------------------------------------------------------------
# CORS MIDDLEWARE
# CORS = Cross Origin Resource Sharing
# Without this, your React frontend (running on port 3000)
# cannot talk to your FastAPI backend (running on port 8000).
# The browser blocks it for security reasons.
# allow_origins=["*"] allows ALL origins — fine for development.
# In production, replace * with your actual frontend URL.
# -------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------
# HEALTH CHECK
# Always have a health check endpoint.
# Used by monitoring tools to verify the server is alive.
# -------------------------------------------------------------
@app.get("/")
def health_check():
    """Check if the API is running."""
    return {
        "status": "online",
        "message": "Air Quality Monitoring API is running",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# -------------------------------------------------------------
# GET RECENT READINGS
# Returns the most recent n readings, newest first.
# limit parameter lets the caller control how many they get.
# -------------------------------------------------------------
@app.get("/readings", response_model=List[SensorReadingResponse])
def get_readings(
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get recent sensor readings.

    - **limit**: Number of readings to return (1-1000, default 100)
    """
    readings = (
        db.query(SensorReading)
        .order_by(SensorReading.timestamp.desc())
        .limit(limit)
        .all()
    )
    return readings


# -------------------------------------------------------------
# GET LATEST SINGLE READING
# Used by the dashboard to show current conditions
# -------------------------------------------------------------
@app.get("/readings/latest", response_model=SensorReadingResponse)
def get_latest_reading(db: Session = Depends(get_db)):
    """Get the single most recent sensor reading."""
    reading = (
        db.query(SensorReading)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    if not reading:
        raise HTTPException(
            status_code=404,
            detail="No readings found in database"
        )
    return reading


# -------------------------------------------------------------
# GET ANOMALIES ONLY
# Used by the dashboard to highlight dangerous events
# -------------------------------------------------------------
@app.get("/readings/anomalies", response_model=List[SensorReadingResponse])
def get_anomalies(
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get readings flagged as anomalies."""
    anomalies = (
        db.query(SensorReading)
        .filter(SensorReading.is_anomaly == True)
        .order_by(SensorReading.timestamp.desc())
        .limit(limit)
        .all()
    )
    return anomalies


# -------------------------------------------------------------
# POST NEW READING
# Accepts a new sensor reading and stores it.
# In production this will be called by the sensor stream.
# Currently useful for testing and manual data entry.
# -------------------------------------------------------------
@app.post("/readings", response_model=SensorReadingResponse)
def create_reading(
    reading: SensorReadingCreate,
    db: Session = Depends(get_db)
):
    """
    Submit a new sensor reading.

    # -------------------------------------------------------
    # REPLACEMENT POINT
    # Later this endpoint will be called automatically
    # by the sensor simulator on a timer, or by an
    # MQTT listener receiving real ESP32 data.
    # -------------------------------------------------------
    """
    db_reading = SensorReading(**reading.model_dump())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading


# -------------------------------------------------------------
# SIMULATE NEW READING
# Convenience endpoint — generates and stores one new reading.
# Used during development to add fresh data without a sensor.
# -------------------------------------------------------------
@app.post("/readings/simulate", response_model=SensorReadingResponse)
def simulate_reading(db: Session = Depends(get_db)):
    """Generate and store one new simulated sensor reading."""
    data = generate_reading()

    db_reading = SensorReading(
        timestamp=datetime.now(),
        pm25=data["pm25"],
        pm10=data["pm10"],
        co2=data["co2"],
        temperature=data["temperature"],
        humidity=data["humidity"],
        aqi=data["aqi"],
        aqi_category=data["aqi_category"],
        is_anomaly=data["is_anomaly"],
    )
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading


# -------------------------------------------------------------
# GET STATISTICS
# Summary stats for the dashboard header cards
# -------------------------------------------------------------
@app.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Get summary statistics for the dashboard."""

    # Query aggregations directly in the database
    # Much faster than loading all rows into Python
    stats = db.query(
        func.count(SensorReading.id).label("total"),
        func.avg(SensorReading.aqi).label("avg_aqi"),
        func.avg(SensorReading.pm25).label("avg_pm25"),
        func.avg(SensorReading.co2).label("avg_co2"),
        func.avg(SensorReading.temperature).label("avg_temp"),
        func.avg(SensorReading.humidity).label("avg_humidity"),
    ).first()

    anomaly_count = (
        db.query(SensorReading)
        .filter(SensorReading.is_anomaly == True)
        .count()
    )

    latest = (
        db.query(SensorReading)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )

    return StatsResponse(
        total_readings=stats.total or 0,
        anomaly_count=anomaly_count,
        avg_aqi=round(stats.avg_aqi or 0, 1),
        avg_pm25=round(stats.avg_pm25 or 0, 1),
        avg_co2=round(stats.avg_co2 or 0, 1),
        avg_temperature=round(stats.avg_temp or 0, 1),
        avg_humidity=round(stats.avg_humidity or 0, 1),
        latest_aqi=latest.aqi if latest else 0,
        latest_category=latest.aqi_category if latest else "Unknown"
    )