"""
EcoRoute Backend - Fuel Prediction API Router
=============================================
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ...schemas.api import FuelPredictionFeatures, FuelPredictionResult
from ...services.fuel_service import fuel_service

logger = logging.getLogger("ecoroute.api.fuel")

router = APIRouter(prefix="/fuel", tags=["fuel-prediction"])


@router.get("/info")
def model_info():
    """Return metadata about the loaded ML model."""
    return {
        "ready": fuel_service.is_ready,
        "model_name": fuel_service._predictor.model_name if fuel_service.is_ready else None,
        "metrics": fuel_service._predictor.training_metrics if fuel_service.is_ready else None,
        "load_error": fuel_service.load_error,
    }


@router.post("/predict", response_model=FuelPredictionResult)
def predict_fuel(features: FuelPredictionFeatures):
    """Predict fuel consumption for a single trip."""
    try:
        return fuel_service.predict(features)
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(500, detail=str(exc))


@router.post("/predict/batch", response_model=List[FuelPredictionResult])
def predict_fuel_batch(features: List[FuelPredictionFeatures]):
    """Predict fuel consumption for multiple trips."""
    try:
        return fuel_service.predict_batch(features)
    except Exception as exc:
        logger.exception("Batch prediction failed")
        raise HTTPException(500, detail=str(exc))
