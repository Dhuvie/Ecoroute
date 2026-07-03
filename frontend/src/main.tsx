import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App'
import './index.css'

// Pages
import Dashboard from './pages/Dashboard'
import Vehicles from './pages/Vehicles'
import Deliveries from './pages/Deliveries'
import RouteOptimizer from './pages/RouteOptimizer'
import FleetOptimizer from './pages/FleetOptimizer'
import Analytics from './pages/Analytics'
import ModelInsights from './pages/ModelInsights'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />}>
          <Route index element={<Dashboard />} />
          <Route path="vehicles" element={<Vehicles />} />
          <Route path="deliveries" element={<Deliveries />} />
          <Route path="routes" element={<RouteOptimizer />} />
          <Route path="fleet" element={<FleetOptimizer />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="model" element={<ModelInsights />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
