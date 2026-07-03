import { Outlet, NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Truck,
  Package,
  Route,
  Network,
  BarChart3,
  BrainCircuit,
  Leaf,
} from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/vehicles', label: 'Vehicles', icon: Truck },
  { to: '/deliveries', label: 'Deliveries', icon: Package },
  { to: '/routes', label: 'Route Optimizer', icon: Route },
  { to: '/fleet', label: 'Fleet Optimizer', icon: Network },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/model', label: 'ML Model', icon: BrainCircuit },
]

export default function App() {
  return (
    <div className="flex h-screen bg-ink-950 text-slate-200">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 border-r border-ink-800 bg-ink-900/60 backdrop-blur">
        <div className="flex items-center gap-2 px-6 h-16 border-b border-ink-800">
          <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-eco-500/15 text-eco-400">
            <Leaf size={20} />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white">EcoRoute</h1>
            <p className="text-[10px] text-slate-500 -mt-0.5 uppercase tracking-wider">
              Logistics Optimization
            </p>
          </div>
        </div>

        <nav className="px-3 py-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all',
                  isActive
                    ? 'bg-eco-500/15 text-eco-300 border-l-2 border-eco-400'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-ink-800/50',
                )
              }
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="absolute bottom-0 w-64 p-4 border-t border-ink-800">
          <div className="rounded-lg bg-ink-800/40 p-3">
            <p className="text-xs text-slate-400">System Status</p>
            <div className="flex items-center gap-2 mt-1">
              <span className="w-2 h-2 rounded-full bg-eco-400 animate-pulse-slow"></span>
              <span className="text-xs text-eco-300 font-medium">Operational</span>
            </div>
            <p className="text-[10px] text-slate-500 mt-2">
              ML model: CatBoost R²=0.9883
            </p>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
