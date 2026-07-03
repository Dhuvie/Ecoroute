/**
 * Shared UI helper functions.
 */

export function formatNumber(n: number, digits: number = 0): string {
  if (n === null || n === undefined || isNaN(n)) return '—'
  return new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(n)
}

export function formatCurrency(n: number): string {
  if (n === null || n === undefined || isNaN(n)) return '—'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(n)
}

export function formatCompact(n: number): string {
  if (n === null || n === undefined || isNaN(n)) return '—'
  return new Intl.NumberFormat('en-IN', {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(n)
}

export function classNames(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(' ')
}

export const VEHICLE_TYPE_LABELS: Record<string, string> = {
  motorcycle: 'Motorcycle',
  van: 'Van',
  mini_truck: 'Mini Truck',
  truck: 'Truck',
  semi_truck: 'Semi Truck',
  refrigerated_truck: 'Refrigerated Truck',
}

export const FUEL_TYPE_LABELS: Record<string, string> = {
  diesel: 'Diesel',
  petrol: 'Petrol',
  electric: 'Electric',
  cng: 'CNG',
  hybrid: 'Hybrid',
}

export const PRIORITY_COLORS: Record<string, string> = {
  low: 'bg-slate-500/15 text-slate-300 border-slate-500/30',
  medium: 'bg-blue-500/15 text-blue-300 border-blue-500/30',
  high: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  critical: 'bg-red-500/15 text-red-300 border-red-500/30',
}

export const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-slate-500/15 text-slate-300 border-slate-500/30',
  assigned: 'bg-blue-500/15 text-blue-300 border-blue-500/30',
  in_transit: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  delivered: 'bg-eco-500/15 text-eco-300 border-eco-500/30',
  failed: 'bg-red-500/15 text-red-300 border-red-500/30',
  cancelled: 'bg-slate-700/30 text-slate-400 border-slate-600/30',
}
