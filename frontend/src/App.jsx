// =============================================================
// App.jsx
//
// PURPOSE: Main dashboard component.
//          Fetches all data and composes the UI.
//
// Auto-refreshes every 30 seconds to show live data.
// =============================================================

import { useState, useEffect } from 'react'
import StatCard from './components/StatCard'
import AQIChart from './components/AQIChart'
import AnomalyTable from './components/AnomalyTable'
import { getStats, getReadings, getAnomalies, simulateReading } from './services/api'

function App() {
  const [stats, setStats]             = useState(null)
  const [readings, setReadings]       = useState([])
  const [anomalies, setAnomalies]     = useState([])
  const [loading, setLoading]         = useState(true)
  const [error, setError]             = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [simulating, setSimulating]   = useState(false)

  const fetchData = async () => {
    try {
      setError(null)
      const [statsData, readingsData, anomaliesData] = await Promise.all([
        getStats(),
        getReadings(100),
        getAnomalies(20),
      ])
      setStats(statsData)
      setReadings(readingsData)
      setAnomalies(anomaliesData)
      setLastUpdated(new Date().toLocaleTimeString())
    } catch (err) {
      setError("Cannot connect to backend. Make sure FastAPI is running.")
    } finally {
      setLoading(false)
    }
  }

  const handleSimulate = async () => {
    setSimulating(true)
    try {
      await simulateReading()
      await fetchData()
    } catch (err) {
      setError("Failed to simulate reading.")
    } finally {
      setSimulating(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const getAQIColor = (aqi) => {
    if (!aqi) return "blue"
    if (aqi <= 50)  return "green"
    if (aqi <= 100) return "yellow"
    if (aqi <= 200) return "orange"
    return "red"
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-gray-500 text-lg">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">

      {/* Header */}
      <div className="bg-white px-6 py-4 shadow-sm" style={{ borderBottom: '1px solid #e5e7eb' }}>
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">
              🌬️ Air Quality Monitor
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              Real-time monitoring with ML anomaly detection
            </p>
          </div>
          <div className="flex items-center gap-4">
            {lastUpdated && (
              <span className="text-xs text-gray-400">
                Last updated: {lastUpdated}
              </span>
            )}
            <button
              onClick={handleSimulate}
              disabled={simulating}
              className="bg-blue-600 hover:bg-blue-700 text-white text-sm px-4 py-2 rounded-lg disabled:opacity-50 transition-colors"
            >
              {simulating ? "Simulating..." : "Simulate Reading"}
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            ⚠️ {error}
          </div>
        )}

        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <StatCard title="AQI"         value={stats.latest_aqi}      unit={stats.latest_category}          color={getAQIColor(stats.latest_aqi)} alert={stats.latest_aqi > 200} />
            <StatCard title="PM2.5"       value={stats.avg_pm25}        unit="µg/m³ avg"                      color="blue" />
            <StatCard title="CO₂"         value={stats.avg_co2}         unit="ppm avg"                        color="purple" />
            <StatCard title="Temperature" value={stats.avg_temperature} unit="°C avg"                         color="orange" />
            <StatCard title="Humidity"    value={stats.avg_humidity}    unit="% avg"                          color="green" />
            <StatCard title="Anomalies"   value={stats.anomaly_count}   unit={`of ${stats.total_readings} readings`} color="red" alert={stats.anomaly_count > 0} />
          </div>
        )}

        {readings.length > 0 && <AQIChart readings={readings} />}

        <AnomalyTable anomalies={anomalies} />

      </div>
    </div>
  )
}

export default App