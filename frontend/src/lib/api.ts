/**
 * EcoRoute API client - thin wrapper around axios with typed methods.
 */

import axios from 'axios'
import type {
  AnalyticsSummary,
  Delivery,
  FleetOptimizationResponse,
  FuelPredictionResult,
  HealthResponse,
  RouteResponse,
  TimeSeriesResponse,
  Vehicle,
} from '../types'

let BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'
if (BASE_URL && !BASE_URL.endsWith('/api/v1')) {
  BASE_URL = BASE_URL.replace(/\/$/, '') + '/api/v1'
}

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

// --------------------------------------------------------------------------- //
// Health
// --------------------------------------------------------------------------- //
export const api = {
  async health(): Promise<HealthResponse> {
    const rootUrl = BASE_URL.endsWith('/api/v1')
      ? BASE_URL.slice(0, -7)
      : BASE_URL;
    const r = await axios.get(`${rootUrl}/health`)
    return r.data
  },

  // ------------------------------------------------------------------ //
  // Vehicles
  // ------------------------------------------------------------------ //
  async listVehicles(): Promise<Vehicle[]> {
    const r = await client.get<Vehicle[]>('/vehicles')
    return r.data
  },

  async createVehicle(payload: Partial<Vehicle>): Promise<Vehicle> {
    const r = await client.post<Vehicle>('/vehicles', payload)
    return r.data
  },

  async deleteVehicle(vehicleId: string): Promise<void> {
    await client.delete(`/vehicles/${vehicleId}`)
  },

  // ------------------------------------------------------------------ //
  // Deliveries
  // ------------------------------------------------------------------ //
  async listDeliveries(): Promise<Delivery[]> {
    const r = await client.get<Delivery[]>('/deliveries')
    return r.data
  },

  async createDelivery(payload: Partial<Delivery>): Promise<Delivery> {
    const r = await client.post<Delivery>('/deliveries', payload)
    return r.data
  },

  // ------------------------------------------------------------------ //
  // Fuel prediction
  // ------------------------------------------------------------------ //
  async predictFuel(features: Record<string, unknown>): Promise<FuelPredictionResult> {
    const r = await client.post<FuelPredictionResult>('/fuel/predict', features)
    return r.data
  },

  // ------------------------------------------------------------------ //
  // Routing
  // ------------------------------------------------------------------ //
  async optimizeRoute(payload: Record<string, unknown>): Promise<RouteResponse> {
    const r = await client.post<RouteResponse>('/routes/optimize', payload)
    return r.data
  },

  // ------------------------------------------------------------------ //
  // Fleet optimisation
  // ------------------------------------------------------------------ //
  async optimizeFleet(payload: {
    delivery_ids: string[]
    vehicle_ids: string[]
    max_stops_per_vehicle?: number
  }): Promise<FleetOptimizationResponse> {
    const r = await client.post<FleetOptimizationResponse>('/fleet/optimize', payload)
    return r.data
  },

  async fleetStatus(): Promise<Record<string, number>> {
    const r = await client.get('/fleet/status')
    return r.data
  },

  // ------------------------------------------------------------------ //
  // Analytics
  // ------------------------------------------------------------------ //
  async analyticsSummary(period: string = 'all'): Promise<AnalyticsSummary> {
    const r = await client.get<AnalyticsSummary>(`/analytics/summary?period=${period}`)
    return r.data
  },

  async analyticsTimeseries(metric: string, days: number = 30): Promise<TimeSeriesResponse> {
    const r = await client.get<TimeSeriesResponse>(
      `/analytics/timeseries?metric=${metric}&days=${days}`,
    )
    return r.data
  },

  async vehicleUtilization(days: number = 30): Promise<Record<string, unknown>[]> {
    const r = await client.get(`/analytics/vehicle-utilization?days=${days}`)
    return r.data
  },
}
