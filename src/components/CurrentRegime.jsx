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

  const threshold = data.threshold_momdiv ?? 4
  const getScoreColor = (score) => {
    if (score >= threshold) return 'text-red-600'
    if (score <= -threshold) return 'text-green-600'
    return 'text-gray-600'
  }

  // Fallbacks so the UI still renders against older API payloads
  const momdiv = data.momdiv_score ?? data.ewma_score ?? 0
  const composite = data.composite_score ?? 0
  const fast = data.fast_ewma
  const slow = data.slow_ewma
  const divergence = data.divergence

  return (
    <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
      <div className="flex items-center justify-between flex-wrap gap-4">
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
          <div className="text-xs text-gray-500 mt-2">
            MomDiv regime: Defensive if score &ge; +{threshold}, Risk-On if &le; -{threshold}, else Neutral
          </div>
        </div>

        <div className="flex gap-6 flex-wrap">
          <div className="text-right">
            <div className="text-xs text-gray-600 mb-1">MomDiv Score</div>
            <div className={`text-3xl font-bold font-mono ${getScoreColor(momdiv)}`}>
              {Number(momdiv).toFixed(2)}
            </div>
          </div>

          <div className="text-right">
            <div className="text-xs text-gray-600 mb-1">Composite Score</div>
            <div className="text-3xl font-bold font-mono text-gray-700">
              {Number(composite).toFixed(0)}
            </div>
          </div>
        </div>
      </div>

      {/* EWMA Context Row */}
      {(fast \!== undefined || slow \!== undefined) && (
        <div className="mt-4 pt-4 border-t border-blue-200 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-xs text-gray-500 uppercase">Fast EWMA (span {data.config_fast ?? 3})</div>
            <div className="text-lg font-mono font-semibold">
              {fast \!== null && fast \!== undefined ? Number(fast).toFixed(2) : '—'}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500 uppercase">Slow EWMA (span {data.config_slow ?? 5})</div>
            <div className="text-lg font-mono font-semibold">
              {slow \!== null && slow \!== undefined ? Number(slow).toFixed(2) : '—'}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500 uppercase">Divergence (Fast - Slow)</div>
            <div className="text-lg font-mono font-semibold">
              {divergence \!== null && divergence \!== undefined ? Number(divergence).toFixed(2) : '—'}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500 uppercase">Legacy EWMA Score</div>
            <div className="text-lg font-mono font-semibold text-gray-500">
              {data.ewma_score \!== undefined ? Number(data.ewma_score).toFixed(2) : '—'}
            </div>
          </div>
        </div>
      )}

      {/* Signal Breakdown */}
      {data.signals && (
        <div className="mt-6 pt-6 border-t border-blue-200">
          <div className="text-sm font-semibold text-gray-700 mb-3">Signal Breakdown (5 subscores -> Composite)</div>
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
                    {Number(signal.weighted).toFixed(1)}
                  </span>
                  <span className="text-xs text-gray-500">
                    (z={Number(signal.z_score).toFixed(2)})
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
