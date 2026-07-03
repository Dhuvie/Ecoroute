"""
EcoRoute Backend - Weather Service
==================================

Estimates weather parameters for a given coordinate.

In production this would call a real weather API (OpenWeatherMap, etc.).
For the demo / offline mode it returns deterministic synthetic values
seeded by the coordinate so the same location always returns the same
weather.

Author : EcoRoute Backend Team
"""

from __future__ import annotations

import logging
import math
from typing import Dict

logger = logging.getLogger("ecoroute.services.weather")


class WeatherService:
    """Deterministic synthetic weather generator."""

    def estimate_weather(self, lat: float, lon: float) -> Dict[str, float]:
        """Return weather parameters for a coordinate."""
        # Deterministic pseudo-random based on lat/lon
        seed = abs(int((lat * 1000 + lon * 100) )) % 1000
        rng = (math.sin(seed) + 1) / 2  # 0..1

        temperature_c = 20.0 + rng * 18.0             # 20-38 C
        rainfall_mm = max(0.0, (rng - 0.5) * 12.0)    # 0-6 mm
        wind_speed_kmh = 8.0 + rng * 22.0             # 8-30 km/h
        humidity_pct = 40.0 + rng * 50.0              # 40-90 %

        # Speed reduction due to weather (rain + wind)
        rain_penalty = min(rainfall_mm / 50.0, 0.4)
        wind_penalty = min(wind_speed_kmh / 120.0, 0.2)
        speed_reduction_pct = min(0.6, rain_penalty + wind_penalty)

        # Fuel increase due to weather
        fuel_increase_pct = rain_penalty * 0.5 + wind_penalty * 0.3

        # Delay risk
        delay_risk = "low"
        if rain_penalty > 0.2 or wind_penalty > 0.15:
            delay_risk = "high"
        elif rain_penalty > 0.1 or wind_penalty > 0.08:
            delay_risk = "medium"

        return {
            "temperature_c": round(temperature_c, 1),
            "rainfall_mm": round(rainfall_mm, 2),
            "wind_speed_kmh": round(wind_speed_kmh, 2),
            "humidity_pct": round(humidity_pct, 1),
            "speed_reduction_pct": round(speed_reduction_pct, 3),
            "fuel_increase_pct": round(fuel_increase_pct, 3),
            "delay_risk": delay_risk,
        }


weather_service = WeatherService()
