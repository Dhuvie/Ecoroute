"""
EcoRoute Backend - Analytics API Router
=======================================
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.api import AnalyticsSummary, TimeSeriesResponse
from ...services.analytics_service import analytics_service

logger = logging.getLogger("ecoroute.api.analytics")

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(
    period: str = Query("all", pattern="^(daily|weekly|monthly|all)$"),
    db: Session = Depends(get_db),
):
    """Return aggregate KPIs for the chosen period."""
    return analytics_service.summary(db, period=period)


@router.get("/timeseries", response_model=TimeSeriesResponse)
def get_timeseries(
    metric: str = Query("fuel", pattern="^(fuel|distance|co2|deliveries|cost)$"),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Return daily time-series for a metric."""
    try:
        return analytics_service.timeseries(db, metric=metric, days=days)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc))


@router.get("/vehicle-utilization")
def get_vehicle_utilization(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Per-vehicle utilisation breakdown."""
    return analytics_service.vehicle_utilization(db, days=days)


@router.get("/reports/weekly")
def weekly_report(db: Session = Depends(get_db)):
    """Weekly KPI snapshot."""
    return analytics_service.summary(db, period="weekly").model_dump()


@router.get("/reports/monthly")
def monthly_report(db: Session = Depends(get_db)):
    """Monthly KPI snapshot."""
    return analytics_service.summary(db, period="monthly").model_dump()
