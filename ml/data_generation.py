"""
EcoRoute - Synthetic Dataset Generator
=======================================

Generates a realistic synthetic logistics dataset for fuel-consumption
prediction and route-optimization research.

The generator produces 50,000+ delivery records with physically-plausible
relationships between vehicle characteristics, weather, traffic, road
geometry and the resulting fuel consumption / CO2 emissions / delivery time.

Author : EcoRoute ML Team
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("ecoroute.data_generation")

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
RANDOM_SEED = 42
DEFAULT_N_DELIVERIES = 50_000

# Major Indian metro hubs used as origin/destination anchors (lat, lon)
CITY_HUBS: List[Tuple[str, float, float]] = [
    ("Mumbai", 19.0760, 72.8777),
    ("Delhi", 28.7041, 77.1025),
    ("Bangalore", 12.9716, 77.5946),
    ("Hyderabad", 17.3850, 78.4867),
    ("Chennai", 13.0827, 80.2707),
    ("Kolkata", 22.5726, 88.3639),
    ("Pune", 18.5204, 73.8567),
    ("Ahmedabad", 23.0225, 72.5714),
    ("Jaipur", 26.9124, 75.7873),
    ("Surat", 21.1702, 72.8311),
]

VEHICLE_TYPES = [
    "motorcycle",
    "van",
    "mini_truck",
    "truck",
    "semi_truck",
    "refrigerated_truck",
]

FUEL_TYPES = ["diesel", "petrol", "electric", "cng", "hybrid"]

ROAD_TYPES = ["highway", "arterial", "residential", "urban", "rural"]

TRAFFIC_LEVELS = ["low", "medium", "high"]

# --------------------------------------------------------------------------- #
# Vehicle profiles  (deterministic, physically grounded baselines)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class VehicleProfile:
    """Baseline physical characteristics for a vehicle class."""

    base_weight_kg: float          # kerb weight
    load_capacity_kg: float        # max payload
    base_mileage_kmpl: float       # ideal-condition fuel economy
    avg_speed_kmph: float          # cruising speed
    co2_per_liter: float           # kg CO2 per litre of fuel
    maint_score: float             # 0 (poor) .. 1 (excellent)


VEHICLE_PROFILES: Dict[str, VehicleProfile] = {
    "motorcycle":          VehicleProfile(180,    50,   50.0, 60, 2.30, 0.85),
    "van":                 VehicleProfile(2200,  1200,  12.0, 70, 2.68, 0.80),
    "mini_truck":          VehicleProfile(3500,  2500,   9.5, 65, 2.68, 0.75),
    "truck":               VehicleProfile(8000,  8000,   5.5, 60, 2.68, 0.70),
    "semi_truck":          VehicleProfile(15000, 25000,  3.2, 55, 2.68, 0.65),
    "refrigerated_truck":  VehicleProfile(9000,  6000,   4.0, 58, 2.68, 0.60),
}

# Fuel economy multipliers relative to diesel baseline
FUEL_MILEAGE_MULT: Dict[str, float] = {
    "diesel":   1.00,
    "petrol":   0.85,
    "electric": 2.80,   # expressed in diesel-litre-equivalent
    "cng":      1.15,
    "hybrid":   1.25,
}

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two lat/lon points."""
    R = 6371.0
    lat1_r, lat2_r = np.radians(lat1), np.radians(lat2)
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1_r) * np.cos(lat2_r) * np.sin(dlon / 2) ** 2
    )
    return 2 * R * np.arcsin(np.sqrt(a))


def _sample_load(profile: VehicleProfile, rng: np.random.Generator) -> float:
    """Sample a payload between 10 % and 95 % of capacity."""
    return rng.uniform(0.10, 0.95) * profile.load_capacity_kg


def _elevation_gain_km(distance_km: float, rng: np.random.Generator) -> float:
    """Synthetic cumulative elevation gain (m)."""
    base = distance_km * rng.uniform(3.0, 12.0)   # 3-12 m gain per km
    return float(np.clip(base, 0.0, 1500.0))


