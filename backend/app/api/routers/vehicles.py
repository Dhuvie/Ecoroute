"""
EcoRoute Backend - Vehicles API Router
======================================
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.orm import Vehicle
from ...schemas.api import VehicleCreate, VehicleOut, VehicleUpdate

logger = logging.getLogger("ecoroute.api.vehicles")

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=List[VehicleOut])
def list_vehicles(
    skip: int = 0,
    limit: int = 100,
    vehicle_type: str | None = None,
    db: Session = Depends(get_db),
):
    """List all vehicles with optional type filter."""
    q = db.query(Vehicle)
    if vehicle_type:
        q = q.filter(Vehicle.vehicle_type == vehicle_type)
    return q.offset(skip).limit(limit).all()


@router.post("", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    """Create a new vehicle."""
    existing = db.query(Vehicle).filter(Vehicle.vehicle_id == payload.vehicle_id).first()
    if existing:
        raise HTTPException(400, detail=f"Vehicle {payload.vehicle_id} already exists")
    v = Vehicle(**payload.model_dump())
    db.add(v)
    db.commit()
    db.refresh(v)
    logger.info("Created vehicle %s", v.vehicle_id)
    return v


@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """Get a vehicle by ID."""
    v = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not v:
        raise HTTPException(404, detail="Vehicle not found")
    return v


@router.patch("/{vehicle_id}", response_model=VehicleOut)
def update_vehicle(
    vehicle_id: str, payload: VehicleUpdate, db: Session = Depends(get_db)
):
    """Update vehicle attributes."""
    v = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not v:
        raise HTTPException(404, detail="Vehicle not found")
    for k, val in payload.model_dump(exclude_unset=True).items():
        setattr(v, k, val)
    db.commit()
    db.refresh(v)
    return v


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """Soft-delete a vehicle (sets is_active=False)."""
    v = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not v:
        raise HTTPException(404, detail="Vehicle not found")
    v.is_active = False
    db.commit()
