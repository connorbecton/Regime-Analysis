import { useState } from 'react'
import ConfigEditor from './components/ConfigEditor'
import PortfolioEditor from './components/PortfolioEditor'
import BacktestResults from './components/BacktestResults'
import CurrentRegime from './components/CurrentRegime'
import { Play, Settings, BarChart3, Activity } from 'lucide-react'

const API_URL = import.meta.env.PROD ? '/api' : 'http://localhost:8000/api'

function App() {
  const [config, setConfig] = useState({
    weight_defcyc: 2.0,
    weight_lobhib: 0.0,
    weight_valgrw: 2.0,
    weight_hidivmkt: 3.0,
    weight_crdsprd: 2.0,
    threshold_defensive: 7.0,
    threshold_riskon: -7.0,
    ewma_span: 6,
    momentum_lookback: 13,
    zscore_window: 252,
    zscore_moderate: 0.75,
    zscore_strong: 1.5,
    cyclical_etfs: ['XLF', 'XLI', 'XLB'],
    // MomDiv (speed-adjusted blend) params
    ewma_span_fast: 3,
    ewma_span_slow: 5,
    lambda_blend: 0.8,
    threshold_momdiv: 4.0
  })

  const [portfolio, setPortfolio] = useState({
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

  const [results, setResults] = useState(null)
  const [currentRegime, setCurrentRegime] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('config')

  const runBacktest = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/backtest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          config,
          portfolio,
          start_date: '2016-01-01',
          end_date: new Date().toISOString().split('T')[0]
        })
      })
      
      if (!response.ok) {
        const err = await response.json().catch(() => ({}))
        throw new Error(err.detail || `HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      setResults(data)
      setCurrentRegime(data.current_regime)
    } catch (error) {
      console.error('Backtest error:', error)
      alert(`Error running backtest: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const fetchCurrentRegime = async () => {
    try {
      const response = await fetch(`${API_URL}/current-regime`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      })

      if (!response.ok) {
        const err = await response.json().catch(() => ({}))
        throw new Error(err.detail || `HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setCurrentRegime(data)
    } catch (error) {
      console.error('Error fetching current regime:', error)
      alert(`Error fetching current regime: ${error.message}`)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Market Regime Detection
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Enhanced Momentum Model v3 · MomDiv (Speed-Adjusted Blend)
              </p>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={fetchCurrentRegime}
                className="btn btn-secondary flex items-center gap-2"
              >
                <Activity className="w-4 h-4" />
                Current Regime
              </button>
              
              <button
                onClick={runBacktest}
                disabled={loading}
                className="btn btn-primary flex items-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Running...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Run Backtest
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Current Regime Display */}
      {currentRegime && (
        <div className="max-w-7xl mx-auto px-6 py-4">
          <CurrentRegime data={currentRegime} />
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('config')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'config'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Configuration
            </div>
          </button>
          
          <button
            onClick={() => setActiveTab('portfolio')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'portfolio'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Portfolio Allocations
            </div>
          </button>
          
          {results && (
            <button
              onClick={() => setActiveTab('results')}
              className={`px-4 py-2 font-medium border-b-2 transition-colors ${
                activeTab === 'results'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Results
              </div>
            </button>
          )}
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'config' && (
            <ConfigEditor config={config} setConfig={setConfig} />
          )}
          
          {activeTab === 'portfolio' && (
            <PortfolioEditor portfolio={portfolio} setPortfolio={setPortfolio} />
          )}
          
          {activeTab === 'results' && results && (
            <BacktestResults results={results} />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <p className="text-sm text-gray-600 text-center">
            Data sourced from stooq.com (weekly close) ·
            Model: MomDiv (dual-EWMA speed-adjusted blend) · ±4 regime threshold
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
