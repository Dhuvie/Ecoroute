import { useEffect, useState } from 'react'
import { Truck, Plus, Trash2, Fuel, Gauge, Weight } from 'lucide-react'
import { PageHeader, Card, Spinner, Badge, EmptyState } from '../components/ui'
import { api } from '../lib/api'
import { formatNumber, VEHICLE_TYPE_LABELS, FUEL_TYPE_LABELS } from '../lib/utils'
import type { Vehicle } from '../types'

const FUEL_BADGE: Record<string, string> = {
  diesel: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  petrol: 'bg-red-500/15 text-red-300 border-red-500/30',
  electric: 'bg-blue-500/15 text-blue-300 border-blue-500/30',
  cng: 'bg-purple-500/15 text-purple-300 border-purple-500/30',
  hybrid: 'bg-eco-500/15 text-eco-300 border-eco-500/30',
}

export default function Vehicles() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)

  const load = () => {
    setLoading(true)
    api.listVehicles().then(setVehicles).finally(() => setLoading(false))
  }

  useEffect(() => load(), [])

  const handleDelete = async (id: string) => {
    if (!confirm('Deactivate this vehicle?')) return
    try {
      await api.deleteVehicle(id)
      load()
    } catch (e) {
      alert('Failed to delete vehicle')
    }
  }

  return (
    <div className="p-6 animate-fade-in">
      <PageHeader
        title="Vehicle Management"
        subtitle="Fleet catalogue with fuel efficiency, capacity and maintenance metrics"
        actions={
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-eco-500/15 text-eco-300 hover:bg-eco-500/25 transition-colors text-sm font-medium border border-eco-500/30"
          >
            <Plus size={16} />
            Add Vehicle
          </button>
        }
      />

      {showForm && <AddVehicleForm onCreated={() => { setShowForm(false); load() }} />}

      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner className="w-8 h-8" />
        </div>
      ) : vehicles.length === 0 ? (
        <EmptyState message="No vehicles yet. Add your first vehicle to get started." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {vehicles.map((v) => (
            <Card key={v.id}>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-eco-500/10 text-eco-400">
                    <Truck size={20} />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold">{v.vehicle_id}</h3>
                    <p className="text-xs text-slate-400">
                      {VEHICLE_TYPE_LABELS[v.vehicle_type] || v.vehicle_type}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(v.id)}
                  className="text-slate-500 hover:text-red-400 transition-colors p-1"
                  title="Deactivate"
                >
                  <Trash2 size={14} />
                </button>
              </div>

              <div className="flex flex-wrap gap-1.5 mb-4">
                <Badge className={FUEL_BADGE[v.fuel_type] || 'bg-ink-800 text-slate-300'}>
                  {FUEL_TYPE_LABELS[v.fuel_type] || v.fuel_type}
                </Badge>
                {v.is_active ? (
                  <Badge className="bg-eco-500/15 text-eco-300 border-eco-500/30">
                    Active
                  </Badge>
                ) : (
                  <Badge className="bg-slate-700/30 text-slate-400 border-slate-600/30">
                    Inactive
                  </Badge>
                )}
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <Stat
                  icon={<Fuel size={13} />}
                  label="Mileage"
                  value={`${formatNumber(v.base_mileage_kmpl, 1)} km/L`}
                />
                <Stat
                  icon={<Gauge size={13} />}
                  label="Avg Speed"
                  value={`${formatNumber(v.avg_speed_kmph, 0)} km/h`}
                />
                <Stat
                  icon={<Weight size={13} />}
                  label="Capacity"
                  value={`${formatNumber(v.load_capacity_kg, 0)} kg`}
                />
                <Stat
                  icon={<Truck size={13} />}
                  label="Kerb Wt"
                  value={`${formatNumber(v.kerb_weight_kg, 0)} kg`}
                />
              </div>

              <div className="mt-4 pt-3 border-t border-ink-800">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500">Maintenance Score</span>
                  <span className="text-slate-300 font-medium">
                    {formatNumber(v.maintenance_score * 100, 0)}%
                  </span>
                </div>
                <div className="mt-1.5 w-full h-1.5 rounded-full bg-ink-800 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-eco-500 to-eco-400 rounded-full"
                    style={{ width: `${v.maintenance_score * 100}%` }}
                  />
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

function Stat({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="flex items-center gap-2">
      <div className="text-slate-500">{icon}</div>
      <div>
        <p className="text-[10px] text-slate-500 uppercase tracking-wider">{label}</p>
        <p className="text-slate-200 font-medium">{value}</p>
      </div>
    </div>
  )
}

function AddVehicleForm({ onCreated }: { onCreated: () => void }) {
  const [form, setForm] = useState({
    vehicle_id: '',
    vehicle_type: 'truck',
    fuel_type: 'diesel',
    base_mileage_kmpl: 5.5,
    kerb_weight_kg: 8000,
    load_capacity_kg: 8000,
    avg_speed_kmph: 60,
    maintenance_score: 0.8,
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await api.createVehicle(form)
      onCreated()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to create vehicle')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Card className="mb-6">
      <h3 className="text-sm font-semibold text-white mb-4">Add New Vehicle</h3>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <Field label="Vehicle ID">
          <input
            required
            value={form.vehicle_id}
            onChange={(e) => setForm({ ...form, vehicle_id: e.target.value })}
            placeholder="V0013"
            className="input"
          />
        </Field>
        <Field label="Vehicle Type">
          <select
            value={form.vehicle_type}
            onChange={(e) => setForm({ ...form, vehicle_type: e.target.value })}
            className="input"
          >
            {Object.entries(VEHICLE_TYPE_LABELS).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Fuel Type">
          <select
            value={form.fuel_type}
            onChange={(e) => setForm({ ...form, fuel_type: e.target.value })}
            className="input"
          >
            {Object.entries(FUEL_TYPE_LABELS).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Mileage (km/L)">
          <input
            type="number"
            step="0.1"
            value={form.base_mileage_kmpl}
            onChange={(e) =>
              setForm({ ...form, base_mileage_kmpl: parseFloat(e.target.value) })
            }
            className="input"
          />
        </Field>
        <Field label="Kerb Weight (kg)">
          <input
            type="number"
            value={form.kerb_weight_kg}
            onChange={(e) =>
              setForm({ ...form, kerb_weight_kg: parseFloat(e.target.value) })
            }
            className="input"
          />
        </Field>
        <Field label="Capacity (kg)">
          <input
            type="number"
            value={form.load_capacity_kg}
            onChange={(e) =>
              setForm({ ...form, load_capacity_kg: parseFloat(e.target.value) })
            }
            className="input"
          />
        </Field>
        <Field label="Avg Speed (km/h)">
          <input
            type="number"
            value={form.avg_speed_kmph}
            onChange={(e) =>
              setForm({ ...form, avg_speed_kmph: parseFloat(e.target.value) })
            }
            className="input"
          />
        </Field>
        <Field label="Maintenance (0-1)">
          <input
            type="number"
            step="0.05"
            min="0"
            max="1"
            value={form.maintenance_score}
            onChange={(e) =>
              setForm({ ...form, maintenance_score: parseFloat(e.target.value) })
            }
            className="input"
          />
        </Field>
        {error && (
          <div className="md:col-span-4 text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded p-2">
            {error}
          </div>
        )}
        <div className="md:col-span-4 flex justify-end gap-2">
          <button
            type="button"
            onClick={onCreated}
            className="px-4 py-2 rounded-lg text-slate-300 hover:text-white text-sm"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="px-4 py-2 rounded-lg bg-eco-500 text-white hover:bg-eco-400 disabled:opacity-50 text-sm font-medium"
          >
            {submitting ? 'Saving...' : 'Save Vehicle'}
          </button>
        </div>
      </form>
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
    </Card>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="text-xs text-slate-400 uppercase tracking-wider">{label}</span>
      <div className="mt-1">{children}</div>
    </label>
  )
}
