import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { TrendingUp, Activity, BarChart3 } from 'lucide-react'

export default function BacktestResults({ results }) {
  const formatPercent = (value) => `${(value * 100).toFixed(2)}%`
  
  const getRegimeColor = (regime) => {
    switch (regime) {
      case 'Risk-On': return '#10b981'
      case 'Defensive': return '#ef4444'
      default: return '#6b7280'
    }
  }

  // Prepare equity curve data
  const equityCurveData = results.performance.equity_curve.map(point => ({
    date: new Date(point.date).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
    value: (point.cumulative * 100).toFixed(2),
    regime: point.regime
  }))

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-sm text-gray-600 mb-1">Total Return</div>
              <div className="text-3xl font-bold text-green-700">
                {formatPercent(results.performance.total_return)}
              </div>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600 opacity-50" />
          </div>
        </div>

        <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-sm text-gray-600 mb-1">Annualized Return</div>
              <div className="text-3xl font-bold text-blue-700">
                {formatPercent(results.performance.annualized_return)}
              </div>
            </div>
            <Activity className="w-8 h-8 text-blue-600 opacity-50" />
          </div>
        </div>

        <div className="card bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-sm text-gray-600 mb-1">Regime Changes</div>
              <div className="text-3xl font-bold text-purple-700">
                {results.regime_summary.changes_per_year.toFixed(2)}
              </div>
              <div className="text-xs text-gray-600 mt-1">per year</div>
            </div>
            <BarChart3 className="w-8 h-8 text-purple-600 opacity-50" />
          </div>
        </div>
      </div>

      {/* Equity Curve */}
      <div className="card">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Equity Curve</h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={equityCurveData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="date" 
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
              label={{ value: 'Portfolio Value (%)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e5e7eb',
                borderRadius: '8px'
              }}
              formatter={(value) => [`${value}%`, 'Value']}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#3b82f6" 
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Regime Statistics */}
      <div className="card">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Performance by Regime</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(results.performance.regime_stats).map(([regime, stats]) => (
            <div 
              key={regime}
              className="p-4 rounded-lg border-2"
              style={{ 
                backgroundColor: `${getRegimeColor(regime)}10`,
                borderColor: getRegimeColor(regime)
              }}
            >
              <div className="font-semibold text-gray-900 mb-3">{regime}</div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Periods:</span>
                  <span className="font-mono font-semibold">{stats.count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg Return:</span>
                  <span className="font-mono font-semibold">
                    {formatPercent(stats.avg_return)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Return:</span>
                  <span className="font-mono font-semibold">
                    {formatPercent(stats.total_return)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Win Rate:</span>
                  <span className="font-mono font-semibold">
                    {(stats.win_rate * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Regime Distribution */}
      <div className="card">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Regime Distribution</h3>
        <div className="space-y-3">
          {Object.entries(results.regime_summary.counts).map(([regime, count]) => {
            const total = Object.values(results.regime_summary.counts).reduce((a, b) => a + b, 0)
            const percentage = (count / total * 100).toFixed(1)
            
            return (
              <div key={regime}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">{regime}</span>
                  <span className="text-sm font-mono text-gray-600">
                    {count} weeks ({percentage}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="h-3 rounded-full transition-all"
                    style={{ 
                      width: `${percentage}%`,
                      backgroundColor: getRegimeColor(regime)
                    }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Configuration Summary */}
      <div className="card bg-gray-50">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Model Configuration</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-600">Thresholds</div>
            <div className="font-mono font-semibold">
              ±{Math.abs(results.config.threshold_riskon)}
            </div>
          </div>
          <div>
            <div className="text-gray-600">EWMA Span</div>
            <div className="font-mono font-semibold">
              {results.config.ewma_span} weeks
            </div>
          </div>
          <div>
            <div className="text-gray-600">DefCyc Weight</div>
            <div className="font-mono font-semibold">
              {results.config.weight_defcyc}×
            </div>
          </div>
          <div>
            <div className="text-gray-600">HiDiv Weight</div>
            <div className="font-mono font-semibold">
              {results.config.weight_hidivmkt}×
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
