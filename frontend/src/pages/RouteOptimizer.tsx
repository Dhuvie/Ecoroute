import { useState } from 'react'
import { Route, Fuel, Clock, Leaf, Navigation, CloudRain } from 'lucide-react'
import { PageHeader, Card, Spinner, Badge } from '../components/ui'
import { api } from '../lib/api'
import { formatNumber, formatCurrency } from '../lib/utils'
import RouteMap from '../components/RouteMap'
import type { RouteResponse } from '../types'

const CITY_PRESETS: Record<string, { lat: number; lon: number; name: string }> = {
  mumbai: { lat: 19.076, lon: 72.877, name: 'Mumbai' },
  delhi: { lat: 28.704, lon: 77.102, name: 'Delhi' },
  bangalore: { lat: 12.971, lon: 77.594, name: 'Bangalore' },
  hyderabad: { lat: 17.385, lon: 78.486, name: 'Hyderabad' },
  chennai: { lat: 13.082, lon: 80.270, name: 'Chennai' },
  pune: { lat: 18.52, lon: 73.856, name: 'Pune' },
  kolkata: { lat: 22.572, lon: 88.363, name: 'Kolkata' },
}

export default function RouteOptimizer() {
  const [origin, setOrigin] = useState(CITY_PRESETS.mumbai)
  const [destination, setDestination] = useState(CITY_PRESETS.pune)
  const [vehicleType, setVehicleType] = useState('truck')
  const [fuelType, setFuelType] = useState('diesel')
  const [algorithm, setAlgorithm] = useState('astar')
  const [result, setResult] = useState<RouteResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const optimize = async () => {
    setLoading(true)
    setError(null)
    try {
      const r = await api.optimizeRoute({
        origin_lat: origin.lat,
        origin_lon: origin.lon,
        destination_lat: destination.lat,
        destination_lon: destination.lon,
        vehicle_type: vehicleType,
        fuel_type: fuelType,
        algorithm,
      })
      setResult(r)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Optimization failed')
    } finally {
      setLoading(false)
    }
  }

  const path = result?.path || []
  const trafficColor =
    result?.traffic_level === 'low'
      ? 'eco'
      : result?.traffic_level === 'medium'
      ? 'amber'
      : 'red'

  return (
    <div className="p-6 animate-fade-in">
      <PageHeader
        title="Route Optimizer"
        subtitle="Compute the optimal delivery route minimizing fuel, distance, and time using Dijkstra, A*, or OR-Tools"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Configuration */}
        <Card className="lg:col-span-1">
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <Navigation size={16} className="text-eco-400" />
            Trip Configuration
          </h3>

          <div className="space-y-4">
            <div>
              <label className="text-xs text-slate-400 uppercase tracking-wider">Origin</label>
              <select
                value={Object.keys(CITY_PRESETS).find(
                  (k) =>
                    CITY_PRESETS[k].lat === origin.lat &&
                    CITY_PRESETS[k].lon === origin.lon,
                )}
                onChange={(e) => setOrigin(CITY_PRESETS[e.target.value])}
                className="input"
              >
                {Object.entries(CITY_PRESETS).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs text-slate-400 uppercase tracking-wider">
                Destination
              </label>
              <select
                value={Object.keys(CITY_PRESETS).find(
                  (k) =>
                    CITY_PRESETS[k].lat === destination.lat &&
                    CITY_PRESETS[k].lon === destination.lon,
                )}
                onChange={(e) => setDestination(CITY_PRESETS[e.target.value])}
                className="input"
              >
                {Object.entries(CITY_PRESETS).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-400 uppercase tracking-wider">
                  Vehicle
                </label>
                <select
                  value={vehicleType}
                  onChange={(e) => setVehicleType(e.target.value)}
                  className="input"
                >
                  <option value="motorcycle">Motorcycle</option>
                  <option value="van">Van</option>
                  <option value="mini_truck">Mini Truck</option>
                  <option value="truck">Truck</option>
                  <option value="semi_truck">Semi Truck</option>
                  <option value="refrigerated_truck">Refrigerated</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-400 uppercase tracking-wider">Fuel</label>
                <select
                  value={fuelType}
                  onChange={(e) => setFuelType(e.target.value)}
                  className="input"
                >
                  <option value="diesel">Diesel</option>
                  <option value="petrol">Petrol</option>
                  <option value="electric">Electric</option>
                  <option value="cng">CNG</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-400 uppercase tracking-wider">
                Algorithm
              </label>
              <select
                value={algorithm}
                onChange={(e) => setAlgorithm(e.target.value)}
                className="input"
              >
                <option value="dijkstra">Dijkstra</option>
                <option value="astar">A* Search</option>
                <option value="ortools">OR-Tools VRP</option>
              </select>
            </div>

            <button
              onClick={optimize}
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-eco-500 text-white hover:bg-eco-400 disabled:opacity-50 transition-colors font-medium text-sm flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Spinner className="w-4 h-4" />
                  Optimizing...
                </>
              ) : (
                <>
                  <Route size={16} />
                  Optimize Route
                </>
              )}
            </button>

            {error && (
              <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded p-2">
                {error}
              </div>
            )}
          </div>
        </Card>

        {/* Map */}
        <Card className="lg:col-span-2">
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <Route size={16} className="text-eco-400" />
            Optimized Route
            {result && (
              <Badge
                className={`bg-${trafficColor}-500/15 text-${trafficColor}-300 border-${trafficColor}-500/30 ml-auto`}
              >
                Traffic: {result.traffic_level}
              </Badge>
            )}
          </h3>
          <RouteMap
            path={path}
            origin={[origin.lat, origin.lon]}
            destination={[destination.lat, destination.lon]}
            height="450px"
          />
        </Card>
      </div>

      {/* Results */}
      {result && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mt-4 animate-fade-in">
          <ResultCard
            icon={<Route size={18} />}
            label="Distance"
            value={formatNumber(result.distance_km, 1)}
            unit="km"
            accent="blue"
          />
          <ResultCard
            icon={<Fuel size={18} />}
            label="Fuel Used"
            value={formatNumber(result.estimated_fuel_l, 2)}
            unit="L"
            accent="amber"
          />
          <ResultCard
            icon={<Leaf size={18} />}
            label="CO₂ Emission"
            value={formatNumber(result.estimated_co2_kg, 2)}
            unit="kg"
            accent="eco"
          />
          <ResultCard
            icon={<Clock size={18} />}
            label="Travel Time"
            value={formatNumber(result.estimated_time_h, 2)}
            unit="h"
            accent="purple"
          />
          <ResultCard
            icon={<CloudRain size={18} />}
            label="Total Cost"
            value={formatCurrency(result.estimated_cost_inr)}
            accent="eco"
          />
        </div>
      )}

      <style>{`
        .input {
          width: 100%;
          background: #0f172a;
          border: 1px solid #1e293b;
          border-radius: 0.5rem;
          padding: 0.5rem 0.75rem;
          color: #e2e8f0;
          font-size: 0.875rem;
        }
        .input:focus {
          outline: none;
          border-color: #22c55e;
        }
      `}</style>
    </div>
  )
}

function ResultCard({
  icon,
  label,
  value,
  unit,
  accent,
}: {
  icon: React.ReactNode
  label: string
  value: string
  unit?: string
  accent: 'eco' | 'blue' | 'amber' | 'red' | 'purple'
}) {
  const accentClasses = {
    eco: 'text-eco-400 bg-eco-500/10',
    blue: 'text-blue-400 bg-blue-500/10',
    amber: 'text-amber-400 bg-amber-500/10',
    red: 'text-red-400 bg-red-500/10',
    purple: 'text-purple-400 bg-purple-500/10',
  }
  return (
    <Card>
      <div className="p-2.5 rounded-lg w-fit" style={{ background: accentClasses[accent].split(' ')[1], color: accentClasses[accent].split(' ')[0] }}>
        {icon}
      </div>
      <p className="text-xs text-slate-500 uppercase tracking-wider mt-3">{label}</p>
      <div className="flex items-baseline gap-1 mt-1">
        <span className="text-xl font-bold text-white">{value}</span>
        {unit && <span className="text-sm text-slate-400">{unit}</span>}
      </div>
    </Card>
  )
}
