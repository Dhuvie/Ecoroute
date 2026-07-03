import { ReactNode } from 'react'
import clsx from 'clsx'

interface CardProps {
  children: ReactNode
  className?: string
  glow?: boolean
}

export function Card({ children, className, glow = true }: CardProps) {
  return (
    <div
      className={clsx(
        'rounded-xl border border-ink-800 bg-ink-900/40 backdrop-blur-sm p-5',
        glow && 'card-glow',
        className,
      )}
    >
      {children}
    </div>
  )
}

interface KpiCardProps {
  label: string
  value: string | number
  unit?: string
  delta?: string
  trend?: 'up' | 'down' | 'neutral'
  icon?: ReactNode
  accent?: 'eco' | 'blue' | 'amber' | 'red' | 'purple'
}

export function KpiCard({
  label,
  value,
  unit,
  delta,
  trend = 'neutral',
  icon,
  accent = 'eco',
}: KpiCardProps) {
  const accentClasses = {
    eco: 'text-eco-400 bg-eco-500/10',
    blue: 'text-blue-400 bg-blue-500/10',
    amber: 'text-amber-400 bg-amber-500/10',
    red: 'text-red-400 bg-red-500/10',
    purple: 'text-purple-400 bg-purple-500/10',
  }
  const trendColor =
    trend === 'up' ? 'text-eco-400' : trend === 'down' ? 'text-red-400' : 'text-slate-400'

  return (
    <Card className="relative overflow-hidden">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-slate-500 font-medium">
            {label}
          </p>
          <div className="mt-2 flex items-baseline gap-1">
            <span className="text-2xl font-bold text-white count-up">{value}</span>
            {unit && <span className="text-sm text-slate-400">{unit}</span>}
          </div>
          {delta && (
            <p className={clsx('mt-1 text-xs font-medium', trendColor)}>{delta}</p>
          )}
        </div>
        {icon && (
          <div className={clsx('p-2.5 rounded-lg', accentClasses[accent])}>{icon}</div>
        )}
      </div>
    </Card>
  )
}

export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string
  subtitle?: string
  actions?: ReactNode
}) {
  return (
    <div className="flex items-start justify-between mb-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">{title}</h1>
        {subtitle && <p className="text-sm text-slate-400 mt-1">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  )
}

export function Badge({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border',
        className || 'bg-ink-800 text-slate-300 border-ink-700',
      )}
    >
      {children}
    </span>
  )
}

export function Spinner({ className }: { className?: string }) {
  return (
    <div
      className={clsx(
        'w-6 h-6 border-2 border-eco-500/30 border-t-eco-400 rounded-full animate-spin',
        className,
      )}
    />
  )
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-slate-500">
      <div className="w-12 h-12 rounded-full bg-ink-800/50 flex items-center justify-center mb-3">
        <span className="text-2xl">∅</span>
      </div>
      <p className="text-sm">{message}</p>
    </div>
  )
}
