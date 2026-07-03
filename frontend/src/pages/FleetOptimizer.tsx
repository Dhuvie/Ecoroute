import { useEffect, useState } from 'react'
import { Network, Truck, Package, Fuel, Leaf, TrendingDown, Clock } from 'lucide-react'
import { PageHeader, Card, Spinner, Badge, EmptyState } from '../components/ui'
import { api } from '../lib/api'
import { formatNumber, formatCurrency } from '../lib/utils'
import type { Delivery, Vehicle, FleetOptimizationResponse } from '../types'

export default function FleetOptimizer() {
  const [deliveries, setDeliveries] = useState<Delivery[]>([])
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [selectedDeliveries, setSelectedDeliveries] = useState<Set<string>>(new Set())
  const [selectedVehicles, setSelectedVehicles] = useState<Set<string>>(new Set())
  const [maxStops, setMaxStops] = useState(8)
  const [result, setResult] = useState<FleetOptimizationResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [optimizing, setOptimizing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([api.listDeliveries(), api.listVehicles()])
      .then(([d, v]) => {
        setDeliveries(d.filter((x) => x.status === 'pending' || x.status === 'assigned'))
        setVehicles(v.filter((x) => x.is_active))
      })
      .finally(() => setLoading(false))
  }, [])

  const toggle = (set: Set<string>, id: string, setter: (s: Set<string>) => void) => {
    const next = new Set(set)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setter(next)
  }

  const optimize = async () => {
    if (selectedDeliveries.size === 0 || selectedVehicles.size === 0) {
      setError('Select at least 1 delivery and 1 vehicle')
      return
    }
    setOptimizing(true)
    setError(null)
    try {
      const r = await api.optimizeFleet({
        delivery_ids: Array.from(selectedDeliveries),
        vehicle_ids: Array.from(selectedVehicles),
        max_stops_per_vehicle: maxStops,
      })
      setResult(r)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Optimization failed')
    } finally {
      setOptimizing(false)
    }
  }

  if (loading) {
    return (
      <div className="p-8 flex justify-center">
        <Spinner className="w-8 h-8" />
      </div>
    )
  }

  return (
    <div className="p-6 animate-fade-in">
      <PageHeader
        title="Fleet Optimizer"
        subtitle="Assign deliveries to vehicles optimally using the capacitated vehicle routing problem (CVRP) solver"
        actions={
          <button
            onClick={optimize}
            disabled={optimizing}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-eco-500 text-white hover:bg-eco-400 disabled:opacity-50 text-sm font-medium"
          >
            {optimizing ? (
              <>
                <Spinner className="w-4 h-4" />
                Optimizing...
              </>
            ) : (
              <>
                <Network size={16} />
                Optimize Fleet
              </>
            )}
          </button>
        }
      />

      {error && (
        <div className="mb-4 text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg p-3">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        {/* Deliveries */}
        <Card>
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <Package size={16} className="text-eco-400" />
            Deliveries ({selectedDeliveries.size}/{deliveries.length} selected)
          </h3>
          <div className="max-h-80 overflow-y-auto space-y-1.5">
            {deliveries.length === 0 ? (
              <EmptyState message="No pending deliveries" />
            ) : (
              deliveries.map((d) => (
                <label
                  key={d.id}
                  className={`flex items-center gap-3 p-2 rounded-lg cursor-pointer transition-colors ${
                    selectedDeliveries.has(d.id)
                      ? 'bg-eco-500/10 border border-eco-500/30'
                      : 'hover:bg-ink-800/40 border border-transparent'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedDeliveries.has(d.id)}
                    onChange={() =>
                      toggle(selectedDeliveries, d.id, setSelectedDeliveries)
                    }
                    className="accent-eco-500"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-mono text-slate-200">
                        {d.delivery_code}
                      </span>
                      <Badge className="bg-ink-800 text-slate-400 border-ink-700">
                        {d.priority}
                      </Badge>
                    </div>
                    <div className="text-xs text-slate-500 mt-0.5">
                      {formatNumber(d.package_weight_kg, 0)} kg • {formatNumber(d.distance_km || 0, 0)} km
                    </div>
                  </div>
                </label>
              ))
            )}
          </div>
        </Card>

        {/* Vehicles */}
        <Card>
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <Truck size={16} className="text-eco-400" />
            Vehicles ({selectedVehicles.size}/{vehicles.length} selected)
          </h3>
          <div className="mb-3">
            <label className="text-xs text-slate-400 uppercase tracking-wider">
              Max stops per vehicle: {maxStops}
            </label>
            <input
              type="range"
              min="1"
              max="20"
              value={maxStops}
              onChange={(e) => setMaxStops(parseInt(e.target.value))}
              className="w-full accent-eco-500 mt-1"
            />
          </div>
          <div className="max-h-72 overflow-y-auto space-y-1.5">
            {vehicles.map((v) => (
              <label
                key={v.id}
                className={`flex items-center gap-3 p-2 rounded-lg cursor-pointer transition-colors ${
                  selectedVehicles.has(v.id)
                    ? 'bg-eco-500/10 border border-eco-500/30'
                    : 'hover:bg-ink-800/40 border border-transparent'
                }`}
              >
                <input
                  type="checkbox"
                  checked={selectedVehicles.has(v.id)}
                  onChange={() =>
                    toggle(selectedVehicles, v.id, setSelectedVehicles)
                  }
                  className="accent-eco-500"
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-mono text-slate-200">
                      {v.vehicle_id}
                    </span>
                    <Badge className="bg-ink-800 text-slate-400 border-ink-700">
                      {v.vehicle_type}
                    </Badge>
                  </div>
                  <div className="text-xs text-slate-500 mt-0.5">
                    Cap: {formatNumber(v.load_capacity_kg, 0)} kg • {formatNumber(v.base_mileage_kmpl, 1)} km/L
                  </div>
                </div>
              </label>
            ))}
          </div>
        </Card>
      </div>

      {/* Results */}
      {result && (
        <div className="animate-fade-in">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <Card>
              <div className="flex items-center gap-2 text-eco-400 mb-2">
                <TrendingDown size={16} />
                <span className="text-xs uppercase text-slate-500">Fuel Saved</span>
              </div>
              <p className="text-2xl font-bold text-white">
                {formatNumber(result.estimated_fuel_saved_pct, 1)}%
              </p>
            </Card>
            <Card>
              <div className="flex items-center gap-2 text-amber-400 mb-2">
                <Fuel size={16} />
                <span className="text-xs uppercase text-slate-500">Total Fuel</span>
              </div>
              <p className="text-2xl font-bold text-white">
                {formatNumber(result.total_fuel_l, 1)} L
              </p>
            </Card>
            <Card>
              <div className="flex items-center gap-2 text-eco-400 mb-2">
                <Leaf size={16} />
                <span className="text-xs uppercase text-slate-500">CO₂</span>
              </div>
              <p className="text-2xl font-bold text-white">
                {formatNumber(result.total_co2_kg, 1)} kg
              </p>
            </Card>
            <Card>
              <div className="flex items-center gap-2 text-blue-400 mb-2">
                <Network size={16} />
                <span className="text-xs uppercase text-slate-500">Total Cost</span>
              </div>
              <p className="text-2xl font-bold text-white">
                {formatCurrency(result.total_cost_inr)}
              </p>
            </Card>
          </div>

          <Card>
            <h3 className="text-sm font-semibold text-white mb-4">
              Assignments ({result.assignments.length}) • Algorithm: {result.algorithm}
            </h3>
            <div className="space-y-3">
              {result.assignments.map((a, i) => {
                const v = vehicles.find((x) => x.id === a.vehicle_id)
                return (
                  <div
                    key={i}
                    className="rounded-lg border border-ink-800 bg-ink-800/30 p-4"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="p-2 rounded bg-eco-500/15 text-eco-300">
                          <Truck size={16} />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-white">
                            {v?.vehicle_id || a.vehicle_id.slice(0, 8)}
                          </p>
                          <p className="text-xs text-slate-500">
                            {v?.vehicle_type} • {v?.fuel_type}
                          </p>
                        </div>
                      </div>
                      <Badge className="bg-eco-500/15 text-eco-300 border-eco-500/30">
                        {a.delivery_codes.length} stops
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm mt-3">
                      <div>
                        <p className="text-[10px] text-slate-500 uppercase">Distance</p>
                        <p className="text-slate-200">{formatNumber(a.total_distance_km, 1)} km</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-slate-500 uppercase">Fuel</p>
                        <p className="text-slate-200">{formatNumber(a.total_fuel_l, 2)} L</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-slate-500 uppercase">CO₂</p>
                        <p className="text-slate-200">{formatNumber(a.total_co2_kg, 2)} kg</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-slate-500 uppercase">Time</p>
                        <p className="text-slate-200">{formatNumber(a.total_time_h, 2)} h</p>
                      </div>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-1">
                      {a.delivery_codes.map((code, j) => (
                        <span
                          key={j}
                          className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-ink-900 text-slate-400"
                        >
                          {j + 1}. {code}
                        </span>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
