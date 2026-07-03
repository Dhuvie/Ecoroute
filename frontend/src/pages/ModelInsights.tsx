import { useEffect, useState } from 'react'
import Plot from 'react-plotly.js'
import { BrainCircuit, Target, Zap, TrendingUp } from 'lucide-react'
import { PageHeader, Card, Spinner, Badge } from '../components/ui'
import { api } from '../lib/api'

interface ModelMetrics {
  model: string
  mae: number
  rmse: number
  r2: number
  mape: number
  fit_seconds: number
  cv_r2_mean: number
  cv_r2_std: number
}

// Static fallback model comparison data (matches training output)
const FALLBACK_METRICS: ModelMetrics[] = [
  { model: 'linear_regression', mae: 78.01, rmse: 104.79, r2: 0.8219, mape: 836.75, fit_seconds: 0.03, cv_r2_mean: 0.803, cv_r2_std: 0.0063 },
  { model: 'random_forest', mae: 21.37, rmse: 37.20, r2: 0.9776, mape: 11.20, fit_seconds: 6.32, cv_r2_mean: 0.9718, cv_r2_std: 0.001 },
  { model: 'gradient_boosting', mae: 18.84, rmse: 30.37, r2: 0.9851, mape: 41.29, fit_seconds: 6.75, cv_r2_mean: 0.9851, cv_r2_std: 0.0 },
  { model: 'xgboost', mae: 15.50, rmse: 27.30, r2: 0.9879, mape: 15.77, fit_seconds: 0.72, cv_r2_mean: 0.9856, cv_r2_std: 0.0004 },
  { model: 'lightgbm', mae: 15.41, rmse: 27.02, r2: 0.9882, mape: 16.62, fit_seconds: 0.62, cv_r2_mean: 0.9851, cv_r2_std: 0.0004 },
  { model: 'catboost', mae: 15.89, rmse: 26.81, r2: 0.9883, mape: 20.97, fit_seconds: 1.41, cv_r2_mean: 0.9883, cv_r2_std: 0.0 },
]

const MODEL_DESCRIPTIONS: Record<string, string> = {
  linear_regression: 'Baseline linear model. Fast but cannot capture non-linear interactions.',
  random_forest: 'Ensemble of decision trees. Strong baseline, good generalization.',
  gradient_boosting: 'Sequential boosting. Excellent accuracy, slower to train.',
  xgboost: 'Extreme gradient boosting. Industry standard for tabular data.',
  lightgbm: 'Gradient boosting with histogram binning. Fast + accurate.',
  catboost: 'Boosting with native categorical handling. Best overall R².',
}

