import { useEffect, useState } from 'react'
import { Package, Plus, MapPin, Weight, Clock } from 'lucide-react'
import { PageHeader, Card, Spinner, Badge, EmptyState } from '../components/ui'
import { api } from '../lib/api'
import {
  formatNumber,
  PRIORITY_COLORS,
  STATUS_COLORS,
  VEHICLE_TYPE_LABELS,
} from '../lib/utils'
import type { Delivery } from '../types'

export default function Deliveries() {
  const [deliveries, setDeliveries] = useState<Delivery[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')

  const load = () => {
    setLoading(true)
    api.listDeliveries().then(setDeliveries).finally(() => setLoading(false))
  }

  useEffect(() => load(), [])

  const filtered =
    filter === 'all' ? deliveries : deliveries.filter((d) => d.status === filter)

  const stats = {
    total: deliveries.length,
    pending: deliveries.filter((d) => d.status === 'pending').length,
    assigned: deliveries.filter((d) => d.status === 'assigned').length,
    delivered: deliveries.filter((d) => d.status === 'delivered').length,
  }

  return (
    <div className="p-6 animate-fade-in">
      <PageHeader
        title="Deliveries"
        subtitle="View and manage all delivery orders across the network"
        actions={
          <button className="flex items-center gap-2 px-4 py-2 rounded btn-skeuo font-bold uppercase tracking-wider text-[10px]">
            <Plus size={14} className="drop-shadow-md" />
            New Delivery
          </button>
        }
      />

      {/* Status stats */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        {[
          { label: 'Total', value: stats.total, color: 'text-slate-200' },
          { label: 'Pending', value: stats.pending, color: 'text-slate-400' },
          { label: 'Assigned', value: stats.assigned, color: 'text-blue-400' },
          { label: 'Delivered', value: stats.delivered, color: 'text-eco-400' },
        ].map((s) => (
          <Card key={s.label}>
            <p className="text-xs uppercase text-slate-500 tracking-wider">{s.label}</p>
            <p className={`text-2xl font-bold mt-1 ${s.color}`}>{formatNumber(s.value)}</p>
          </Card>
        ))}
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-4">
        {['all', 'pending', 'assigned', 'in_transit', 'delivered'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded font-bold uppercase tracking-wider text-[10px] transition-colors ${
              filter === f
                ? 'bg-panel-800 text-eco-400 shadow-recessed border-t border-black/80 border-b border-white/5 drop-shadow-[0_0_5px_rgba(74,222,128,0.3)]'
                : 'btn-skeuo text-slate-400'
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner className="w-8 h-8" />
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState message="No deliveries found" />
      ) : (
        <Card className="overflow-hidden p-0 bg-panel-900 shadow-recessed border-none">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-black/80 bg-panel-800 text-[10px] font-bold uppercase text-slate-500 tracking-wider drop-shadow-md shadow-[0_1px_0_rgba(255,255,255,0.05)]">
                  <th className="text-left px-4 py-3">Code</th>
                  <th className="text-left px-4 py-3">Priority</th>
                  <th className="text-left px-4 py-3">Status</th>
                  <th className="text-right px-4 py-3">Weight</th>
                  <th className="text-right px-4 py-3">Distance</th>
                  <th className="text-right px-4 py-3">Fuel (est.)</th>
                  <th className="text-right px-4 py-3">CO₂ (est.)</th>
                  <th className="text-right px-4 py-3">Time (est.)</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((d) => (
                  <tr
                    key={d.id}
                    className="border-b border-black/40 hover:bg-black/20"
                  >
                    <td className="px-4 py-3">
                      <div className="font-mono text-slate-200 text-xs">{d.delivery_code}</div>
                      <div className="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
                        <MapPin size={10} />
                        {d.destination_lat.toFixed(2)}, {d.destination_lon.toFixed(2)}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Badge className={PRIORITY_COLORS[d.priority]}>{d.priority}</Badge>
                    </td>
                    <td className="px-4 py-3">
                      <Badge className={STATUS_COLORS[d.status]}>{d.status}</Badge>
                    </td>
                    <td className="px-4 py-3 text-right text-slate-300">
                      <div className="flex items-center justify-end gap-1">
                        <Weight size={12} className="text-slate-500" />
                        {formatNumber(d.package_weight_kg, 0)} kg
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right text-slate-300">
                      {d.distance_km ? `${formatNumber(d.distance_km, 0)} km` : '—'}
                    </td>
                    <td className="px-4 py-3 text-right text-amber-300">
                      {d.estimated_fuel_l ? `${formatNumber(d.estimated_fuel_l, 1)} L` : '—'}
                    </td>
                    <td className="px-4 py-3 text-right text-eco-300">
                      {d.estimated_co2_kg ? `${formatNumber(d.estimated_co2_kg, 1)} kg` : '—'}
                    </td>
                    <td className="px-4 py-3 text-right text-slate-300">
                      <div className="flex items-center justify-end gap-1">
                        <Clock size={12} className="text-slate-500" />
                        {d.estimated_time_h ? `${formatNumber(d.estimated_time_h, 1)} h` : '—'}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}
