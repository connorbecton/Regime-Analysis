import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'

export default function ConfigEditor({ config, setConfig }) {
  const [expanded, setExpanded] = useState({
    weights: true,
    thresholds: true,
    advanced: false
  })

  const updateConfig = (key, value) => {
    setConfig({ ...config, [key]: parseFloat(value) || 0 })
  }

  const toggleSection = (section) => {
    setExpanded({ ...expanded, [section]: !expanded[section] })
  }

  return (
    <div className="space-y-4">
      {/* Signal Weights */}
      <div className="card">
        <button
          onClick={() => toggleSection('weights')}
          className="flex items-center justify-between w-full text-left mb-4"
        >
          <h2 className="text-xl font-bold text-gray-900">Signal Weights</h2>
          {expanded.weights ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>
        
        {expanded.weights && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="label">Defensive vs Cyclical</label>
              <input
                type="number"
                step="0.5"
                value={config.weight_defcyc}
                onChange={(e) => updateConfig('weight_defcyc', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">
                XLU/XLP/XLV vs XLF/XLI/XLB
              </p>
            </div>

            <div>
              <label className="label">Value vs Growth</label>
              <input
                type="number"
                step="0.5"
                value={config.weight_valgrw}
                onChange={(e) => updateConfig('weight_valgrw', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">RPV vs RPG</p>
            </div>

            <div>
              <label className="label">High Dividend vs Market</label>
              <input
                type="number"
                step="0.5"
                value={config.weight_hidivmkt}
                onChange={(e) => updateConfig('weight_hidivmkt', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">VYM vs SPY</p>
            </div>

            <div>
              <label className="label">Credit Spread</label>
              <input
                type="number"
                step="0.5"
                value={config.weight_crdsprd}
                onChange={(e) => updateConfig('weight_crdsprd', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">VSCH vs HYG</p>
            </div>

            <div>
              <label className="label">Low Beta vs High Beta</label>
              <input
                type="number"
                step="0.5"
                value={config.weight_lobhib}
                onChange={(e) => updateConfig('weight_lobhib', e.target.value)}
                className="input font-mono"
                disabled
              />
              <p className="text-xs text-gray-500 mt-1">Disabled (redundant)</p>
            </div>
          </div>
        )}
      </div>

      {/* Thresholds */}
      <div className="card">
        <button
          onClick={() => toggleSection('thresholds')}
          className="flex items-center justify-between w-full text-left mb-4"
        >
          <h2 className="text-xl font-bold text-gray-900">Regime Thresholds</h2>
          {expanded.thresholds ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>
        
        {expanded.thresholds && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="label">Risk-On Threshold</label>
              <input
                type="number"
                step="0.5"
                value={config.threshold_riskon}
                onChange={(e) => updateConfig('threshold_riskon', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter when EWMA ≤ this value
              </p>
            </div>

            <div>
              <label className="label">Defensive Threshold</label>
              <input
                type="number"
                step="0.5"
                value={config.threshold_defensive}
                onChange={(e) => updateConfig('threshold_defensive', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter when EWMA ≥ this value
              </p>
            </div>

            <div>
              <label className="label">EWMA Span (weeks)</label>
              <input
                type="number"
                step="1"
                min="3"
                max="10"
                value={config.ewma_span}
                onChange={(e) => updateConfig('ewma_span', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">
                Smoothing period (optimal: 6)
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Advanced Settings */}
      <div className="card">
        <button
          onClick={() => toggleSection('advanced')}
          className="flex items-center justify-between w-full text-left mb-4"
        >
          <h2 className="text-xl font-bold text-gray-900">Advanced Settings</h2>
          {expanded.advanced ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>
        
        {expanded.advanced && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="label">Momentum Lookback (weeks)</label>
              <input
                type="number"
                step="1"
                value={config.momentum_lookback}
                onChange={(e) => updateConfig('momentum_lookback', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">Default: 13 weeks</p>
            </div>

            <div>
              <label className="label">Z-Score Window (weeks)</label>
              <input
                type="number"
                step="1"
                value={config.zscore_window}
                onChange={(e) => updateConfig('zscore_window', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">Default: 252 weeks</p>
            </div>

            <div>
              <label className="label">Z-Score Moderate Threshold</label>
              <input
                type="number"
                step="0.25"
                value={config.zscore_moderate}
                onChange={(e) => updateConfig('zscore_moderate', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">Score = ±1</p>
            </div>

            <div>
              <label className="label">Z-Score Strong Threshold</label>
              <input
                type="number"
                step="0.25"
                value={config.zscore_strong}
                onChange={(e) => updateConfig('zscore_strong', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">Score = ±2</p>
            </div>
          </div>
        )}
      </div>

      {/* Preset Configs */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-gray-900 mb-3">Quick Presets</h3>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setConfig({
              ...config,
              weight_defcyc: 2.0,
              weight_valgrw: 2.0,
              weight_hidivmkt: 3.0,
              weight_crdsprd: 2.0,
              threshold_defensive: 7.0,
              threshold_riskon: -7.0,
              ewma_span: 6
            })}
            className="btn btn-primary text-sm"
          >
            Optimal (±7, Span 6)
          </button>
          
          <button
            onClick={() => setConfig({
              ...config,
              threshold_defensive: 8.0,
              threshold_riskon: -8.0,
              ewma_span: 6
            })}
            className="btn btn-secondary text-sm"
          >
            Conservative (±8)
          </button>
          
          <button
            onClick={() => setConfig({
              ...config,
              threshold_defensive: 6.0,
              threshold_riskon: -6.0,
              ewma_span: 5
            })}
            className="btn btn-secondary text-sm"
          >
            Aggressive (±6)
          </button>
        </div>
      </div>
    </div>
  )
}
