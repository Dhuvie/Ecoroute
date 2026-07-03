"""
EcoRoute Backend - Fleet Optimisation API Router
================================================
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.api import FleetOptimizationRequest, FleetOptimizationResponse
from ...services.fleet_service import fleet_service

logger = logging.getLogger("ecoroute.api.fleet")

router = APIRouter(prefix="/fleet", tags=["fleet-optimization"])


@router.post("/optimize", response_model=FleetOptimizationResponse)
def optimize_fleet(request: FleetOptimizationRequest, db: Session = Depends(get_db)):
    """Assign deliveries to vehicles optimally."""
    try:
        return fleet_service.optimize(request, db)
    except Exception as exc:
        logger.exception("Fleet optimisation failed")
        raise HTTPException(500, detail=str(exc))


@router.get("/status")
def fleet_status(db: Session = Depends(get_db)):
    """Quick overview of fleet state."""
    from ...models.orm import Delivery, Vehicle
    from sqlalchemy import func

    total_vehicles = db.query(Vehicle).count()
    active_vehicles = db.query(Vehicle).filter(Vehicle.is_active.is_(True)).count()
    pending_deliveries = db.query(Delivery).filter(Delivery.status == "pending").count()
    in_transit = db.query(Delivery).filter(Delivery.status == "in_transit").count()
    delivered = db.query(Delivery).filter(Delivery.status == "delivered").count()

    return {
        "total_vehicles": total_vehicles,
        "active_vehicles": active_vehicles,
        "pending_deliveries": pending_deliveries,
        "in_transit_deliveries": in_transit,
        "delivered_deliveries": delivered,
    }
