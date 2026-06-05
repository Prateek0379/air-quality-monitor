// =============================================================
// AnomalyTable.jsx
//
// PURPOSE: Table showing recent anomalous readings.
//          Helps operators quickly see what was flagged.
//
// Props:
//   anomalies - array of anomalous reading objects
// =============================================================

const AnomalyTable = ({ anomalies }) => {

  const formatTime = (timestamp) => new Date(timestamp).toLocaleString()

  const getScoreColor = (score) => {
    if (!score) return "#9ca3af"
    if (score < -0.55) return "#ef4444"
    if (score < -0.45) return "#f97316"
    return "#eab308"
  }

  if (!anomalies || anomalies.length === 0) {
    return (
      <div
        className="bg-white rounded-xl p-6 text-center text-gray-400"
        style={{
          border: '1px solid #e5e7eb',
          boxShadow: '0 4px 6px -1px rgba(0,0,0,0.07)',
        }}
      >
        No anomalies detected yet.
      </div>
    )
  }

  return (
    <div
      className="bg-white rounded-xl overflow-hidden"
      style={{
        border: '1px solid #e5e7eb',
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.05)',
      }}
    >
      {/* Header */}
      <div className="p-5" style={{ borderBottom: '1px solid #e5e7eb' }}>
        <h2 className="text-lg font-semibold text-gray-700">
          Recent Anomalies
          <span className="ml-2 text-xs px-2 py-1 rounded-full bg-red-100 text-red-600">
            {anomalies.length} detected
          </span>
        </h2>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 text-gray-400 text-xs uppercase tracking-wider">
              <th className="px-5 py-3 text-left">Time</th>
              <th className="px-5 py-3 text-left">AQI</th>
              <th className="px-5 py-3 text-left">PM2.5</th>
              <th className="px-5 py-3 text-left">CO₂</th>
              <th className="px-5 py-3 text-left">Score</th>
              <th className="px-5 py-3 text-left">Category</th>
            </tr>
          </thead>
          <tbody>
            {anomalies.map((reading, index) => (
              <tr
                key={reading.id}
                className="transition-colors hover:bg-red-50"
                style={{
                  borderBottom: '1px solid #f3f4f6',
                  backgroundColor: index % 2 === 0 ? '#ffffff' : '#fafafa',
                }}
                onMouseEnter={e => e.currentTarget.style.backgroundColor = '#fff1f1'}
                onMouseLeave={e => e.currentTarget.style.backgroundColor = index % 2 === 0 ? '#ffffff' : '#fafafa'}
              >
                <td className="px-5 py-3 text-gray-500">{formatTime(reading.timestamp)}</td>
                <td className="px-5 py-3 font-semibold text-red-500">{reading.aqi}</td>
                <td className="px-5 py-3 text-gray-700">{reading.pm25}</td>
                <td className="px-5 py-3 text-gray-700">{reading.co2}</td>
                <td className="px-5 py-3 font-semibold" style={{ color: getScoreColor(reading.anomaly_score) }}>
                  {reading.anomaly_score ?? "—"}
                </td>
                <td className="px-5 py-3">
                  <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-600">
                    {reading.aqi_category}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default AnomalyTable