# =============================================================
# train.py
#
# PURPOSE: Train an Isolation Forest model on historical
#          sensor data to learn what "normal" looks like.
#
# This script:
# 1. Loads historical readings from the database
# 2. Preprocesses and scales the features
# 3. Trains the Isolation Forest model
# 4. Saves the model and scaler to disk
#
# Run this file to train or retrain the model:
#   python anomaly_detection/train.py
# =============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from database.database import SessionLocal
from database.models import SensorReading

# -------------------------------------------------------------
# FEATURE COLUMNS
# These are the sensor readings we feed to the ML model.
# We exclude: id, timestamp, aqi_category (text),
#             is_anomaly (label), anomaly_score (output)
# -------------------------------------------------------------
FEATURE_COLUMNS = [
    "pm25",
    "pm10",
    "co2",
    "temperature",
    "humidity",
    "aqi"
]

# -------------------------------------------------------------
# MODEL PATHS
# Where to save the trained model and scaler.
# joblib is better than pickle for numpy/sklearn objects.
# -------------------------------------------------------------
MODEL_PATH  = "models/isolation_forest.joblib"
SCALER_PATH = "models/scaler.joblib"


def load_training_data() -> pd.DataFrame:
    """
    Load historical sensor readings from the database.

    We only load NORMAL readings for training.
    Why? Because Isolation Forest learns what normal looks
    like — we don't want anomalies polluting that definition.

    Returns:
        DataFrame with feature columns only
    """
    db = SessionLocal()
    try:
        # Load only non-anomalous readings for training
        readings = (
            db.query(SensorReading)
            .filter(SensorReading.is_anomaly == False)
            .all()
        )

        if len(readings) < 50:
            raise ValueError(
                f"Not enough training data. "
                f"Found {len(readings)} readings, need at least 50."
            )

        # Convert SQLAlchemy objects to a pandas DataFrame
        data = pd.DataFrame([{
            "pm25":        r.pm25,
            "pm10":        r.pm10,
            "co2":         r.co2,
            "temperature": r.temperature,
            "humidity":    r.humidity,
            "aqi":         r.aqi,
        } for r in readings])

        print(f"Loaded {len(data)} normal readings for training.")
        return data

    finally:
        db.close()


def preprocess_features(df: pd.DataFrame) -> tuple:
    """
    Scale features so no single feature dominates.

    Without scaling:
    - CO2 values range 400-1000
    - Humidity values range 40-80
    - The model treats CO2 as more important just
      because its numbers are larger. That's wrong.

    StandardScaler transforms each feature to have:
    - Mean of 0
    - Standard deviation of 1
    - Now all features are equally weighted

    Args:
        df: Raw feature DataFrame

    Returns:
        Tuple of (scaled_array, fitted_scaler)
    """
    scaler = StandardScaler()

    # fit_transform: learns the mean/std AND applies scaling
    scaled = scaler.fit_transform(df[FEATURE_COLUMNS])

    print(f"Features scaled. Shape: {scaled.shape}")
    return scaled, scaler


def train_model(scaled_data: np.ndarray) -> IsolationForest:
    """
    Train the Isolation Forest model.

    Key parameters explained:
    - n_estimators: Number of isolation trees to build.
      More trees = more stable results but slower training.
      100 is a good default.

    - contamination: What fraction of data we expect to be
      anomalous. We set 0.05 = 5%, matching our simulator.
      In production, tune this based on domain knowledge.

    - random_state: Seed for reproducibility. With the same
      seed, training always produces the same model.
      Critical for debugging and comparing experiments.

    Args:
        scaled_data: Preprocessed feature array

    Returns:
        Trained IsolationForest model
    """
    print("Training Isolation Forest model...")

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
        verbose=0
    )

    # fit() is where actual training happens
    # The model builds 100 random isolation trees
    model.fit(scaled_data)

    print("Model training complete.")
    return model


def evaluate_model(
    model: IsolationForest,
    scaler: StandardScaler,
    df: pd.DataFrame
):
    """
    Quick evaluation — check how the model performs
    on the training data itself.

    Note: In production you'd use a separate test set.
    For anomaly detection with limited labelled data,
    this sanity check is acceptable.
    """
    scaled = scaler.transform(df[FEATURE_COLUMNS])

    # predict() returns 1 for normal, -1 for anomaly
    predictions = model.predict(scaled)

    # score_samples() returns the raw anomaly score
    # More negative = more anomalous
    scores = model.score_samples(scaled)

    normal_count  = (predictions == 1).sum()
    anomaly_count = (predictions == -1).sum()

    print(f"\n=== Model Evaluation ===")
    print(f"Training samples : {len(predictions)}")
    print(f"Flagged normal   : {normal_count}")
    print(f"Flagged anomaly  : {anomaly_count}")
    print(f"Anomaly rate     : {anomaly_count/len(predictions)*100:.1f}%")
    print(f"Score range      : {scores.min():.3f} to {scores.max():.3f}")


def save_model(model: IsolationForest, scaler: StandardScaler):
    """
    Save the trained model and scaler to disk.

    We save BOTH because at prediction time we need to
    scale new readings the same way we scaled training data.
    If we only saved the model, we'd have no way to
    consistently scale incoming sensor readings.

    joblib is more efficient than pickle for large
    numpy arrays inside sklearn objects.
    """
    os.makedirs("models", exist_ok=True)

    joblib.dump(model,  MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    print(f"\nModel  saved → {MODEL_PATH}")
    print(f"Scaler saved → {SCALER_PATH}")


if __name__ == "__main__":
    print("=== Isolation Forest Training Pipeline ===\n")

    # Step 1: Load data
    df = load_training_data()

    # Step 2: Scale features
    scaled_data, scaler = preprocess_features(df)

    # Step 3: Train model
    model = train_model(scaled_data)

    # Step 4: Evaluate
    evaluate_model(model, scaler, df)

    # Step 5: Save
    save_model(model, scaler)

    print("\n✓ Training pipeline complete.")