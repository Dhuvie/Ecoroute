import { useEffect, useState } from 'react'
import Plot from 'react-plotly.js'
import { BarChart3, TrendingUp, Truck, Leaf } from 'lucide-react'
import { PageHeader, Card, Spinner } from '../components/ui'
import { api } from '../lib/api'
import { formatNumber, formatCurrency } from '../lib/utils'
import type { AnalyticsSummary, TimeSeriesResponse } from '../types'

export default function Analytics() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [fuelSeries, setFuelSeries] = useState<TimeSeriesResponse | null>(null)
  const [distanceSeries, setDistanceSeries] = useState<TimeSeriesResponse | null>(null)
  const [deliverySeries, setDeliverySeries] = useState<TimeSeriesResponse | null>(null)
  const [vehicleUtil, setVehicleUtil] = useState<Record<string, unknown>[]>([])
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState('all')

  useEffect(() => {
    setLoading(true)
    Promise.all([
      api.analyticsSummary(period),
      api.analyticsTimeseries('fuel', 30),
      api.analyticsTimeseries('distance', 30),
      api.analyticsTimeseries('deliveries', 30),
      api.vehicleUtilization(30),
    ])
      .then(([s, f, d, del, v]) => {
        setSummary(s)
        setFuelSeries(f)
        setDistanceSeries(d)
        setDeliverySeries(del)
        setVehicleUtil(v)
      })
      .finally(() => setLoading(false))
  }, [period])

  if (loading || !summary) {
    return (
      <div className="p-8 flex justify-center">
        <Spinner className="w-8 h-8" />
      </div>
    )
  }

  const dates = fuelSeries?.points.map((p) => p.timestamp.slice(0, 10)) || []

  return (
    <div className="p-6 animate-fade-in">
      <PageHeader
        title="Analytics"
        subtitle="Comprehensive analytics dashboard with KPIs, trends and reports"
        actions={
          <div className="flex gap-2">
            {['daily', 'weekly', 'monthly', 'all'].map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-4 py-2 rounded uppercase tracking-wider text-[10px] font-bold transition-colors ${
                  period === p
                    ? 'bg-panel-800 text-eco-400 shadow-recessed border-t border-black/80 border-b border-white/5 drop-shadow-[0_0_5px_rgba(74,222,128,0.3)]'
                    : 'btn-skeuo text-slate-400'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        }
      />

      {/* Summary KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <div className="flex items-center gap-2 text-eco-400 mb-2">
            <TrendingUp size={16} />
            <span className="text-xs uppercase text-slate-500">Total Deliveries</span>
          </div>
          <p className="text-2xl font-bold text-white">
            {formatNumber(summary.total_deliveries)}
          </p>
          <p className="text-xs text-slate-500 mt-1">
            {formatNumber(summary.total_distance_km, 0)} km total
          </p>
        </Card>
        <Card>
          <div className="flex items-center gap-2 text-amber-400 mb-2">
            <BarChart3 size={16} />
            <span className="text-xs uppercase text-slate-500">Total Fuel</span>
          </div>
          <p className="text-2xl font-bold text-white">
            {formatNumber(summary.total_fuel_l, 0)} L
          </p>
          <p className="text-xs text-eco-400 mt-1">
            {formatNumber(summary.fuel_saved_l, 0)} L saved
          </p>
        </Card>
        <Card>
          <div className="flex items-center gap-2 text-eco-400 mb-2">
            <Leaf size={16} />
            <span className="text-xs uppercase text-slate-500">CO₂ Emissions</span>
          </div>
          <p className="text-2xl font-bold text-white">
            {formatNumber(summary.total_co2_kg, 0)} kg
          </p>
          <p className="text-xs text-eco-400 mt-1">
            {formatNumber(summary.co2_saved_kg, 0)} kg saved
          </p>
        </Card>
        <Card>
          <div className="flex items-center gap-2 text-purple-400 mb-2">
            <Truck size={16} />
            <span className="text-xs uppercase text-slate-500">Cost Savings</span>
          </div>
          <p className="text-2xl font-bold text-white">
            {formatCurrency(summary.cost_saved_inr)}
          </p>
          <p className="text-xs text-slate-500 mt-1">
            {formatNumber(summary.vehicle_utilization_pct, 1)}% utilization
          </p>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <Card>
          <h3 className="text-sm font-semibold text-slate-200 mb-4">
            Fuel vs Distance Trend
          </h3>
          <Plot
            data={[
              {
                x: dates,
                y: fuelSeries?.points.map((p) => p.value) || [],
                type: 'scatter',
                mode: 'lines',
                name: 'Fuel (L)',
                line: { color: '#f59e0b', width: 2 },
                yaxis: 'y',
              },
              {
                x: dates,
                y: distanceSeries?.points.map((p) => p.value) || [],
                type: 'scatter',
                mode: 'lines',
                name: 'Distance (km)',
                line: { color: '#22c55e', width: 2 },
                yaxis: 'y2',
              },
            ] as any}
            layout={{
              paper_bgcolor: 'transparent',
              plot_bgcolor: 'transparent',
              font: { color: '#94a3b8', size: 11 },
              margin: { t: 10, r: 50, b: 30, l: 50 },
              xaxis: { gridcolor: '#1e293b' },
              yaxis: { gridcolor: '#1e293b', title: 'Fuel (L)', side: 'left' },
              yaxis2: {
                gridcolor: '#1e293b',
                title: 'Distance (km)',
                side: 'right',
                overlaying: 'y',
              },
              legend: { x: 0, y: 1.15, orientation: 'h' },
              height: 320,
            } as any}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: '100%' }}
          />
        </Card>

        <Card>
          <h3 className="text-sm font-semibold text-slate-200 mb-4">
            Daily Deliveries Volume
          </h3>
          <Plot
            data={[
              {
                x: dates,
                y: deliverySeries?.points.map((p) => p.value) || [],
                type: 'bar',
                marker: {
                  color: '#0ea5e9',
                  line: { color: '#0284c7', width: 1 },
                },
              },
            ] as any}
            layout={{
              paper_bgcolor: 'transparent',
              plot_bgcolor: 'transparent',
              font: { color: '#94a3b8', size: 11 },
              margin: { t: 10, r: 10, b: 30, l: 50 },
              xaxis: { gridcolor: '#1e293b' },
              yaxis: { gridcolor: '#1e293b', title: 'Deliveries' },
              height: 320,
            } as any}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: '100%' }}
          />
        </Card>
      </div>

      {/* Vehicle utilization */}
      <Card>
        <h3 className="text-sm font-semibold text-slate-200 mb-4">
          Vehicle Utilization (top 10)
        </h3>
        {vehicleUtil.length === 0 ? (
          <p className="text-sm text-slate-500 py-6 text-center">No utilization data yet</p>
        ) : (
          <Plot
            data={[
              {
                x: vehicleUtil.slice(0, 10).map((v) => v.vehicle_id as string),
                y: vehicleUtil.slice(0, 10).map((v) => v.distance_km as number),
                type: 'bar',
                name: 'Distance (km)',
                marker: { color: '#22c55e' },
              },
              {
                x: vehicleUtil.slice(0, 10).map((v) => v.vehicle_id as string),
                y: vehicleUtil.slice(0, 10).map((v) => v.fuel_used_l as number),
                type: 'bar',
                name: 'Fuel (L)',
                marker: { color: '#f59e0b' },
              },
            ] as any}
            layout={{
              paper_bgcolor: 'transparent',
              plot_bgcolor: 'transparent',
              font: { color: '#94a3b8', size: 11 },
              margin: { t: 20, r: 10, b: 50, l: 50 },
              xaxis: { gridcolor: '#1e293b', tickangle: -45 },
              yaxis: { gridcolor: '#1e293b' },
              barmode: 'group',
              legend: { x: 0, y: 1.15, orientation: 'h' },
              height: 320,
            } as any}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: '100%' }}
          />
        )}
      </Card>
    </div>
  )
}
