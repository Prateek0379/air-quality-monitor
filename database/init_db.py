# =============================================================
# init_db.py
#
# PURPOSE: Create the database tables and populate with
#          initial simulated data for development/testing.
#
# Run this file once before starting the application:
#   python database/init_db.py
# =============================================================

import sys
import os

# Add the project root to Python's path so imports work
# This is needed when running scripts from subfolders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import engine, SessionLocal, Base
from database.models import SensorReading
from data.sensor_simulator import generate_dataset
from datetime import datetime, timedelta


def create_tables():
    """
    Create all database tables defined in models.py.
    
    Base.metadata.create_all() looks at all classes that
    inherit from Base and creates their tables if they
    don't already exist. Safe to run multiple times.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")


def populate_initial_data(num_readings: int = 500):
    """
    Fill the database with simulated sensor readings.
    
    This gives us historical data to:
    - Train the ML model
    - Display on the dashboard charts
    - Test our API endpoints
    
    Args:
        num_readings: How many readings to insert
    """
    db = SessionLocal()

    try:
        # Check if data already exists — don't duplicate
        existing = db.query(SensorReading).count()
        if existing > 0:
            print(f"Database already has {existing} readings. Skipping.")
            return

        print(f"Inserting {num_readings} readings into database...")

        # Generate simulated data
        dataset = generate_dataset(num_readings)

        # Create timestamps spread over the last 24 hours
        # so charts show meaningful historical trends
        now = datetime.now()
        time_step = timedelta(hours=24) / num_readings

        readings = []
        for i, data in enumerate(dataset):
            # Spread readings evenly over last 24 hours
            timestamp = now - timedelta(hours=24) + (time_step * i)

            reading = SensorReading(
                timestamp=timestamp,
                pm25=data["pm25"],
                pm10=data["pm10"],
                co2=data["co2"],
                temperature=data["temperature"],
                humidity=data["humidity"],
                aqi=data["aqi"],
                aqi_category=data["aqi_category"],
                is_anomaly=data["is_anomaly"],
            )
            readings.append(reading)

        # Bulk insert — much faster than inserting one by one
        db.bulk_save_objects(readings)
        db.commit()

        print(f"Successfully inserted {num_readings} readings.")
        anomaly_count = sum(1 for r in readings if r.is_anomaly)
        print(f"Anomalies in dataset: {anomaly_count}")

    except Exception as e:
        print(f"Error inserting data: {e}")
        db.rollback()  # Undo any partial inserts on error

    finally:
        db.close()  # Always close the session


def verify_database():
    """
    Quick sanity check — print a few rows to confirm
    everything was inserted correctly.
    """
    db = SessionLocal()
    try:
        total = db.query(SensorReading).count()
        latest = db.query(SensorReading).order_by(
            SensorReading.timestamp.desc()
        ).first()

        print(f"\n=== Database Verification ===")
        print(f"Total readings : {total}")
        if latest:
            print(f"Latest reading : {latest}")
            print(f"Latest AQI     : {latest.aqi} ({latest.aqi_category})")

    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    populate_initial_data(500)
    verify_database()