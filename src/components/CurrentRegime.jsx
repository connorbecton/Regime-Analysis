export default function CurrentRegime({ data }) {
  const getRegimeColor = (regime) => {
    switch (regime) {
      case 'Risk-On':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'Defensive':
        return 'bg-red-100 text-red-800 border-red-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getScoreColor = (score) => {
    if (score >= 7) return 'text-red-600'
    if (score <= -7) return 'text-green-600'
    return 'text-gray-600'
  }

  return (
    <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-gray-600 mb-1">Current Market Regime</div>
          <div className="flex items-center gap-3">
            <span className={`px-4 py-2 rounded-lg font-bold text-lg border-2 ${getRegimeColor(data.regime)}`}>
              {data.regime}
            </span>
            <div className="text-sm text-gray-600">
              as of {new Date(data.date).toLocaleDateString()}
            </div>
          </div>
        </div>
        
        <div className="flex gap-6">
          <div className="text-right">
            <div className="text-xs text-gray-600 mb-1">EWMA Score</div>
            <div className={`text-3xl font-bold font-mono ${getScoreColor(data.ewma_score)}`}>
              {data.ewma_score.toFixed(2)}
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-xs text-gray-600 mb-1">Composite Score</div>
            <div className={`text-3xl font-bold font-mono ${getScoreColor(data.composite_score)}`}>
              {data.composite_score.toFixed(0)}
            </div>
          </div>
        </div>
      </div>

      {/* Signal Breakdown */}
      {data.signals && (
        <div className="mt-6 pt-6 border-t border-blue-200">
          <div className="text-sm font-semibold text-gray-700 mb-3">Signal Breakdown</div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(data.signals).map(([name, signal]) => (
              <div key={name} className="bg-white rounded-lg p-3 border border-gray-200">
                <div className="text-xs text-gray-500 uppercase mb-1">
                  {name === 'defcyc' ? 'Def vs Cyc' :
                   name === 'valgrw' ? 'Val vs Grw' :
                   name === 'hidivmkt' ? 'HiDiv vs Mkt' :
                   'Credit Spread'}
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-lg font-bold font-mono">
                    {signal.weighted.toFixed(1)}
                  </span>
                  <span className="text-xs text-gray-500">
                    (z={signal.z_score.toFixed(2)})
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
