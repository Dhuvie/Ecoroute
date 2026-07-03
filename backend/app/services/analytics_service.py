"""
EcoRoute Backend - Analytics Service
====================================

Computes KPIs and time-series for the dashboard.

Author : EcoRoute Backend Team
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.orm import Delivery, Vehicle
from ..schemas.api import AnalyticsSummary, TimeSeriesPoint, TimeSeriesResponse

logger = logging.getLogger("ecoroute.services.analytics")


# --------------------------------------------------------------------------- #
# Baseline constants (used to compute savings vs naive single-delivery trips)
# --------------------------------------------------------------------------- #
NAIVE_FUEL_MULTIPLIER = 1.18        # consolidated routes save ~18 % fuel
NAIVE_DISTANCE_MULTIPLIER = 1.15    # consolidated routes save ~15 % distance


class AnalyticsService:
    """Compute dashboard KPIs and time-series."""

    # ------------------------------------------------------------------ #
    def summary(self, db: Session, period: str = "all") -> AnalyticsSummary:
        """Return aggregate KPIs for the given period."""
        now = datetime.utcnow()
        if period == "daily":
            start = now - timedelta(days=1)
        elif period == "weekly":
            start = now - timedelta(days=7)
        elif period == "monthly":
            start = now - timedelta(days=30)
        else:
            start = datetime(2000, 1, 1)

        q = db.query(Delivery).filter(Delivery.created_at >= start)
        total_deliveries = q.count()

        # Aggregates
        agg = q.with_entities(
            func.coalesce(func.sum(Delivery.distance_km), 0.0),
            func.coalesce(func.sum(Delivery.estimated_fuel_l), 0.0),
            func.coalesce(func.sum(Delivery.estimated_co2_kg), 0.0),
            func.coalesce(func.avg(Delivery.estimated_time_h), 0.0),
        ).first()

        total_distance = float(agg[0] or 0.0)
        total_fuel = float(agg[1] or 0.0)
        total_co2 = float(agg[2] or 0.0)
        avg_time = float(agg[3] or 0.0)

        # Savings vs naive
        naive_fuel = total_fuel * NAIVE_FUEL_MULTIPLIER
        naive_distance = total_distance * NAIVE_DISTANCE_MULTIPLIER
        naive_co2 = naive_fuel * 2.68
        fuel_saved = max(0.0, naive_fuel - total_fuel)
        distance_saved = max(0.0, naive_distance - total_distance)
        co2_saved = max(0.0, naive_co2 - total_co2)
        cost_saved = (
            fuel_saved * settings.fuel_price_per_liter
            + distance_saved * 0.5          # maintenance savings
        )

        # Vehicle utilisation
        active_vehicles = db.query(Vehicle).filter(Vehicle.is_active.is_(True)).count()
        assigned_vehicles = (
            db.query(Delivery.vehicle_id)
            .filter(Delivery.created_at >= start)
            .filter(Delivery.vehicle_id.isnot(None))
            .distinct()
            .count()
        )
        utilisation = (
            (assigned_vehicles / active_vehicles * 100.0)
            if active_vehicles > 0
            else 0.0
        )

        # Efficiency score (0-100): weighted blend of savings + utilisation
        efficiency = (
            min(fuel_saved / max(total_fuel, 1.0) * 100, 50)
            + min(utilisation, 50)
        )

        return AnalyticsSummary(
            total_deliveries=total_deliveries,
            total_distance_km=round(total_distance, 2),
            total_fuel_l=round(total_fuel, 2),
            total_co2_kg=round(total_co2, 2),
            fuel_saved_l=round(fuel_saved, 2),
            distance_saved_km=round(distance_saved, 2),
            co2_saved_kg=round(co2_saved, 2),
            cost_saved_inr=round(cost_saved, 2),
            avg_delivery_time_h=round(avg_time, 2),
            avg_efficiency_score=round(efficiency, 2),
            vehicle_utilization_pct=round(utilisation, 2),
            period=period,
        )

    # ------------------------------------------------------------------ #
    def timeseries(
        self,
        db: Session,
        metric: str,
        days: int = 30,
    ) -> TimeSeriesResponse:
        """Return daily time-series for the requested metric.

        metric choices: fuel, distance, co2, deliveries, cost
        """
        now = datetime.utcnow()
        start = now - timedelta(days=days)

        col_map = {
            "fuel": Delivery.estimated_fuel_l,
            "distance": Delivery.distance_km,
            "co2": Delivery.estimated_co2_kg,
            "deliveries": Delivery.id,
            "cost": Delivery.estimated_fuel_l,  # multiplied by price below
        }
        if metric not in col_map:
            raise ValueError(f"Unknown metric {metric!r}")

        col = col_map[metric]
        if metric == "deliveries":
            stmt = (
                db.query(
                    func.date(Delivery.created_at).label("d"),
                    func.count(Delivery.id).label("v"),
                )
                .filter(Delivery.created_at >= start)
                .group_by(func.date(Delivery.created_at))
                .order_by("d")
            )
        else:
            stmt = (
                db.query(
                    func.date(Delivery.created_at).label("d"),
                    func.coalesce(func.sum(col), 0.0).label("v"),
                )
                .filter(Delivery.created_at >= start)
                .group_by(func.date(Delivery.created_at))
                .order_by("d")
            )
        rows = stmt.all()

        points: List[TimeSeriesPoint] = []
        for r in rows:
            value = float(r.v)
            if metric == "cost":
                value = value * settings.fuel_price_per_liter
            points.append(
                TimeSeriesPoint(
                    timestamp=datetime.strptime(str(r.d), "%Y-%m-%d"),
                    value=round(value, 2),
                )
            )

        return TimeSeriesResponse(metric=metric, points=points)

    # ------------------------------------------------------------------ #
    def vehicle_utilization(
        self, db: Session, days: int = 30
    ) -> List[Dict]:
        """Return per-vehicle utilisation stats."""
        start = datetime.utcnow() - timedelta(days=days)
        rows = (
            db.query(
                Vehicle.vehicle_id,
                Vehicle.vehicle_type,
                Vehicle.fuel_type,
                func.count(Delivery.id).label("n_deliveries"),
                func.coalesce(func.sum(Delivery.distance_km), 0.0).label("km"),
                func.coalesce(func.sum(Delivery.estimated_fuel_l), 0.0).label("fuel"),
            )
            .outerjoin(Delivery, Delivery.vehicle_id == Vehicle.id)
            .filter((Delivery.created_at >= start) | (Delivery.id.is_(None)))
            .group_by(Vehicle.id)
            .all()
        )
        return [
            {
                "vehicle_id": r.vehicle_id,
                "vehicle_type": r.vehicle_type,
                "fuel_type": r.fuel_type,
                "n_deliveries": int(r.n_deliveries or 0),
                "distance_km": round(float(r.km or 0), 2),
                "fuel_used_l": round(float(r.fuel or 0), 2),
            }
            for r in rows
        ]


analytics_service = AnalyticsService()
