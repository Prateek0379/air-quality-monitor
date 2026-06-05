# =============================================================
# predict.py
#
# PURPOSE: Use the trained model to detect anomalies in
#          new sensor readings.
#
# This module is called by the FastAPI backend every time
# a new reading comes in. It returns:
# - is_anomaly: True/False
# - anomaly_score: raw score (more negative = more anomalous)
# =============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import joblib
from typing import Optional

MODEL_PATH  = "models/isolation_forest.joblib"
SCALER_PATH = "models/scaler.joblib"

FEATURE_COLUMNS = [
    "pm25",
    "pm10",
    "co2",
    "temperature",
    "humidity",
    "aqi"
]


def load_model():
    """
    Load the trained model and scaler from disk.

    Returns:
        Tuple of (model, scaler) or (None, None) if not found
    """
    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at {MODEL_PATH}. Train first.")
        return None, None

    if not os.path.exists(SCALER_PATH):
        print(f"Scaler not found at {SCALER_PATH}. Train first.")
        return None, None

    model  = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    return model, scaler


def predict_single(reading: dict) -> dict:
    """
    Predict whether a single sensor reading is anomalous.

    This is called every time a new reading arrives —
    either from the simulator or a real sensor.

    Args:
        reading: Dictionary with sensor values
                 Must contain all FEATURE_COLUMNS keys

    Returns:
        Dictionary with:
        - is_anomaly: bool
        - anomaly_score: float (more negative = more anomalous)
        - confidence: str ("high", "medium", "low")

    # -------------------------------------------------------
    # REPLACEMENT POINT
    # In production this function is called by the FastAPI
    # endpoint every time a new reading is submitted.
    # The reading dict comes directly from the sensor stream.
    # -------------------------------------------------------
    """
    model, scaler = load_model()

    if model is None:
        # Model not trained yet — default to not anomalous
        return {
            "is_anomaly":    False,
            "anomaly_score": None,
            "confidence":    "none"
        }

    # Extract features in the correct order
    import pandas as pd
    features = pd.DataFrame([{
        "pm25":        reading["pm25"],
        "pm10":        reading["pm10"],
        "co2":         reading["co2"],
        "temperature": reading["temperature"],
        "humidity":    reading["humidity"],
        "aqi":         reading["aqi"]
    }])

    # Scale using the same scaler used during training
    # Critical: must use transform(), NOT fit_transform()
    # fit_transform() would recalculate mean/std from this
    # single reading — completely wrong
    scaled = scaler.transform(features)

    # Get prediction: 1 = normal, -1 = anomaly
    prediction = model.predict(scaled)[0]

    # Get raw score: more negative = more anomalous
    score = model.score_samples(scaled)[0]

    # Convert to confidence level for the dashboard
    is_anomaly_flag = bool(prediction == -1)

    if not is_anomaly_flag:
        confidence = "none"        # normal reading — no anomaly confidence
    elif score < -0.55:
        confidence = "high"
    elif score < -0.45:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "is_anomaly":    bool(prediction == -1),
        "anomaly_score": round(float(score), 4),
        "confidence":    confidence
    }


def run_batch_prediction():
    """
    Run anomaly detection on all unscored readings
    in the database.

    Used after training to retroactively score
    all existing readings.
    """
    from database.database import SessionLocal
    from database.models import SensorReading

    model, scaler = load_model()
    if model is None:
        return

    db = SessionLocal()
    try:
        # Get readings that haven't been scored yet
        unscored = (
            db.query(SensorReading)
            .filter(SensorReading.anomaly_score == None)
            .all()
        )

        print(f"Scoring {len(unscored)} unscored readings...")

        for reading in unscored:
            result = predict_single({
                "pm25":        reading.pm25,
                "pm10":        reading.pm10,
                "co2":         reading.co2,
                "temperature": reading.temperature,
                "humidity":    reading.humidity,
                "aqi":         reading.aqi
            })

            reading.anomaly_score = result["anomaly_score"]

        db.commit()
        print("Batch scoring complete.")

    finally:
        db.close()


if __name__ == "__main__":
    print("=== Running Batch Anomaly Detection ===\n")
    run_batch_prediction()

    # Test with a normal reading
    print("\n=== Test: Normal Reading ===")
    normal = {
        "pm25": 45.0, "pm10": 80.0, "co2": 800.0,
        "temperature": 30.0, "humidity": 60.0, "aqi": 94
    }
    result = predict_single(normal)
    print(f"  is_anomaly    : {result['is_anomaly']}")
    print(f"  anomaly_score : {result['anomaly_score']}")
    print(f"  confidence    : {result['confidence']}")

    # Test with an anomalous reading
    print("\n=== Test: Anomalous Reading ===")
    anomaly = {
        "pm25": 280.0, "pm10": 350.0, "co2": 4500.0,
        "temperature": 47.0, "humidity": 95.0, "aqi": 588
    }
    result = predict_single(anomaly)
    print(f"  is_anomaly    : {result['is_anomaly']}")
    print(f"  anomaly_score : {result['anomaly_score']}")
    print(f"  confidence    : {result['confidence']}")