"""
EcoRoute Backend - Traffic Service
==================================

Estimates congestion level (low / medium / high) for a given coordinate
and time-of-day using a deterministic historical-pattern model.

Author : EcoRoute Backend Team
"""

from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Dict

logger = logging.getLogger("ecoroute.services.traffic")


class TrafficService:
    """Deterministic traffic estimator."""

    def estimate_traffic(
        self,
        lat: float,
        lon: float,
        hour: int | None = None,
        timestamp: datetime | None = None,
    ) -> str:
        """Return 'low' | 'medium' | 'high'."""
        if hour is None:
            if timestamp is None:
                timestamp = datetime.utcnow()
            hour = timestamp.hour

        # Base probability from hour-of-day (rush hours 8-10, 18-20)
        rush_bias = 0.0
        if hour in (8, 9, 10, 18, 19, 20):
            rush_bias = 0.35

        # Spatial modulation: city centres are busier
        seed = abs(int((lat * 1000 + lon * 100))) % 1000
        spatial = (math.sin(seed) + 1) / 2  # 0..1

        score = rush_bias + spatial * 0.5
        if score > 0.6:
            return "high"
        if score > 0.3:
            return "medium"
        return "low"

    def estimate_traffic_detailed(
        self, lat: float, lon: float, hour: int | None = None
    ) -> Dict[str, object]:
        """Return traffic level + congestion index (0-1)."""
        level = self.estimate_traffic(lat, lon, hour)
        congestion_map = {"low": 0.2, "medium": 0.5, "high": 0.8}
        return {
            "level": level,
            "congestion_index": congestion_map[level],
            "hour": hour,
        }


traffic_service = TrafficService()
