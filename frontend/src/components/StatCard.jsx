// =============================================================
// StatCard.jsx
//
// PURPOSE: Display a single metric (AQI, PM2.5, etc.)
//          as a clean card with a title, value, and unit.
//
// Props:
//   title  - e.g. "PM2.5"
//   value  - e.g. 47.3
//   unit   - e.g. "µg/m³"
//   color  - tailwind color class e.g. "blue"
//   alert  - boolean, true = show red warning style
// =============================================================

const StatCard = ({ title, value, unit, color = "blue", alert = false }) => {

  const colorMap = {
    blue:   "border-blue-200 text-blue-700 bg-blue-50",
    green:  "border-green-200 text-green-700 bg-green-50",
    yellow: "border-yellow-200 text-yellow-600 bg-yellow-50",
    red:    "border-red-200 text-red-700 bg-red-50",
    purple: "border-purple-200 text-purple-700 bg-purple-50",
    orange: "border-orange-200 text-orange-600 bg-orange-50",
  }

  const colorClass = alert
    ? "border-red-400 text-red-700 bg-red-50 animate-pulse"
    : colorMap[color] || colorMap.blue

  return (
    <div
      className={`rounded-xl border-2 p-4 ${colorClass}`}
      style={{
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.05)',
        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
        cursor: 'default',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.transform = 'translateY(-4px)'
        e.currentTarget.style.boxShadow = '0 10px 25px -3px rgba(0,0,0,0.12), 0 4px 6px -2px rgba(0,0,0,0.07)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.05)'
      }}
    >
      <p className="text-sm font-medium opacity-70">{title}</p>
      <p className="text-3xl font-bold mt-1">
        {value !== null && value !== undefined ? value : "—"}
      </p>
      <p className="text-xs mt-1 opacity-60">{unit}</p>
    </div>
  )
}

export default StatCard