export default function ModelInsights() {
  const [metrics] = useState<ModelMetrics[]>(FALLBACK_METRICS)
  const [health, setHealth] = useState<{ model_name: string | null; model_loaded: boolean } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .health()
      .then((h) => setHealth(h))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="p-8 flex justify-center">
        <Spinner className="w-8 h-8" />
      </div>
    )
  }

  const sortedByR2 = [...metrics].sort((a, b) => b.r2 - a.r2)
  const best = sortedByR2[0]

  return (
    <div className="p-6 animate-fade-in">
      <PageHeader
        title="ML Model Insights"
        subtitle="Compare all six candidate fuel-prediction models and inspect the winner"
      />

      {/* Best model banner */}
      <Card className="mb-6 bg-gradient-to-br from-eco-500/10 to-transparent border-eco-500/30">
        <div className="flex items-center gap-4">
          <div className="p-4 rounded-xl bg-eco-500/15 text-eco-400">
            <BrainCircuit size={32} />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-white">
                {health?.model_name || best.model}
              </h2>
              <Badge className="bg-eco-500/15 text-eco-300 border-eco-500/30">
                Production Model
              </Badge>
            </div>
            <p className="text-sm text-slate-400 mt-1">
              {MODEL_DESCRIPTIONS[best.model]}
            </p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-eco-300">{(best.r2 * 100).toFixed(2)}%</p>
            <p className="text-xs text-slate-500 uppercase tracking-wider">R² Score</p>
          </div>
        </div>
      </Card>

      {/* Quick stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <div className="flex items-center gap-2 text-eco-400 mb-2">
            <Target size={16} />
            <span className="text-xs uppercase text-slate-500">MAE</span>
          </div>
          <p className="text-2xl font-bold text-white">{best.mae.toFixed(2)} L</p>
          <p className="text-xs text-slate-500 mt-1">Mean Absolute Error</p>
        </Card>
        <Card>
          <div className="flex items-center gap-2 text-amber-400 mb-2">
            <Target size={16} />
            <span className="text-xs uppercase text-slate-500">RMSE</span>
          </div>
          <p className="text-2xl font-bold text-white">{best.rmse.toFixed(2)} L</p>
          <p className="text-xs text-slate-500 mt-1">Root Mean Sq Error</p>
        </Card>
        <Card>
          <div className="flex items-center gap-2 text-blue-400 mb-2">
            <TrendingUp size={16} />
            <span className="text-xs uppercase text-slate-500">CV-R²</span>
          </div>
          <p className="text-2xl font-bold text-white">
            {best.cv_r2_mean.toFixed(4)} ± {best.cv_r2_std.toFixed(4)}
          </p>
          <p className="text-xs text-slate-500 mt-1">5-fold cross-validation</p>
        </Card>
        <Card>
          <div className="flex items-center gap-2 text-purple-400 mb-2">
            <Zap size={16} />
            <span className="text-xs uppercase text-slate-500">Train Time</span>
          </div>
          <p className="text-2xl font-bold text-white">{best.fit_seconds.toFixed(2)} s</p>
          <p className="text-xs text-slate-500 mt-1">On 9,600 samples</p>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <Card>
          <h3 className="text-sm font-semibold text-slate-200 mb-4">
            R² Score Comparison (higher is better)
          </h3>
          <Plot
            data={[
              {
                x: sortedByR2.map((m) => m.model),
                y: sortedByR2.map((m) => m.r2),
                type: 'bar',
                marker: {
                  color: sortedByR2.map((m) =>
                    m.model === best.model ? '#22c55e' : '#475569',
                  ),
                },
              },
            ] as any}
            layout={{
              paper_bgcolor: 'transparent',
              plot_bgcolor: 'transparent',
              font: { color: '#94a3b8', size: 11 },
              margin: { t: 10, r: 10, b: 60, l: 50 },
              xaxis: { gridcolor: '#1e293b', tickangle: -30 },
              yaxis: { gridcolor: '#1e293b', range: [0.8, 1.0], title: 'R²' },
              height: 320,
            } as any}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: '100%' }}
          />
        </Card>

        <Card>
          <h3 className="text-sm font-semibold text-slate-200 mb-4">
            MAE Comparison (lower is better)
          </h3>
          <Plot
            data={[
              {
                x: metrics.map((m) => m.model),
                y: metrics.map((m) => m.mae),
                type: 'bar',
                marker: {
                  color: metrics.map((m) =>
                    m.model === best.model ? '#22c55e' : '#7c3aed',
                  ),
                },
              },
            ] as any}
            layout={{
              paper_bgcolor: 'transparent',
              plot_bgcolor: 'transparent',
              font: { color: '#94a3b8', size: 11 },
              margin: { t: 10, r: 10, b: 60, l: 50 },
              xaxis: { gridcolor: '#1e293b', tickangle: -30 },
              yaxis: { gridcolor: '#1e293b', title: 'MAE (litres)' },
              height: 320,
            } as any}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: '100%' }}
          />
        </Card>
      </div>

      {/* Full metrics table */}
      <Card>
        <h3 className="text-sm font-semibold text-slate-200 mb-4">
          Complete Model Comparison
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ink-800 text-xs uppercase text-slate-500 tracking-wider">
                <th className="text-left px-4 py-3">Model</th>
                <th className="text-right px-4 py-3">MAE</th>
                <th className="text-right px-4 py-3">RMSE</th>
                <th className="text-right px-4 py-3">R²</th>
                <th className="text-right px-4 py-3">MAPE (%)</th>
                <th className="text-right px-4 py-3">CV-R²</th>
                <th className="text-right px-4 py-3">Train Time</th>
              </tr>
            </thead>
            <tbody>
              {sortedByR2.map((m) => (
                <tr
                  key={m.model}
                  className={`border-b border-ink-800/50 ${
                    m.model === best.model ? 'bg-eco-500/5' : ''
                  }`}
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-200">{m.model}</span>
                      {m.model === best.model && (
                        <Badge className="bg-eco-500/15 text-eco-300 border-eco-500/30">
                          Best
                        </Badge>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right text-slate-300">{m.mae.toFixed(2)}</td>
                  <td className="px-4 py-3 text-right text-slate-300">{m.rmse.toFixed(2)}</td>
                  <td className="px-4 py-3 text-right text-eco-300 font-mono">
                    {m.r2.toFixed(4)}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-400">{m.mape.toFixed(2)}</td>
                  <td className="px-4 py-3 text-right text-slate-300 font-mono">
                    {m.cv_r2_mean.toFixed(4)} ± {m.cv_r2_std.toFixed(4)}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-400">
                    {m.fit_seconds.toFixed(2)}s
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
