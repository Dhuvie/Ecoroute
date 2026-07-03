"""
EcoRoute Backend - Route Optimisation API Router
================================================
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from ...schemas.api import RouteRequest, RouteResponse
from ...services.routing_service import routing_service

logger = logging.getLogger("ecoroute.api.routing")

router = APIRouter(prefix="/routes", tags=["routing"])


@router.post("/optimize", response_model=RouteResponse)
def optimize_route(request: RouteRequest):
    """Compute an optimised route between origin and destination."""
    try:
        return routing_service.optimize(request)
    except Exception as exc:
        logger.exception("Route optimisation failed")
        raise HTTPException(500, detail=str(exc))


@router.get("/algorithms")
def list_algorithms():
    """List supported routing algorithms."""
    return {
        "algorithms": [
            {
                "id": "dijkstra",
                "name": "Dijkstra",
                "description": "Classic shortest-path on a distance-weighted graph.",
            },
            {
                "id": "astar",
                "name": "A* Search",
                "description": "Heuristic-guided shortest path.",
            },
            {
                "id": "ortools",
                "name": "OR-Tools VRP",
                "description": "Google OR-Tools capacitated vehicle routing solver.",
            },
        ]
    }
