# EcoRoute API Documentation

Base URL: `http://localhost:8000`

Interactive Swagger UI: <http://localhost:8000/docs>
ReDoc: <http://localhost:8000/redoc>
OpenAPI Schema: <http://localhost:8000/openapi.json>

---

## Authentication

The current version does not enforce authentication. For production deployments, add an API gateway or OAuth2 middleware in `backend/app/main.py`.

---

## Health & Metadata

### `GET /health`
Liveness + readiness probe.

**Response**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "model_loaded": true,
  "model_name": "catboost",
  "database_ready": true
}
```

### `GET /api/v1/_meta`
Project metadata for the frontend.

---

## Vehicles

### `GET /api/v1/vehicles`
List all vehicles.

**Query params**
- `skip` (int, default 0)
- `limit` (int, default 100)
- `vehicle_type` (string, optional filter)

**Response**: array of `VehicleOut`

### `POST /api/v1/vehicles`
Create a new vehicle.

**Request body** (`VehicleCreate`)
```json
{
  "vehicle_id": "V0013",
  "vehicle_type": "truck",
  "fuel_type": "diesel",
  "base_mileage_kmpl": 5.5,
  "kerb_weight_kg": 8000,
  "load_capacity_kg": 8000,
  "avg_speed_kmph": 60,
  "maintenance_score": 0.8,
  "is_active": true
}
```

### `GET /api/v1/vehicles/{vehicle_id}`
Get a vehicle by its human-readable ID.

### `PATCH /api/v1/vehicles/{vehicle_id}`
Partial update (mileage, speed, maintenance_score, is_active).

### `DELETE /api/v1/vehicles/{vehicle_id}`
Soft-delete (sets `is_active=false`).

---

## Deliveries

### `GET /api/v1/deliveries`
List deliveries.

**Query params**
- `status` (string, optional: pending/assigned/in_transit/delivered/failed/cancelled)
- `vehicle_id` (string, optional)
- `skip`, `limit`

### `POST /api/v1/deliveries`
Create a delivery. Auto-computes distance (haversine × 1.3 road factor) and ML-based fuel/CO₂ estimates.

**Request body** (`DeliveryCreate`)
```json
{
  "origin_lat": 19.076,
  "origin_lon": 72.877,
  "destination_lat": 28.704,
  "destination_lon": 77.102,
  "package_weight_kg": 500,
  "priority": "high",
  "deadline_at": "2026-07-05T18:00:00Z",
  "customer_id": "abc123"
}
```

### `GET /api/v1/deliveries/{delivery_id}`
Get a delivery by ID or `delivery_code`.

### `POST /api/v1/deliveries/{delivery_id}/assign/{vehicle_id}`
Assign a vehicle to a delivery (status → `assigned`).

### `POST /api/v1/deliveries/{delivery_id}/complete`
Mark as delivered with optional actuals (`actual_fuel_l`, `actual_time_h`).

---

## Fuel Prediction

### `GET /api/v1/fuel/info`
ML model metadata (name, metrics, load status).

### `POST /api/v1/fuel/predict`
Predict fuel consumption for a single trip.

**Request body** (`FuelPredictionFeatures`)
```json
{
  "distance_km": 145.0,
  "load_weight_kg": 3500,
  "kerb_weight_kg": 8000,
  "load_capacity_kg": 8000,
  "maintenance_score": 0.75,
  "elevation_gain_m": 120,
  "temperature_c": 32,
  "rainfall_mm": 5,
  "wind_speed_kmh": 18,
  "humidity_pct": 65,
  "stops": 4,
  "avg_speed_kmph": 58,
  "hour_of_day": 9,
  "vehicle_type": "truck",
  "fuel_type": "diesel",
  "road_type": "highway",
  "traffic_level": "medium",
  "priority": "high"
}
```

**Response** (`FuelPredictionResult`)
```json
{
  "fuel_used_l": 19.80,
  "co2_emission_kg": 53.06,
  "model_name": "catboost",
  "model_r2": 0.9883,
  "model_mae": 15.89,
  "estimated_cost_inr": 1880.50
}
```

### `POST /api/v1/fuel/predict/batch`
Predict for multiple trips. Body: array of `FuelPredictionFeatures`.

---

## Route Optimization

### `POST /api/v1/routes/optimize`
Compute an optimized route between two coordinates.

**Request body** (`RouteRequest`)
```json
{
  "origin_lat": 19.076,
  "origin_lon": 72.877,
  "destination_lat": 18.520,
  "destination_lon": 73.856,
  "vehicle_type": "truck",
  "fuel_type": "diesel",
  "algorithm": "astar"
}
```

**Response** (`RouteResponse`)
```json
{
  "distance_km": 156.228,
  "estimated_time_h": 3.21,
  "estimated_fuel_l": 13.05,
  "estimated_co2_kg": 34.98,
  "estimated_cost_inr": 2045.45,
  "path": [[19.076, 72.877], [19.08, 72.88], ...],
  "algorithm": "astar",
  "traffic_level": "low",
  "weather_penalty": 0.05
}
```

### `GET /api/v1/routes/algorithms`
List supported routing algorithms.

---

## Fleet Optimization

### `POST /api/v1/fleet/optimize`
Solve the capacitated vehicle routing problem.

**Request body** (`FleetOptimizationRequest`)
```json
{
  "delivery_ids": ["uuid1", "uuid2", "uuid3"],
  "vehicle_ids": ["vid1", "vid2"],
  "max_stops_per_vehicle": 8
}
```

**Response** (`FleetOptimizationResponse`)
```json
{
  "assignments": [
    {
      "vehicle_id": "vid1",
      "delivery_codes": ["DL001", "DL002"],
      "total_distance_km": 245.5,
      "total_fuel_l": 18.4,
      "total_co2_kg": 49.3,
      "total_cost_inr": 2245.0,
      "total_time_h": 4.9,
      "route_order": [1, 2]
    }
  ],
  "unassigned": [],
  "total_fuel_l": 18.4,
  "total_co2_kg": 49.3,
  "total_cost_inr": 2245.0,
  "estimated_fuel_saved_pct": 15.25,
  "algorithm": "greedy_capacity_balanced"
}
```

### `GET /api/v1/fleet/status`
Quick fleet overview (vehicle counts + delivery status counts).

---

## Analytics

### `GET /api/v1/analytics/summary?period=all`
Aggregate KPIs. `period`: `daily|weekly|monthly|all`.

**Response** (`AnalyticsSummary`)
```json
{
  "total_deliveries": 21,
  "total_distance_km": 12450.5,
  "total_fuel_l": 1505.03,
  "total_co2_kg": 4033.53,
  "fuel_saved_l": 270.91,
  "distance_saved_km": 1867.58,
  "co2_saved_kg": 726.04,
  "cost_saved_inr": 28872.45,
  "avg_delivery_time_h": 12.45,
  "avg_efficiency_score": 87.3,
  "vehicle_utilization_pct": 61.54,
  "period": "all"
}
```

### `GET /api/v1/analytics/timeseries?metric=fuel&days=30`
Daily time-series. `metric`: `fuel|distance|co2|deliveries|cost`.

### `GET /api/v1/analytics/vehicle-utilization?days=30`
Per-vehicle utilization stats (n_deliveries, distance, fuel).

### `GET /api/v1/analytics/reports/weekly`
### `GET /api/v1/analytics/reports/monthly`
Period-specific KPI snapshots.

---

## Error Handling

All errors return JSON with this shape:

```json
{
  "detail": "Human-readable error message"
}
```

Common status codes:
- `200 OK` – success
- `201 Created` – resource created
- `400 Bad Request` – validation error
- `404 Not Found` – resource missing
- `422 Unprocessable Entity` – Pydantic validation error
- `500 Internal Server Error` – server error (logged)
