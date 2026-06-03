# =============================================================
# sensor_simulator.py
# 
# PURPOSE: Simulate air quality sensor readings.
# 
# In a real deployment, this file would be replaced by
# actual sensor data coming from ESP32 / Arduino / MQTT.
# The rest of the pipeline doesn't change — only this file.
# =============================================================

import random
import math
from datetime import datetime

# -------------------------------------------------------------
# NORMAL RANGES
# These represent typical outdoor air quality in an Indian city.
# We'll use these to generate "normal" readings.
# Source: CPCB (Central Pollution Control Board) guidelines
# -------------------------------------------------------------
NORMAL_RANGES = {
    "pm25":       (10, 60),     # micrograms per cubic meter
    "pm10":       (20, 100),    # micrograms per cubic meter
    "co2":        (400, 1000),  # parts per million (ppm)
    "temperature":(22, 35),     # degrees Celsius
    "humidity":   (40, 80),     # percentage
}

# -------------------------------------------------------------
# ANOMALY RANGES
# These represent dangerous or unusual pollution events.
# For example: a factory nearby, a fire, heavy traffic.
# The ML model's job is to detect these automatically.
# -------------------------------------------------------------
ANOMALY_RANGES = {
    "pm25":       (150, 300),
    "pm10":       (200, 400),
    "co2":        (2000, 5000),
    "temperature":(42, 50),
    "humidity":   (90, 100),
}

# -------------------------------------------------------------
# ANOMALY PROBABILITY
# On average, 1 in every 20 readings will be an anomaly.
# You can increase this to test the ML model more aggressively.
# -------------------------------------------------------------
ANOMALY_PROBABILITY = 0.05


def calculate_aqi(pm25: float, pm10: float) -> int:
    """
    Calculate Air Quality Index (AQI) from PM2.5 and PM10.
    
    This uses a simplified version of the Indian AQI formula.
    In production you would use the full CPCB breakpoint table.
    
    Args:
        pm25: PM2.5 reading in micrograms per cubic meter
        pm10: PM10 reading in micrograms per cubic meter
    
    Returns:
        AQI as an integer
    """
    # Simplified AQI: take the worse of the two pollutants
    # PM2.5 is weighted more heavily as it's more dangerous
    aqi_from_pm25 = pm25 * 2.1
    aqi_from_pm10 = pm10 * 1.0
    
    return int(max(aqi_from_pm25, aqi_from_pm10))


def get_aqi_category(aqi: int) -> str:
    """
    Convert a numeric AQI value into a human-readable category.
    
    Based on CPCB (India) AQI categories.
    
    Args:
        aqi: Numeric AQI value
    
    Returns:
        Category string like "Good", "Moderate", etc.
    """
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"


def add_sensor_noise(value: float, noise_percent: float = 0.02) -> float:
    """
    Add small random noise to simulate real sensor imprecision.
    
    Real sensors are never perfectly accurate — they fluctuate
    slightly even in stable conditions. This makes our simulated
    data more realistic.
    
    Args:
        value: The base sensor reading
        noise_percent: How much noise to add (default 2%)
    
    Returns:
        Value with small random fluctuation added
    """
    noise = value * noise_percent * random.uniform(-1, 1)
    return round(value + noise, 2)


def generate_reading(force_anomaly: bool = False) -> dict:
    """
    Generate a single sensor reading.
    
    This is the main function you will call repeatedly
    to simulate a stream of sensor data.
    
    Args:
        force_anomaly: If True, forces an anomaly reading.
                      Useful for testing the ML model.
    
    Returns:
        Dictionary containing all sensor readings + metadata
    
    # -------------------------------------------------------
    # REPLACEMENT POINT
    # In production, replace this function's body with:
    #   - ESP32 serial port reading
    #   - MQTT message parsing
    #   - API call to a sensor network
    # The return format (dictionary keys) stays the same.
    # -------------------------------------------------------
    """
    
    # Decide if this reading is an anomaly
    is_anomaly = force_anomaly or (random.random() < ANOMALY_PROBABILITY)
    
    # Pick the right ranges based on normal vs anomaly
    ranges = ANOMALY_RANGES if is_anomaly else NORMAL_RANGES
    
    # Generate raw values within the chosen range
    pm25        = random.uniform(*ranges["pm25"])
    pm10        = random.uniform(*ranges["pm10"])
    co2         = random.uniform(*ranges["co2"])
    temperature = random.uniform(*ranges["temperature"])
    humidity    = random.uniform(*ranges["humidity"])
    
    # Add realistic sensor noise to each reading
    pm25        = add_sensor_noise(pm25)
    pm10        = add_sensor_noise(pm10)
    co2         = add_sensor_noise(co2)
    temperature = add_sensor_noise(temperature)
    humidity    = add_sensor_noise(humidity)
    
    # Calculate derived values
    aqi          = calculate_aqi(pm25, pm10)
    aqi_category = get_aqi_category(aqi)
    
    return {
        "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pm25":         round(pm25, 2),
        "pm10":         round(pm10, 2),
        "co2":          round(co2, 2),
        "temperature":  round(temperature, 2),
        "humidity":     round(humidity, 2),
        "aqi":          aqi,
        "aqi_category": aqi_category,
        "is_anomaly":   is_anomaly,
    }


def generate_dataset(num_readings: int = 1000) -> list:
    """
    Generate a batch of sensor readings as a list.
    
    Used for:
    - Training the ML model (needs historical data)
    - Testing the preprocessing pipeline
    - Populating the database with initial data
    
    Args:
        num_readings: How many readings to generate
    
    Returns:
        List of reading dictionaries
    """
    print(f"Generating {num_readings} sensor readings...")
    
    dataset = []
    for i in range(num_readings):
        reading = generate_reading()
        dataset.append(reading)
    
    anomaly_count = sum(1 for r in dataset if r["is_anomaly"])
    print(f"Done. {anomaly_count} anomalies in {num_readings} readings.")
    
    return dataset


# -------------------------------------------------------------
# QUICK TEST
# Run this file directly to verify everything works:
#   python data/sensor_simulator.py
# -------------------------------------------------------------
if __name__ == "__main__":
    print("=== Single Reading Test ===")
    reading = generate_reading()
    for key, value in reading.items():
        print(f"  {key:15}: {value}")
    
    print("\n=== Forced Anomaly Test ===")
    anomaly = generate_reading(force_anomaly=True)
    for key, value in anomaly.items():
        print(f"  {key:15}: {value}")
    
    print("\n=== Dataset Generation Test ===")
    dataset = generate_dataset(100)
    print(f"  First reading : {dataset[0]['timestamp']}")
    print(f"  Last reading  : {dataset[-1]['timestamp']}")