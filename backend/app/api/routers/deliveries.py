"""
EcoRoute Backend - Deliveries API Router
========================================
"""

from __future__ import annotations

import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.orm import Customer, Delivery
from ...schemas.api import CustomerCreate, CustomerOut, DeliveryCreate, DeliveryOut
from ...services.fuel_service import fuel_service
from ...schemas.api import FuelPredictionFeatures
from ...services.routing_service import haversine_km

logger = logging.getLogger("ecoroute.api.deliveries")

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


# --------------------------------------------------------------------------- #
# Customer sub-resource
# --------------------------------------------------------------------------- #
@router.get("/customers", response_model=List[CustomerOut])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Customer).offset(skip).limit(limit).all()


@router.post("/customers", response_model=CustomerOut, status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    c = Customer(**payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


# --------------------------------------------------------------------------- #
# Deliveries
# --------------------------------------------------------------------------- #
@router.get("", response_model=List[DeliveryOut])
def list_deliveries(
    status_filter: str | None = Query(None, alias="status"),
    vehicle_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(Delivery)
    if status_filter:
        q = q.filter(Delivery.status == status_filter)
    if vehicle_id:
        q = q.filter(Delivery.vehicle_id == vehicle_id)
    return q.order_by(Delivery.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=DeliveryOut, status_code=201)
def create_delivery(payload: DeliveryCreate, db: Session = Depends(get_db)):
    """Create a new delivery and auto-estimate distance/fuel/CO2."""
    distance_km = haversine_km(
        payload.origin_lat, payload.origin_lon,
        payload.destination_lat, payload.destination_lon,
    ) * 1.3  # road distance correction

    # Try ML-based fuel estimate, fall back to mileage heuristic
    estimated_fuel = None
    estimated_co2 = None
    estimated_time = distance_km / 50.0
    try:
        features = FuelPredictionFeatures(
            distance_km=distance_km,
            load_weight_kg=payload.package_weight_kg,
            vehicle_type="truck",
            fuel_type="diesel",
            avg_speed_kmph=50.0,
            traffic_level="medium",
            stops=1,
        )
        result = fuel_service.predict(features)
        estimated_fuel = result.fuel_used_l
        estimated_co2 = result.co2_emission_kg
    except Exception as exc:
        logger.debug("Fuel estimate failed, using heuristic: %s", exc)
        estimated_fuel = distance_km * 0.06
        estimated_co2 = estimated_fuel * 2.68

    d = Delivery(
        delivery_code=f"DL{uuid.uuid4().hex[:8].upper()}",
        customer_id=payload.customer_id,
        origin_lat=payload.origin_lat,
        origin_lon=payload.origin_lon,
        destination_lat=payload.destination_lat,
        destination_lon=payload.destination_lon,
        package_weight_kg=payload.package_weight_kg,
        priority=payload.priority,
        deadline_at=payload.deadline_at,
        status="pending",
        distance_km=round(distance_km, 3),
        estimated_fuel_l=round(estimated_fuel, 4),
        estimated_co2_kg=round(estimated_co2, 4),
        estimated_time_h=round(estimated_time, 3),
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    logger.info("Created delivery %s", d.delivery_code)
    return d


@router.get("/{delivery_id}", response_model=DeliveryOut)
def get_delivery(delivery_id: str, db: Session = Depends(get_db)):
    d = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not d:
        d = db.query(Delivery).filter(Delivery.delivery_code == delivery_id).first()
    if not d:
        raise HTTPException(404, detail="Delivery not found")
    return d


@router.post("/{delivery_id}/assign/{vehicle_id}", response_model=DeliveryOut)
def assign_vehicle(delivery_id: str, vehicle_id: str, db: Session = Depends(get_db)):
    """Assign a vehicle to a delivery."""
    d = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not d:
        raise HTTPException(404, detail="Delivery not found")
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first() if False else None
    # Use string FK
    from ...models.orm import Vehicle
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(404, detail="Vehicle not found")
    d.vehicle_id = v.id
    d.status = "assigned"
    db.commit()
    db.refresh(d)
    return d


@router.post("/{delivery_id}/complete", response_model=DeliveryOut)
def complete_delivery(
    delivery_id: str,
    actual_fuel_l: float | None = None,
    actual_time_h: float | None = None,
    db: Session = Depends(get_db),
):
    """Mark a delivery as delivered with optional actuals."""
    from datetime import datetime
    d = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not d:
        raise HTTPException(404, detail="Delivery not found")
    d.status = "delivered"
    d.delivered_at = datetime.utcnow()
    if actual_fuel_l is not None:
        d.actual_fuel_l = actual_fuel_l
        d.actual_co2_kg = actual_fuel_l * 2.68
    if actual_time_h is not None:
        d.actual_time_h = actual_time_h
    db.commit()
    db.refresh(d)
    return d
