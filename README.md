# Air Quality Monitoring System

A full-stack air quality monitoring system with machine learning-based anomaly detection.

## Tech Stack

- **Frontend:** React, Tailwind CSS, Recharts
- **Backend:** FastAPI, SQLAlchemy
- **Database:** SQLite (upgradeable to PostgreSQL)
- **Machine Learning:** Scikit-learn (Isolation Forest)

## Project Structure
air_quality_monitor/
├── frontend/          # React dashboard
├── backend/           # FastAPI server
├── data/              # Datasets and raw sensor data
├── database/          # Schema and connection logic
├── preprocessing/     # Data cleaning and feature engineering
├── anomaly_detection/ # ML model training and prediction
├── alerts/            # Threshold and ML-based alerts
├── models/            # Saved ML model files
├── utils/             # Shared helper functions
├── tests/             # Unit and integration tests
└── docs/              # Architecture and documentation

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/prateek0379/air-quality-monitor.git
cd air-quality-monitor
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Status

🚧 Currently in development.