import { useEffect, useState } from 'react'
import {
  Leaf,
  Fuel,
  TrendingDown,
  Clock,
  Truck,
  Activity,
  DollarSign,
  BarChart3,
} from 'lucide-react'
import Plot from 'react-plotly.js'
import { PageHeader, KpiCard, Card, Spinner } from '../components/ui'
import { api } from '../lib/api'
import { formatNumber, formatCompact, formatCurrency } from '../lib/utils'
import type { AnalyticsSummary, TimeSeriesResponse, HealthResponse } from '../types'

export default function Dashboard() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [fuelSeries, setFuelSeries] = useState<TimeSeriesResponse | null>(null)
  const [co2Series, setCo2Series] = useState<TimeSeriesResponse | null>(null)
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.analyticsSummary('all'),
      api.analyticsTimeseries('fuel', 30),
      api.analyticsTimeseries('co2', 30),
      api.health(),
    ])
      .then(([s, f, c, h]) => {
        setSummary(s)
        setFuelSeries(f)
        setCo2Series(c)
        setHealth(h)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading || !summary) {
    return (
      <div className="p-8 flex items-center justify-center">
        <Spinner className="w-8 h-8" />
      </div>
    )
  }

  const fuelDates = fuelSeries?.points.map((p) => p.timestamp.slice(0, 10)) || []
  const fuelValues = fuelSeries?.points.map((p) => p.value) || []
  const co2Values = co2Series?.points.map((p) => p.value) || []

  return (
    <div className="p-6 animate-fade-in">
      <PageHeader
        title="Dashboard"
        subtitle="Real-time fleet performance and ML-driven optimization insights"
      />

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KpiCard
          label="Fuel Saved"
          value={formatNumber(summary.fuel_saved_l, 0)}
          unit="L"
          delta="≈ 18% reduction vs naive routing"
          trend="up"
          icon={<Fuel size={20} />}
          accent="eco"
        />
        <KpiCard
          label="CO₂ Reduced"
          value={formatNumber(summary.co2_saved_kg, 0)}
          unit="kg"
          delta="Carbon footprint savings"
          trend="up"
          icon={<Leaf size={20} />}
          accent="eco"
        />
        <KpiCard
          label="Cost Savings"
          value={formatCurrency(summary.cost_saved_inr)}
          delta="INR saved via optimization"
          trend="up"
          icon={<DollarSign size={20} />}
          accent="blue"
        />
        <KpiCard
          label="Vehicle Utilization"
          value={formatNumber(summary.vehicle_utilization_pct, 1)}
          unit="%"
          delta="Active vehicles in fleet"
          trend="up"
          icon={<Truck size={20} />}
          accent="purple"
        />
        <KpiCard
          label="Total Deliveries"
          value={formatNumber(summary.total_deliveries)}
          delta="All-time"
          icon={<Activity size={20} />}
          accent="blue"
        />
        <KpiCard
          label="Avg Delivery Time"
          value={formatNumber(summary.avg_delivery_time_h, 2)}
          unit="h"
          delta="Per delivery average"
          trend="down"
          icon={<Clock size={20} />}
          accent="amber"
        />
        <KpiCard
          label="Distance Saved"
          value={formatNumber(summary.distance_saved_km, 0)}
          unit="km"
          delta="vs naive single-trip routing"
          trend="up"
          icon={<TrendingDown size={20} />}
          accent="eco"
        />
        <KpiCard
          label="Efficiency Score"
          value={formatNumber(summary.avg_efficiency_score, 1)}
          unit="/100"
          delta="Composite KPI"
          trend="up"
          icon={<BarChart3 size={20} />}
          accent="eco"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <Card>
          <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <Fuel size={16} className="text-eco-400" />
            Daily Fuel Consumption (30d)
          </h3>
          <Plot
            data={[
              {
                x: fuelDates,
                y: fuelValues,
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: '#22c55e', width: 2 },
                marker: { size: 6, color: '#22c55e' },
                fill: 'tozeroy',
                fillcolor: 'rgba(34, 197, 94, 0.12)',
              },
            ] as any}
            layout={{
              paper_bgcolor: 'transparent',
              plot_bgcolor: 'transparent',
              font: { color: '#94a3b8', size: 11 },
              margin: { t: 10, r: 10, b: 30, l: 50 },
              xaxis: { gridcolor: '#1e293b', showgrid: true },
              yaxis: { gridcolor: '#1e293b', showgrid: true, title: 'Litres' },
              height: 280,
            } as any}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: '100%' }}
          />
        </Card>

        <Card>
          <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <Leaf size={16} className="text-eco-400" />
            Daily CO₂ Emissions (30d)
          </h3>
          <Plot
            data={[
              {
                x: fuelDates,
                y: co2Values,
                type: 'bar',
                marker: {
                  color: '#0d9488',
                  line: { color: '#14b8a6', width: 1 },
                },
              },
            ] as any}
            layout={{
              paper_bgcolor: 'transparent',
              plot_bgcolor: 'transparent',
              font: { color: '#94a3b8', size: 11 },
              margin: { t: 10, r: 10, b: 30, l: 50 },
              xaxis: { gridcolor: '#1e293b' },
              yaxis: { gridcolor: '#1e293b', title: 'kg CO₂' },
              height: 280,
            } as any}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: '100%' }}
          />
        </Card>
      </div>

      {/* System info */}
      <div className="panel-recessed p-6 mt-6 border-t border-black/80 border-b border-white/5">
        <h3 className="text-sm font-semibold text-slate-400 mb-4 flex items-center gap-2 drop-shadow-md">
          <Activity size={16} className="text-eco-500 drop-shadow-[0_0_5px_rgba(34,197,94,0.5)]" />
          SYSTEM DIAGNOSTICS
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="bg-panel-900 rounded shadow-lcd p-3 border-t border-black border-b border-white/5">
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">API Status</p>
            <p className="text-eco-400 font-display font-bold mt-1 tracking-wider drop-shadow-[0_0_5px_rgba(74,222,128,0.4)]">{health?.status || 'ok'}</p>
          </div>
          <div className="bg-panel-900 rounded shadow-lcd p-3 border-t border-black border-b border-white/5">
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Version</p>
            <p className="text-slate-300 font-display font-bold mt-1 tracking-wider drop-shadow-md">{health?.version || '1.0.0'}</p>
          </div>
          <div className="bg-panel-900 rounded shadow-lcd p-3 border-t border-black border-b border-white/5">
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">ML Model</p>
            <p className="text-slate-300 font-display font-bold mt-1 uppercase tracking-wider drop-shadow-md">
              {health?.model_name || 'N/A'}
            </p>
          </div>
          <div className="bg-panel-900 rounded shadow-lcd p-3 border-t border-black border-b border-white/5">
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Database</p>
            <div className="flex items-center gap-2 mt-1">
              <div className={health?.database_ready ? "led-indicator text-eco-500 bg-eco-500" : "led-indicator text-red-500 bg-red-500"}></div>
              <p className="text-slate-300 font-display font-bold uppercase tracking-wider drop-shadow-md">
                {health?.database_ready ? 'Connected' : 'Offline'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
