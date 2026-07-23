import { ReactNode } from 'react'
import clsx from 'clsx'

interface CardProps {
  children: ReactNode
  className?: string
  glow?: boolean
}

export function Card({ children, className, glow = false }: CardProps) {
  return (
    <div
      className={clsx(
        'panel-skeuo p-5',
        glow && 'shadow-[inset_0_1px_1px_rgba(255,255,255,0.1),_inset_0_-1px_2px_rgba(0,0,0,0.8),_0_0_15px_rgba(34,197,94,0.3)] border-eco-500/30',
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
    eco: 'text-eco-400 bg-panel-700 shadow-recessed border-t border-black/50',
    blue: 'text-blue-400 bg-panel-700 shadow-recessed border-t border-black/50',
    amber: 'text-amber-400 bg-panel-700 shadow-recessed border-t border-black/50',
    red: 'text-red-400 bg-panel-700 shadow-recessed border-t border-black/50',
    purple: 'text-purple-400 bg-panel-700 shadow-recessed border-t border-black/50',
  }
  const trendColor =
    trend === 'up' ? 'text-eco-400 drop-shadow-[0_0_8px_rgba(74,222,128,0.5)]' : trend === 'down' ? 'text-red-400 drop-shadow-[0_0_8px_rgba(239,68,68,0.5)]' : 'text-slate-400'

  return (
    <Card className="relative overflow-hidden">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400 font-bold drop-shadow-md">
            {label}
          </p>
          <div className="mt-3 flex items-baseline gap-1 bg-panel-900 shadow-lcd rounded px-3 py-1.5 border-t border-black border-b border-white/5">
            <span className="text-2xl font-display font-bold text-white count-up tracking-wider">{value}</span>
            {unit && <span className="text-xs font-display text-slate-500 ml-1">{unit}</span>}
          </div>
          {delta && (
            <p className={clsx('mt-2 text-xs font-bold', trendColor)}>{delta}</p>
          )}
        </div>
        {icon && (
          <div className={clsx('p-2.5 rounded-lg flex items-center justify-center', accentClasses[accent])}>
            <div className="drop-shadow-[0_0_5px_currentColor]">{icon}</div>
          </div>
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
        'inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider',
        'bg-panel-800 shadow-recessed border-t border-black/60 border-b border-white/5',
        className,
      )}
    >
      <span className="drop-shadow-[0_0_4px_currentColor]">{children}</span>
    </span>
  )
}

export function Spinner({ className }: { className?: string }) {
  return (
    <div className={clsx("flex items-center gap-1.5", className)}>
      <div className="w-2 h-2 rounded-full bg-eco-500 animate-led-blink shadow-glow-green" style={{ animationDelay: '0ms' }} />
      <div className="w-2 h-2 rounded-full bg-eco-500 animate-led-blink shadow-glow-green" style={{ animationDelay: '200ms' }} />
      <div className="w-2 h-2 rounded-full bg-eco-500 animate-led-blink shadow-glow-green" style={{ animationDelay: '400ms' }} />
    </div>
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
