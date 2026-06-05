// =============================================================
// AQIChart.jsx
//
// PURPOSE: Line chart showing AQI trend over recent readings.
//          Anomalous readings are marked with red dots.
//
// Props:
//   readings - array of reading objects from the API
// =============================================================

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer, Dot
} from 'recharts'

const AQIChart = ({ readings }) => {

  const chartData = [...readings]
    .reverse()
    .map((r, index) => ({
      index,
      aqi:       r.aqi,
      pm25:      r.pm25,
      isAnomaly: r.is_anomaly,
      time:      new Date(r.timestamp).toLocaleTimeString(),
    }))

  const CustomDot = (props) => {
    const { cx, cy, payload } = props
    if (payload.isAnomaly) {
      return (
        <circle
          cx={cx} cy={cy} r={5}
          fill="#ef4444"
          stroke="#fff"
          strokeWidth={2}
        />
      )
    }
    return null
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-lg text-sm">
          <p className="font-semibold text-gray-700">{data.time}</p>
          <p className="text-blue-600">AQI: {data.aqi}</p>
          <p className="text-green-600">PM2.5: {data.pm25}</p>
          {data.isAnomaly && (
            <p className="text-red-500 font-bold">⚠ Anomaly detected</p>
          )}
        </div>
      )
    }
    return null
  }

  return (
    <div
      className="bg-white rounded-xl p-6"
      style={{
        border: '1px solid #e5e7eb',
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.05)',
      }}
    >
      <h2 className="text-lg font-semibold text-gray-700 mb-4">
        AQI Trend
        <span className="text-sm font-normal text-gray-400 ml-2">
          (red dots = anomalies)
        </span>
      </h2>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 11, fill: '#9ca3af' }}
            stroke="#e5e7eb"
            interval={Math.floor(chartData.length / 6)}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#9ca3af' }}
            stroke="#e5e7eb"
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            y={200}
            stroke="#ef4444"
            strokeDasharray="4 4"
            label={{ value: "Danger", fontSize: 11, fill: "#ef4444" }}
          />
          <Line
            type="monotone"
            dataKey="aqi"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={<CustomDot />}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default AQIChart