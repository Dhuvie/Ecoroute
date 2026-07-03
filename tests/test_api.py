"""
EcoRoute - API Smoke Test
=========================

Tests all REST endpoints using FastAPI's TestClient (no running server needed).

Run:
    cd backend && python -m tests.test_api
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add backend dir to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200, r.text
    data = r.json()
    print(f"[OK] /health -> status={data['status']} model={data['model_name']}")
    assert data["status"] == "ok"
    assert data["model_loaded"] is True


def test_vehicles() -> None:
    r = client.get("/api/v1/vehicles")
    assert r.status_code == 200, r.text
    data = r.json()
    print(f"[OK] /api/v1/vehicles -> count={len(data)}")
    assert len(data) > 0
    # Create a new vehicle with unique ID
    import uuid as _uuid
    unique_vid = f"VT{_uuid.uuid4().hex[:6].upper()}"
    payload = {
        "vehicle_id": unique_vid,
        "vehicle_type": "van",
        "fuel_type": "electric",
        "base_mileage_kmpl": 30.0,
        "kerb_weight_kg": 2400,
        "load_capacity_kg": 1200,
        "avg_speed_kmph": 65,
        "maintenance_score": 0.88,
    }
    r = client.post("/api/v1/vehicles", json=payload)
    assert r.status_code == 201, r.text
    print(f"[OK] POST /api/v1/vehicles -> created {r.json()['vehicle_id']}")


def test_fuel_predict() -> None:
    payload = {
        "distance_km": 145.0,
        "load_weight_kg": 3500,
        "vehicle_type": "truck",
        "fuel_type": "diesel",
        "traffic_level": "medium",
        "avg_speed_kmph": 58,
        "stops": 4,
        "temperature_c": 32,
        "rainfall_mm": 5,
        "wind_speed_kmh": 18,
        "humidity_pct": 65,
        "elevation_gain_m": 120,
        "kerb_weight_kg": 8000,
        "load_capacity_kg": 8000,
        "maintenance_score": 0.75,
    }
    r = client.post("/api/v1/fuel/predict", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    print(f"[OK] /api/v1/fuel/predict -> fuel={data['fuel_used_l']}L co2={data['co2_emission_kg']}kg cost=₹{data['estimated_cost_inr']}")
    assert data["fuel_used_l"] > 0
    assert data["co2_emission_kg"] > 0


def test_route_optimize() -> None:
    payload = {
        "origin_lat": 19.076, "origin_lon": 72.877,
        "destination_lat": 18.520, "destination_lon": 73.856,
        "vehicle_type": "truck", "fuel_type": "diesel",
        "algorithm": "astar",
    }
    r = client.post("/api/v1/routes/optimize", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    print(f"[OK] /api/v1/routes/optimize -> dist={data['distance_km']}km fuel={data['estimated_fuel_l']}L path_len={len(data['path'])} traffic={data['traffic_level']}")
    assert data["distance_km"] > 0
    assert len(data["path"]) > 1


def test_create_delivery() -> None:
    payload = {
        "origin_lat": 19.076, "origin_lon": 72.877,
        "destination_lat": 28.704, "destination_lon": 77.102,
        "package_weight_kg": 500,
        "priority": "high",
    }
    r = client.post("/api/v1/deliveries", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    print(f"[OK] POST /api/v1/deliveries -> code={data['delivery_code']} est_fuel={data['estimated_fuel_l']}L")
    assert data["estimated_fuel_l"] > 0


def test_fleet_status() -> None:
    r = client.get("/api/v1/fleet/status")
    assert r.status_code == 200, r.text
    data = r.json()
    print(f"[OK] /api/v1/fleet/status -> vehicles={data['total_vehicles']} pending={data['pending_deliveries']}")


def test_analytics_summary() -> None:
    r = client.get("/api/v1/analytics/summary")
    assert r.status_code == 200, r.text
    data = r.json()
    print(f"[OK] /api/v1/analytics/summary -> deliveries={data['total_deliveries']} fuel={data['total_fuel_l']}L co2={data['total_co2_kg']}kg util={data['vehicle_utilization_pct']}%")

    r = client.get("/api/v1/analytics/summary?period=weekly")
    assert r.status_code == 200, r.text
    print("[OK] /api/v1/analytics/summary?period=weekly -> ok")


def test_analytics_timeseries() -> None:
    r = client.get("/api/v1/analytics/timeseries?metric=fuel&days=7")
    assert r.status_code == 200, r.text
    data = r.json()
    print(f"[OK] /api/v1/analytics/timeseries -> metric={data['metric']} points={len(data['points'])}")


def test_fleet_optimize() -> None:
    # Get some pending deliveries + vehicles
    deliveries = client.get("/api/v1/deliveries").json()
    vehicles = client.get("/api/v1/vehicles").json()
    if not deliveries or not vehicles:
        print("[SKIP] /api/v1/fleet/optimize -> no deliveries/vehicles")
        return
    payload = {
        "delivery_ids": [d["id"] for d in deliveries[:5]],
        "vehicle_ids": [v["id"] for v in vehicles[:3]],
        "max_stops_per_vehicle": 3,
    }
    r = client.post("/api/v1/fleet/optimize", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    print(f"[OK] /api/v1/fleet/optimize -> algorithm={data['algorithm']} assignments={len(data['assignments'])} fuel_saved={data['estimated_fuel_saved_pct']}%")


if __name__ == "__main__":
    print("=" * 70)
    print("EcoRoute API Smoke Test")
    print("=" * 70)
    tests = [
        test_health,
        test_vehicles,
        test_fuel_predict,
        test_route_optimize,
        test_create_delivery,
        test_fleet_status,
        test_analytics_summary,
        test_analytics_timeseries,
        test_fleet_optimize,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as exc:
            print(f"[FAIL] {t.__name__}: {exc}")
            failed += 1
    print("-" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
