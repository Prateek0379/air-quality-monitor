# =============================================================
# models.py
#
# PURPOSE: Define the database tables using Python classes.
#
# SQLAlchemy lets us define tables as Python classes.
# Each class = one table. Each attribute = one column.
# This is called an ORM (Object Relational Mapper).
#
# ORM means: instead of writing SQL like
#   INSERT INTO sensor_readings (pm25, pm10) VALUES (47, 82)
# we write Python like:
#   reading = SensorReading(pm25=47, pm10=82)
#   db.add(reading)
# =============================================================

from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime
from sqlalchemy.sql import func
from database.database import Base


class SensorReading(Base):
    """
    Represents one sensor reading stored in the database.

    Each row in this table = one reading from our simulator
    (or later, from a real sensor).

    Table name: sensor_readings
    """

    __tablename__ = "sensor_readings"

    # -------------------------------------------------------------
    # PRIMARY KEY
    # Every table needs a unique identifier for each row.
    # index=True makes lookups by ID faster.
    # -------------------------------------------------------------
    id = Column(Integer, primary_key=True, index=True)

    # -------------------------------------------------------------
    # TIMESTAMP
    # When was this reading taken?
    # server_default=func.now() auto-fills with current time
    # if we forget to provide it.
    # -------------------------------------------------------------
    timestamp = Column(DateTime, server_default=func.now(), index=True)

    # -------------------------------------------------------------
    # SENSOR READINGS
    # nullable=False means this column MUST have a value.
    # We never want a reading with missing sensor data.
    # -------------------------------------------------------------
    pm25        = Column(Float, nullable=False)
    pm10        = Column(Float, nullable=False)
    co2         = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity    = Column(Float, nullable=False)

    # -------------------------------------------------------------
    # DERIVED VALUES
    # Calculated from sensor readings, stored for fast querying.
    # We could recalculate these every time, but storing them
    # means the dashboard loads faster.
    # -------------------------------------------------------------
    aqi          = Column(Integer, nullable=False)
    aqi_category = Column(String, nullable=False)

    # -------------------------------------------------------------
    # ANOMALY FLAG
    # Was this reading flagged as an anomaly?
    # During training: set by our simulator (ground truth)
    # In production: set by our ML model's prediction
    # -------------------------------------------------------------
    is_anomaly = Column(Boolean, default=False)

    # -------------------------------------------------------------
    # ML ANOMALY SCORE
    # The raw score from Isolation Forest.
    # Negative = more anomalous, positive = more normal.
    # Null until the ML model processes this reading.
    # -------------------------------------------------------------
    anomaly_score = Column(Float, nullable=True)

    def __repr__(self):
        """
        String representation for debugging.
        Called when you print() a SensorReading object.
        """
        return (
            f"<SensorReading("
            f"id={self.id}, "
            f"timestamp={self.timestamp}, "
            f"aqi={self.aqi}, "
            f"is_anomaly={self.is_anomaly}"
            f")>"
        )