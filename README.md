# 🌬️ Air Quality Monitoring System

A full-stack air quality monitoring system with machine learning-based anomaly detection. Built with React, FastAPI, SQLite, and Scikit-learn.

---

## 📸 Preview

> Dashboard showing real-time AQI, PM2.5, CO₂, temperature, humidity, and ML-detected anomalies.

---

## 🚀 Features

- **Real-time Dashboard** — Live sensor readings with auto-refresh every 30 seconds
- **ML Anomaly Detection** — Isolation Forest model detects unusual pollution spikes automatically
- **Interactive Charts** — AQI trend visualization with anomaly markers
- **Alert System** — Cards pulse red when dangerous thresholds are crossed
- **Simulated Sensors** — Realistic data simulation, replaceable with real ESP32/Arduino sensors
- **REST API** — Full FastAPI backend with auto-generated documentation at `/docs`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS, Recharts |
| Backend | FastAPI, Uvicorn |
| Database | SQLite (upgradeable to PostgreSQL) |
| ORM | SQLAlchemy |
| Machine Learning | Scikit-learn (Isolation Forest) |
| Data Processing | Pandas, NumPy |

---

## 📁 Project Structure
air-quality-monitor/
├── frontend/                  # React dashboard
│   └── src/
│       ├── components/        # StatCard, AQIChart, AnomalyTable
│       └── services/          # API communication layer
├── backend/                   # FastAPI server
│   ├── main.py                # API endpoints
│   └── schemas.py             # Pydantic data models
├── data/                      # Sensor simulator
├── database/                  # DB models, connection, initializer
├── anomaly_detection/         # ML training and prediction
├── models/                    # Saved ML model files
├── preprocessing/             # Data cleaning pipeline
├── alerts/                    # Alert logic
├── tests/                     # Unit tests
└── docs/                      # Documentation

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Prateek0379/air-quality-monitor.git
cd air-quality-monitor
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize the database
```bash
python -m database.init_db
```

### 5. Train the ML model
```bash
python -m anomaly_detection.train
```

### 6. Start the backend
```bash
uvicorn backend.main:app --reload
```

### 7. Install and start the frontend
```bash
cd frontend
npm install
npm run dev
```

### 8. Open the dashboard
http://localhost:5173

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/readings` | Get recent readings |
| GET | `/readings/latest` | Get latest reading |
| GET | `/readings/anomalies` | Get anomalous readings |
| POST | `/readings/simulate` | Simulate a new reading |
| GET | `/stats` | Get summary statistics |

Full interactive API docs available at `http://127.0.0.1:8000/docs`

---

## 🤖 Machine Learning

The system uses **Isolation Forest** — an unsupervised anomaly detection algorithm that:

- Learns normal air quality patterns from historical data
- Detects unusual pollution spikes without needing labelled examples
- Returns an anomaly score for each reading (more negative = more anomalous)
- Flags approximately 5% of readings as anomalous based on the contamination parameter

### Features used for detection
- PM2.5, PM10, CO₂, Temperature, Humidity, AQI

---

## 🔮 Future Upgrades

- [ ] Replace simulated data with real ESP32/Arduino sensors via MQTT
- [ ] Upgrade database to PostgreSQL
- [ ] Add email/Telegram alerts
- [ ] Deploy with Docker
- [ ] Add AQI forecasting with time-series models
- [ ] Multi-city monitoring support

---