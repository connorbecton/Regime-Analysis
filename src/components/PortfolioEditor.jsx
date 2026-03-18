import { useState } from 'react'

const SECTOR_ETFS = [
  { ticker: 'XLF', name: 'Financials' },
  { ticker: 'XLI', name: 'Industrials' },
  { ticker: 'XLB', name: 'Materials' },
  { ticker: 'XLK', name: 'Technology' },
  { ticker: 'XLY', name: 'Consumer Discretionary' },
  { ticker: 'XLC', name: 'Communication Services' },
  { ticker: 'XLU', name: 'Utilities' },
  { ticker: 'XLP', name: 'Consumer Staples' },
  { ticker: 'XLV', name: 'Healthcare' }
]

export default function PortfolioEditor({ portfolio, setPortfolio }) {
  const [activeRegime, setActiveRegime] = useState('risk_on')

  const updateAllocation = (regime, ticker, value) => {
    const newPortfolio = { ...portfolio }
    newPortfolio[regime] = {
      ...newPortfolio[regime],
      [ticker]: parseFloat(value) / 100 || 0
    }
    setPortfolio(newPortfolio)
  }

  const getTotalAllocation = (regime) => {
    return Object.values(portfolio[regime]).reduce((sum, val) => sum + val, 0)
  }

  const resetToEqualWeight = (regime) => {
    const equalWeight = 1 / SECTOR_ETFS.length
    const newAllocation = {}
    SECTOR_ETFS.forEach(({ ticker }) => {
      newAllocation[ticker] = equalWeight
    })
    setPortfolio({ ...portfolio, [regime]: newAllocation })
  }

  const renderAllocationTable = (regime, regimeName) => {
    const total = getTotalAllocation(regime)
    const isValid = Math.abs(total - 1.0) < 0.01

    return (
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-900">{regimeName}</h3>
          <button
            onClick={() => resetToEqualWeight(regime)}
            className="btn btn-secondary text-sm"
          >
            Reset to Equal Weight
          </button>
        </div>

        <div className="space-y-3">
          {SECTOR_ETFS.map(({ ticker, name }) => (
            <div key={ticker} className="flex items-center gap-4">
              <div className="w-12 text-sm font-mono font-semibold text-gray-700">
                {ticker}
              </div>
              <div className="flex-1 text-sm text-gray-600">
                {name}
              </div>
              <div className="relative w-32">
                <input
                  type="number"
                  step="1"
                  min="0"
                  max="100"
                  value={((portfolio[regime][ticker] || 0) * 100).toFixed(1)}
                  onChange={(e) => updateAllocation(regime, ticker, e.target.value)}
                  className="input text-right font-mono pr-8"
                />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">
                  %
                </span>
              </div>
              <div className="w-32">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${(portfolio[regime][ticker] || 0) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-gray-900">Total Allocation</span>
            <div className="flex items-center gap-3">
              <span className={`text-xl font-bold font-mono ${
                isValid ? 'text-green-600' : 'text-red-600'
              }`}>
                {(total * 100).toFixed(1)}%
              </span>
              {!isValid && (
                <span className="text-xs text-red-600">
                  Must equal 100%
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Regime Selector */}
      <div className="flex gap-2 bg-white rounded-lg p-1 border border-gray-200 w-fit">
        <button
          onClick={() => setActiveRegime('risk_on')}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            activeRegime === 'risk_on'
              ? 'bg-green-100 text-green-700'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          Risk-On
        </button>
        <button
          onClick={() => setActiveRegime('neutral')}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            activeRegime === 'neutral'
              ? 'bg-gray-100 text-gray-700'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          Neutral
        </button>
        <button
          onClick={() => setActiveRegime('defensive')}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            activeRegime === 'defensive'
              ? 'bg-red-100 text-red-700'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          Defensive
        </button>
      </div>

      {/* Allocation Tables */}
      {activeRegime === 'risk_on' && renderAllocationTable('risk_on', 'Risk-On Portfolio')}
      {activeRegime === 'neutral' && renderAllocationTable('neutral', 'Neutral Portfolio')}
      {activeRegime === 'defensive' && renderAllocationTable('defensive', 'Defensive Portfolio')}

      {/* Preset Allocations */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-gray-900 mb-3">Quick Presets</h3>
        <p className="text-sm text-gray-600 mb-4">
          Apply common allocation strategies across all regimes
        </p>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => {
              setPortfolio({
                risk_on: {
                  XLF: 0.20, XLI: 0.20, XLB: 0.15,
                  XLK: 0.10, XLY: 0.10, XLC: 0.05,
                  XLU: 0.05, XLP: 0.05, XLV: 0.10
                },
                neutral: {
                  XLF: 0.11, XLI: 0.11, XLB: 0.11,
                  XLK: 0.11, XLY: 0.11, XLC: 0.11,
                  XLU: 0.11, XLP: 0.11, XLV: 0.11
                },
                defensive: {
                  XLU: 0.20, XLP: 0.20, XLV: 0.20,
                  XLF: 0.10, XLI: 0.10, XLB: 0.05,
                  XLK: 0.05, XLY: 0.05, XLC: 0.05
                }
              })
            }}
            className="btn btn-primary text-sm"
          >
            Default (Cyclical Tilt)
          </button>
          
          <button
            onClick={() => {
              const equalWeight = {
                XLF: 0.11, XLI: 0.11, XLB: 0.11,
                XLK: 0.11, XLY: 0.11, XLC: 0.11,
                XLU: 0.11, XLP: 0.11, XLV: 0.11
              }
              setPortfolio({
                risk_on: equalWeight,
                neutral: equalWeight,
                defensive: equalWeight
              })
            }}
            className="btn btn-secondary text-sm"
          >
            Equal Weight (All Regimes)
          </button>
        </div>
      </div>
    </div>
  )
}
