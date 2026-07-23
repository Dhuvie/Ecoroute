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
    <div className="flex h-screen bg-panel-950 text-slate-200">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 bg-panel-500 bg-metal-gradient border-r border-black/80 shadow-[2px_0_10px_rgba(0,0,0,0.5)] z-10 relative">
        <div className="flex items-center gap-2 px-6 h-16 border-b border-black/60 shadow-[0_1px_0_rgba(255,255,255,0.05)]">
          <div className="flex items-center justify-center w-9 h-9 rounded bg-panel-700 shadow-recessed border-t border-black/60 border-b border-white/5 text-eco-400">
            <Leaf size={20} className="drop-shadow-[0_0_5px_rgba(74,222,128,0.5)]" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-slate-200 drop-shadow-[0_-1px_1px_rgba(0,0,0,0.8)]">EcoRoute</h1>
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
                  'flex items-center gap-3 px-3 py-2 rounded text-sm font-medium transition-all relative',
                  isActive
                    ? 'bg-panel-700 text-eco-400 shadow-recessed border-t border-black/80 border-b border-white/5'
                    : 'text-slate-300 hover:text-slate-100 hover:bg-panel-600/50 hover:shadow-btn-raised',
                )
              }
            >
              {({ isActive }) => (
                <>
                  <item.icon size={18} className={isActive ? "drop-shadow-[0_0_8px_currentColor]" : "drop-shadow-md"} />
                  <span className="drop-shadow-[0_-1px_1px_rgba(0,0,0,0.8)]">{item.label}</span>
                  {isActive && (
                    <div className="absolute right-3 w-1.5 h-1.5 rounded-full bg-eco-500 shadow-glow-green" />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="absolute bottom-0 w-64 p-4 border-t border-black/60 shadow-[0_-1px_0_rgba(255,255,255,0.05)] bg-metal-gradient">
          <div className="rounded bg-panel-900 shadow-lcd p-3 border-t border-black border-b border-white/5">
            <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">System Status</p>
            <div className="flex items-center gap-2 mt-2">
              <div className="led-indicator text-eco-500 bg-eco-500 animate-led-blink"></div>
              <span className="text-xs text-eco-400 font-bold tracking-wide drop-shadow-[0_0_5px_rgba(74,222,128,0.5)]">OPERATIONAL</span>
            </div>
            <p className="text-[9px] font-mono text-slate-500 mt-3 uppercase tracking-wider">
              ML: CatBoost R²=0.9883
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
