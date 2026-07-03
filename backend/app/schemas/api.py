"""
EcoRoute Backend - Pydantic Schemas (V1)
========================================

Request/response models for every REST endpoint.

Author : EcoRoute Backend Team
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------------------- #
# Common
# --------------------------------------------------------------------------- #
class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------- #
# Vehicle
# --------------------------------------------------------------------------- #
class VehicleBase(BaseModel):
    vehicle_id: str = Field(..., description="Human-readable vehicle code e.g. V0001")
    vehicle_type: Literal[
        "motorcycle", "van", "mini_truck", "truck", "semi_truck", "refrigerated_truck"
    ]
    fuel_type: Literal["diesel", "petrol", "electric", "cng", "hybrid"]
    base_mileage_kmpl: float = Field(..., gt=0)
    kerb_weight_kg: float = Field(..., gt=0)
    load_capacity_kg: float = Field(..., gt=0)
    avg_speed_kmph: float = Field(60.0, gt=0)
    maintenance_score: float = Field(0.8, ge=0, le=1)
    is_active: bool = True


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    base_mileage_kmpl: Optional[float] = Field(None, gt=0)
    avg_speed_kmph: Optional[float] = Field(None, gt=0)
    maintenance_score: Optional[float] = Field(None, ge=0, le=1)
    is_active: Optional[bool] = None


class VehicleOut(VehicleBase, ORMBase):
    id: str
    created_at: datetime
    updated_at: datetime


# --------------------------------------------------------------------------- #
# Customer
# --------------------------------------------------------------------------- #
class CustomerBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerOut(CustomerBase, ORMBase):
    id: str
    created_at: datetime


# --------------------------------------------------------------------------- #
# Delivery
# --------------------------------------------------------------------------- #
class DeliveryBase(BaseModel):
    customer_id: Optional[str] = None
    origin_lat: float
    origin_lon: float
    destination_lat: float
    destination_lon: float
    package_weight_kg: float = Field(0.0, ge=0)
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    deadline_at: Optional[datetime] = None


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryOut(DeliveryBase, ORMBase):
    id: str
    delivery_code: str
    vehicle_id: Optional[str]
    status: str
    distance_km: Optional[float]
    estimated_time_h: Optional[float]
    estimated_fuel_l: Optional[float]
    estimated_co2_kg: Optional[float]
    route_geometry: Optional[dict[str, Any]]
    actual_fuel_l: Optional[float]
    actual_time_h: Optional[float]
    actual_co2_kg: Optional[float]
    created_at: datetime
    updated_at: datetime
    delivered_at: Optional[datetime]


# --------------------------------------------------------------------------- #
# Fuel prediction
# --------------------------------------------------------------------------- #
class FuelPredictionFeatures(BaseModel):
    """Feature payload for the fuel-prediction endpoint."""

    distance_km: float = Field(..., gt=0)
    load_weight_kg: float = Field(0.0, ge=0)
    kerb_weight_kg: float = Field(0.0, ge=0)
    load_capacity_kg: float = Field(0.0, ge=0)
    maintenance_score: float = Field(0.8, ge=0, le=1)
    elevation_gain_m: float = Field(0.0, ge=0)
    temperature_c: float = 28.0
    rainfall_mm: float = 0.0
    wind_speed_kmh: float = 15.0
    humidity_pct: float = 60.0
    stops: int = Field(0, ge=0)
    avg_speed_kmph: float = 50.0
    hour_of_day: int = Field(12, ge=0, le=23)
    vehicle_type: Literal[
        "motorcycle", "van", "mini_truck", "truck", "semi_truck", "refrigerated_truck"
    ] = "truck"
    fuel_type: Literal["diesel", "petrol", "electric", "cng", "hybrid"] = "diesel"
    road_type: Literal["highway", "arterial", "residential", "urban", "rural"] = "highway"
    traffic_level: Literal["low", "medium", "high"] = "low"
    priority: Literal["low", "medium", "high", "critical"] = "medium"


class FuelPredictionResult(BaseModel):
    fuel_used_l: float
    co2_emission_kg: float
    model_name: str
    model_r2: float
    model_mae: float
    estimated_cost_inr: Optional[float] = None


# --------------------------------------------------------------------------- #
# Route optimisation
# --------------------------------------------------------------------------- #
class RouteRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    destination_lat: float
    destination_lon: float
    vehicle_type: str = "truck"
    fuel_type: str = "diesel"
    algorithm: Literal["dijkstra", "astar", "ortools"] = "astar"


class RouteResponse(BaseModel):
    distance_km: float
    estimated_time_h: float
    estimated_fuel_l: float
    estimated_co2_kg: float
    estimated_cost_inr: float
    path: list[list[float]]   # [[lat, lon], ...]
    algorithm: str
    traffic_level: str
    weather_penalty: float


# --------------------------------------------------------------------------- #
# Fleet optimisation
# --------------------------------------------------------------------------- #
class FleetOptimizationRequest(BaseModel):
    """Assign a batch of deliveries to available vehicles."""

    delivery_ids: List[str] = Field(..., min_length=1)
    vehicle_ids: List[str] = Field(..., min_length=1)
    max_stops_per_vehicle: int = Field(8, ge=1, le=50)


class FleetAssignment(BaseModel):
    vehicle_id: str
    delivery_codes: List[str]
    total_distance_km: float
    total_fuel_l: float
    total_co2_kg: float
    total_cost_inr: float
    total_time_h: float
    route_order: List[int]


class FleetOptimizationResponse(BaseModel):
    assignments: List[FleetAssignment]
    unassigned: List[str]
    total_fuel_l: float
    total_co2_kg: float
    total_cost_inr: float
    estimated_fuel_saved_pct: float
    algorithm: str


# --------------------------------------------------------------------------- #
# Analytics
# --------------------------------------------------------------------------- #
class AnalyticsSummary(BaseModel):
    total_deliveries: int
    total_distance_km: float
    total_fuel_l: float
    total_co2_kg: float
    fuel_saved_l: float
    distance_saved_km: float
    co2_saved_kg: float
    cost_saved_inr: float
    avg_delivery_time_h: float
    avg_efficiency_score: float
    vehicle_utilization_pct: float
    period: str


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float


class TimeSeriesResponse(BaseModel):
    metric: str
    points: List[TimeSeriesPoint]


# --------------------------------------------------------------------------- #
# Health
# --------------------------------------------------------------------------- #
class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool
    database_ready: bool
