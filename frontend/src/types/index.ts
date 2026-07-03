/**
 * Shared TypeScript types for the EcoRoute frontend.
 */

export interface Vehicle {
  id: string
  vehicle_id: string
  vehicle_type: string
  fuel_type: string
  base_mileage_kmpl: number
  kerb_weight_kg: number
  load_capacity_kg: number
  avg_speed_kmph: number
  maintenance_score: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Delivery {
  id: string
  delivery_code: string
  customer_id: string | null
  vehicle_id: string | null
  origin_lat: number
  origin_lon: number
  destination_lat: number
  destination_lon: number
  package_weight_kg: number
  priority: 'low' | 'medium' | 'high' | 'critical'
  deadline_at: string | null
  status: 'pending' | 'assigned' | 'in_transit' | 'delivered' | 'failed' | 'cancelled'
  distance_km: number | null
  estimated_time_h: number | null
  estimated_fuel_l: number | null
  estimated_co2_kg: number | null
  route_geometry: Record<string, unknown> | null
  actual_fuel_l: number | null
  actual_time_h: number | null
  actual_co2_kg: number | null
  created_at: string
  updated_at: string
  delivered_at: string | null
}

export interface FuelPredictionResult {
  fuel_used_l: number
  co2_emission_kg: number
  model_name: string
  model_r2: number
  model_mae: number
  estimated_cost_inr: number | null
}

export interface RouteResponse {
  distance_km: number
  estimated_time_h: number
  estimated_fuel_l: number
  estimated_co2_kg: number
  estimated_cost_inr: number
  path: [number, number][]
  algorithm: string
  traffic_level: string
  weather_penalty: number
}

export interface FleetAssignment {
  vehicle_id: string
  delivery_codes: string[]
  total_distance_km: number
  total_fuel_l: number
  total_co2_kg: number
  total_cost_inr: number
  total_time_h: number
  route_order: number[]
}

export interface FleetOptimizationResponse {
  assignments: FleetAssignment[]
  unassigned: string[]
  total_fuel_l: number
  total_co2_kg: number
  total_cost_inr: number
  estimated_fuel_saved_pct: number
  algorithm: string
}

export interface AnalyticsSummary {
  total_deliveries: number
  total_distance_km: number
  total_fuel_l: number
  total_co2_kg: number
  fuel_saved_l: number
  distance_saved_km: number
  co2_saved_kg: number
  cost_saved_inr: number
  avg_delivery_time_h: number
  avg_efficiency_score: number
  vehicle_utilization_pct: number
  period: string
}

export interface TimeSeriesPoint {
  timestamp: string
  value: number
}

export interface TimeSeriesResponse {
  metric: string
  points: TimeSeriesPoint[]
}

export interface HealthResponse {
  status: string
  version: string
  model_loaded: boolean
  model_name: string | null
  database_ready: boolean
}
