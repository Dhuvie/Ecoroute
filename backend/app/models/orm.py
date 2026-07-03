"""
EcoRoute Backend - ORM Models
=============================

SQLAlchemy ORM models for vehicles, deliveries, and analytics snapshots.

Author : EcoRoute Backend Team
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _uuid() -> str:
    return uuid.uuid4().hex


# --------------------------------------------------------------------------- #
# Enums
# --------------------------------------------------------------------------- #
class VehicleType(str, PyEnum):
    MOTORCYCLE = "motorcycle"
    VAN = "van"
    MINI_TRUCK = "mini_truck"
    TRUCK = "truck"
    SEMI_TRUCK = "semi_truck"
    REFRIGERATED_TRUCK = "refrigerated_truck"


class FuelType(str, PyEnum):
    DIESEL = "diesel"
    PETROL = "petrol"
    ELECTRIC = "electric"
    CNG = "cng"
    HYBRID = "hybrid"


class DeliveryStatus(str, PyEnum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Priority(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# --------------------------------------------------------------------------- #
# Vehicle
# --------------------------------------------------------------------------- #
class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    vehicle_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    vehicle_type: Mapped[str] = mapped_column(String(32), index=True)
    fuel_type: Mapped[str] = mapped_column(String(16), index=True)
    base_mileage_kmpl: Mapped[float] = mapped_column(Float)
    kerb_weight_kg: Mapped[float] = mapped_column(Float)
    load_capacity_kg: Mapped[float] = mapped_column(Float)
    avg_speed_kmph: Mapped[float] = mapped_column(Float, default=60.0)
    maintenance_score: Mapped[float] = mapped_column(Float, default=0.8)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    deliveries: Mapped[list["Delivery"]] = relationship(
        back_populates="vehicle", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Vehicle {self.vehicle_id} ({self.vehicle_type}/{self.fuel_type})>"


# --------------------------------------------------------------------------- #
# Customer
# --------------------------------------------------------------------------- #
class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(128))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    deliveries: Mapped[list["Delivery"]] = relationship(back_populates="customer")

    def __repr__(self) -> str:
        return f"<Customer {self.name}>"


# --------------------------------------------------------------------------- #
# Delivery
# --------------------------------------------------------------------------- #
class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    delivery_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    customer_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("customers.id"), nullable=True
    )
    vehicle_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("vehicles.id"), nullable=True, index=True
    )

    # Geo
    origin_lat: Mapped[float] = mapped_column(Float)
    origin_lon: Mapped[float] = mapped_column(Float)
    destination_lat: Mapped[float] = mapped_column(Float)
    destination_lon: Mapped[float] = mapped_column(Float)

    # Package
    package_weight_kg: Mapped[float] = mapped_column(Float, default=0.0)
    priority: Mapped[str] = mapped_column(String(16), default="medium")
    deadline_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(16), default="pending", index=True
    )

    # Routing
    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_time_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_fuel_l: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_co2_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    route_geometry: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Actuals (filled after delivery)
    actual_fuel_l: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_time_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_co2_kg: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    vehicle: Mapped[Vehicle | None] = relationship(back_populates="deliveries")
    customer: Mapped[Customer | None] = relationship(back_populates="deliveries")

    def __repr__(self) -> str:
        return f"<Delivery {self.delivery_code} [{self.status}]>"


# --------------------------------------------------------------------------- #
# AnalyticsSnapshot
# --------------------------------------------------------------------------- #
class AnalyticsSnapshot(Base):
    """Periodically computed KPIs (daily / weekly / monthly)."""

    __tablename__ = "analytics_snapshots"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    period: Mapped[str] = mapped_column(String(16), index=True)  # daily/weekly/monthly
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    total_deliveries: Mapped[int] = mapped_column(Integer, default=0)
    total_distance_km: Mapped[float] = mapped_column(Float, default=0.0)
    total_fuel_l: Mapped[float] = mapped_column(Float, default=0.0)
    total_co2_kg: Mapped[float] = mapped_column(Float, default=0.0)
    fuel_saved_l: Mapped[float] = mapped_column(Float, default=0.0)
    distance_saved_km: Mapped[float] = mapped_column(Float, default=0.0)
    co2_saved_kg: Mapped[float] = mapped_column(Float, default=0.0)
    cost_saved_inr: Mapped[float] = mapped_column(Float, default=0.0)
    avg_delivery_time_h: Mapped[float] = mapped_column(Float, default=0.0)
    avg_efficiency_score: Mapped[float] = mapped_column(Float, default=0.0)
    vehicle_utilization_pct: Mapped[float] = mapped_column(Float, default=0.0)
    extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<AnalyticsSnapshot {self.period} {self.period_start.date()}>"
