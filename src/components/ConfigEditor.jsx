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
                XLU/XLP/XLV vs XLF/XLI/XLK
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
              <p className="text-xs text-gray-500 mt-1">VCSH vs HYG</p>
            </div>

            <div>
              <label className="label">Low Beta vs High Beta</label>
              <input
                type="number"
                step="0.5"
                value={config.weight_lobhib}
                onChange={(e) => updateConfig('weight_lobhib', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">SPLV vs SPHB (set to 0 in Excel)</p>
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
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="label">MomDiv Threshold (±)</label>
              <input
                type="number"
                step="0.5"
                value={config.threshold_momdiv}
                onChange={(e) => updateConfig('threshold_momdiv', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">
                Defensive if score ≥ +X, Risk-On if ≤ −X
              </p>
            </div>

            <div>
              <label className="label">Fast EWMA Span</label>
              <input
                type="number"
                step="1"
                min="2"
                max="15"
                value={config.ewma_span_fast}
                onChange={(e) => updateConfig('ewma_span_fast', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">Short, aggressive (default: 3)</p>
            </div>

            <div>
              <label className="label">Slow EWMA Span</label>
              <input
                type="number"
                step="1"
                min="2"
                max="20"
                value={config.ewma_span_slow}
                onChange={(e) => updateConfig('ewma_span_slow', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">Long, conservative (default: 5)</p>
            </div>

            <div>
              <label className="label">Lambda (blend weight)</label>
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={config.lambda_blend}
                onChange={(e) => updateConfig('lambda_blend', e.target.value)}
                className="input font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">
                0 = slow only, 1 = fast only (default: 0.8)
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
        <h3 className="font-semibold text-gray-900 mb-3">Quick Presets (MomDiv)</h3>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setConfig({
              ...config,
              threshold_momdiv: 4.0,
              ewma_span_fast: 3,
              ewma_span_slow: 5,
              lambda_blend: 0.8
            })}
            className="btn btn-primary text-sm"
          >
            Default (±4, 3/5, λ=0.8)
          </button>

          <button
            onClick={() => setConfig({
              ...config,
              threshold_momdiv: 5.0,
              ewma_span_fast: 3,
              ewma_span_slow: 8,
              lambda_blend: 0.7
            })}
            className="btn btn-secondary text-sm"
          >
            Conservative (±5, 3/8)
          </button>

          <button
            onClick={() => setConfig({
              ...config,
              threshold_momdiv: 3.0,
              ewma_span_fast: 2,
              ewma_span_slow: 4,
              lambda_blend: 0.9
            })}
            className="btn btn-secondary text-sm"
          >
            Aggressive (±3, 2/4)
          </button>
        </div>
      </div>
    </div>
  )
}