# --------------------------------------------------------------------------- #
# Core generators
# --------------------------------------------------------------------------- #
def generate_vehicle_fleet(n_vehicles: int = 500, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Generate a catalogue of vehicles with stable IDs."""
    rng = np.random.default_rng(seed)
    rows = []
    for vid in range(1, n_vehicles + 1):
        vtype = rng.choice(VEHICLE_TYPES)
        ftype = rng.choice(FUEL_TYPES, p=[0.55, 0.15, 0.10, 0.12, 0.08])
        profile = VEHICLE_PROFILES[vtype]
        mileage = profile.base_mileage_kmpl * FUEL_MILEAGE_MULT[ftype]
        mileage *= rng.uniform(0.85, 1.10)         # individual variation
        rows.append(
            {
                "vehicle_id": f"V{vid:04d}",
                "vehicle_type": vtype,
                "fuel_type": ftype,
                "base_mileage_kmpl": round(mileage, 2),
                "kerb_weight_kg": profile.base_weight_kg,
                "load_capacity_kg": profile.load_capacity_kg,
                "avg_speed_kmph": profile.avg_speed_kmph,
                "maintenance_score": round(
                    float(np.clip(profile.maint_score + rng.normal(0, 0.05), 0, 1)), 3
                ),
            }
        )
    return pd.DataFrame(rows)


def generate_deliveries(
    n_deliveries: int = DEFAULT_N_DELIVERIES,
    fleet: pd.DataFrame | None = None,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """Generate the main delivery dataset.

    Each row corresponds to one completed delivery with features observed
    pre-trip and the target variables (fuel_used, delivery_time, co2_emission)
    computed from a physically-plausible model + noise.
    """
    rng = np.random.default_rng(seed)
    fleet = fleet if fleet is not None else generate_vehicle_fleet(seed=seed)

    rows: List[dict] = []
    for _ in range(n_deliveries):
        # --- origin / destination -------------------------------------------------
        o_city = CITY_HUBS[rng.integers(0, len(CITY_HUBS))]
        d_city = CITY_HUBS[rng.integers(0, len(CITY_HUBS))]
        o_lat = o_city[1] + rng.normal(0, 0.15)
        o_lon = o_city[2] + rng.normal(0, 0.15)
        d_lat = d_city[1] + rng.normal(0, 0.15)
        d_lon = d_city[2] + rng.normal(0, 0.15)

        distance_km = _haversine_km(o_lat, o_lon, d_lat, d_lon)
        if distance_km < 1.0:                # same-city short hop
            distance_km = float(rng.uniform(2.0, 15.0))

        # --- vehicle selection ----------------------------------------------------
        vrow = fleet.sample(1, random_state=rng.integers(0, 10**9)).iloc[0]
        vtype = vrow["vehicle_type"]
        ftype = vrow["fuel_type"]
        profile = VEHICLE_PROFILES[vtype]
        load_kg = _sample_load(profile, rng)

        # --- weather --------------------------------------------------------------
        temperature_c = float(rng.normal(28, 8))           # tropical climate
        rainfall_mm = float(np.clip(rng.exponential(1.2), 0, 60))
        wind_speed_kmh = float(np.clip(rng.normal(15, 7), 0, 80))
        humidity_pct = float(np.clip(rng.normal(60, 15), 10, 100))

        # --- traffic --------------------------------------------------------------
        hour_of_day = int(rng.integers(0, 24))
        # Rush-hour bias
        rush_bias = 0.0
        if hour_of_day in (8, 9, 10, 18, 19, 20):
            rush_bias = 0.35
        traffic_level = rng.choice(
            TRAFFIC_LEVELS, p=[0.4 - rush_bias, 0.35, 0.25 + rush_bias]
        )
        traffic_factor = {"low": 1.0, "medium": 1.25, "high": 1.65}[traffic_level]

        # --- road & driving -------------------------------------------------------
        road_type = rng.choice(ROAD_TYPES, p=[0.25, 0.30, 0.15, 0.20, 0.10])
        road_speed_mult = {
            "highway": 1.10, "arterial": 0.95, "residential": 0.60,
            "urban": 0.70, "rural": 0.85,
        }[road_type]

        n_stops = int(np.clip(rng.poisson(distance_km / 25), 0, 30))

        base_speed = vrow["avg_speed_kmph"] * road_speed_mult / traffic_factor
        # Weather penalty
        rain_penalty = min(rainfall_mm / 50.0, 0.4)
        wind_penalty = min(wind_speed_kmh / 120.0, 0.2)
        avg_speed = max(15.0, base_speed * (1 - rain_penalty - wind_penalty))
        # Stop penalty
        avg_speed *= max(0.6, 1 - n_stops * 0.01)

        # --- elevation ------------------------------------------------------------
        elevation_gain_m = _elevation_gain_km(distance_km, rng)

        # --- fuel computation (physical model) -----------------------------------
        # Effective load = kerb + payload
        total_mass = profile.base_weight_kg + load_kg
        # Base litre consumption: distance / mileage
        base_fuel = distance_km / vrow["base_mileage_kmpl"]
        # Mass factor: heavier loads burn more (non-linear)
        mass_ratio = total_mass / (profile.base_weight_kg + 0.5 * profile.load_capacity_kg)
        mass_factor = mass_ratio ** 1.15
        # Elevation adds energy: ~0.003 L per 100 kg per 100 m gain
        elev_fuel = (elevation_gain_m * total_mass * 0.003) / 100_000 * 100
        # Traffic idling fuel
        idle_fuel = n_stops * 0.05 + (traffic_factor - 1) * base_fuel * 0.4
        # Weather fuel penalty
        weather_fuel = base_fuel * (rain_penalty * 0.5 + wind_penalty * 0.3)
        # Speed penalty (very low or very high speeds burn more)
        speed_penalty = abs(avg_speed - 55) / 100
        speed_fuel = base_fuel * speed_penalty

        fuel_used = (
            base_fuel * mass_factor
            + elev_fuel
            + idle_fuel
            + weather_fuel
            + speed_fuel
        )
        # Maintenance penalty (poorly maintained burns ~10% more)
        fuel_used *= 1 + (1 - vrow["maintenance_score"]) * 0.10
        # Add realistic noise
        fuel_used *= rng.normal(1.0, 0.05)
        fuel_used = max(0.1, float(fuel_used))

        # --- delivery time --------------------------------------------------------
        moving_time_h = distance_km / avg_speed
        stop_time_h = n_stops * 0.08          # ~5 min per stop
        delivery_time_h = moving_time_h + stop_time_h
        # Weather / traffic delay
        delivery_time_h *= 1 + rain_penalty * 0.5
        delivery_time_h *= rng.normal(1.0, 0.07)

        # --- CO2 ------------------------------------------------------------------
        co2_emission_kg = fuel_used * profile.co2_per_liter
        if ftype == "electric":
            co2_emission_kg = fuel_used * 0.4    # grid emission equivalent
        elif ftype == "cng":
            co2_emission_kg = fuel_used * 1.9

        # --- priority & deadline --------------------------------------------------
        priority = rng.choice(["low", "medium", "high", "critical"], p=[0.35, 0.40, 0.20, 0.05])
        deadline_hours = float(np.clip(delivery_time_h * rng.uniform(1.2, 2.5), 2.0, 96.0))

        rows.append(
            {
                "delivery_id": f"D{len(rows) + 1:06d}",
                "vehicle_id": vrow["vehicle_id"],
                "vehicle_type": vtype,
                "fuel_type": ftype,
                "kerb_weight_kg": profile.base_weight_kg,
                "load_capacity_kg": profile.load_capacity_kg,
                "load_weight_kg": round(load_kg, 1),
                "maintenance_score": vrow["maintenance_score"],
                "origin_lat": round(o_lat, 6),
                "origin_lon": round(o_lon, 6),
                "destination_lat": round(d_lat, 6),
                "destination_lon": round(d_lon, 6),
                "distance_km": round(distance_km, 3),
                "elevation_gain_m": round(elevation_gain_m, 1),
                "road_type": road_type,
                "traffic_level": traffic_level,
                "hour_of_day": hour_of_day,
                "temperature_c": round(temperature_c, 1),
                "rainfall_mm": round(rainfall_mm, 2),
                "wind_speed_kmh": round(wind_speed_kmh, 2),
                "humidity_pct": round(humidity_pct, 1),
                "stops": n_stops,
                "avg_speed_kmph": round(avg_speed, 2),
                "priority": priority,
                "deadline_hours": round(deadline_hours, 2),
                "fuel_used_l": round(fuel_used, 4),
                "delivery_time_h": round(delivery_time_h, 4),
                "co2_emission_kg": round(co2_emission_kg, 4),
            }
        )

    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# CLI entry point
# --------------------------------------------------------------------------- #
def main(n: int = DEFAULT_N_DELIVERIES, out_dir: str = "data/raw") -> Path:
    """Generate dataset and persist to CSV."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    logger.info("Generating vehicle fleet (n=500) ...")
    fleet = generate_vehicle_fleet()
    fleet_path = out_path / "vehicles.csv"
    fleet.to_csv(fleet_path, index=False)
    logger.info("Fleet saved -> %s (%d rows)", fleet_path, len(fleet))

    logger.info("Generating %d deliveries ...", n)
    df = generate_deliveries(n_deliveries=n, fleet=fleet)
    deliveries_path = out_path / "deliveries.csv"
    df.to_csv(deliveries_path, index=False)
    logger.info("Deliveries saved -> %s (%d rows)", deliveries_path, len(df))

    # Quick stats
    stats = {
        "n_records": len(df),
        "n_vehicles": len(fleet),
        "fuel_used_mean": float(df["fuel_used_l"].mean()),
        "fuel_used_std": float(df["fuel_used_l"].std()),
        "co2_mean": float(df["co2_emission_kg"].mean()),
        "delivery_time_mean_h": float(df["delivery_time_h"].mean()),
        "distance_mean_km": float(df["distance_km"].mean()),
    }
    stats_path = out_path / "dataset_stats.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    logger.info("Stats -> %s", stats_path)
    print(json.dumps(stats, indent=2))
    return deliveries_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate EcoRoute synthetic dataset")
    parser.add_argument("-n", "--n-deliveries", type=int, default=DEFAULT_N_DELIVERIES)
    parser.add_argument("-o", "--out-dir", type=str, default="data/raw")
    args = parser.parse_args()

    # When invoked directly we resolve paths relative to the project root
    project_root = Path(__file__).resolve().parents[1]
    os.chdir(project_root)
    main(args.n_deliveries, args.out_dir)
