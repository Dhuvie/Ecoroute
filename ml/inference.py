"""
EcoRoute - Inference Helper
===========================

Loads the persisted best model and exposes a single ``predict_fuel`` helper
used by the FastAPI backend.

Author : EcoRoute ML Team
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd

from .features import FEATURE_COLUMNS, add_cyclical_features

logger = logging.getLogger("ecoroute.inference")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "best_model.joblib"


class FuelPredictor:
    """Thin wrapper around the persisted sklearn Pipeline."""

    def __init__(self, model_path: str | Path = DEFAULT_MODEL_PATH):
        if not Path(model_path).exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}. Run `python -m ml.train` first."
            )
        bundle = joblib.load(model_path)
        self.pipeline = bundle["pipeline"]
        self.model_name = bundle.get("model_name", "unknown")
        self.target = bundle.get("target", "fuel_used_l")
        self.feature_columns = bundle["feature_columns"]
        self.training_metrics = bundle.get("metrics", {})
        logger.info("Loaded model %s | target=%s", self.model_name, self.target)

    # ------------------------------------------------------------------ #
    def _build_input_frame(self, payload: Dict | List[Dict]) -> pd.DataFrame:
        """Convert an API payload into a feature dataframe."""
        if isinstance(payload, dict):
            payload = [payload]
        df = pd.DataFrame(payload)
        # Defaults for optional fields
        defaults = {
            "elevation_gain_m": 0.0,
            "load_weight_kg": 0.0,
            "kerb_weight_kg": 0.0,
            "load_capacity_kg": 0.0,
            "maintenance_score": 0.8,
            "temperature_c": 28.0,
            "rainfall_mm": 0.0,
            "wind_speed_kmh": 15.0,
            "humidity_pct": 60.0,
            "stops": 0,
            "avg_speed_kmph": 50.0,
            "hour_of_day": 12,
            "vehicle_type": "truck",
            "fuel_type": "diesel",
            "road_type": "highway",
            "traffic_level": "low",
            "priority": "medium",
        }
        for k, v in defaults.items():
            if k not in df.columns:
                df[k] = v
        df = add_cyclical_features(df)
        # Ensure all expected columns exist
        for col in FEATURE_COLUMNS:
            if col not in df.columns:
                df[col] = 0
        return df[FEATURE_COLUMNS]

    # ------------------------------------------------------------------ #
    def predict(self, payload: Dict | List[Dict]) -> List[Dict]:
        """Return prediction records with fuel + derived metrics."""
        X = self._build_input_frame(payload)
        preds = self.pipeline.predict(X)
        results = []
        for i, p in enumerate(preds):
            # Co2 emission estimate from fuel (diesel baseline)
            fuel = float(max(0.0, p))
            record = {
                "fuel_used_l": round(fuel, 4),
                "co2_emission_kg": round(fuel * 2.68, 4),
                "model_name": self.model_name,
                "model_r2": self.training_metrics.get("r2", 0.0),
                "model_mae": self.training_metrics.get("mae", 0.0),
            }
            results.append(record)
        return results

    # ------------------------------------------------------------------ #
    def predict_single(self, payload: Dict) -> Dict:
        return self.predict(payload)[0]


# --------------------------------------------------------------------------- #
# CLI smoke test
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    predictor = FuelPredictor()
    sample = {
        "distance_km": 145.0,
        "load_weight_kg": 3500.0,
        "kerb_weight_kg": 8000.0,
        "load_capacity_kg": 8000.0,
        "maintenance_score": 0.75,
        "temperature_c": 32.0,
        "rainfall_mm": 5.0,
        "wind_speed_kmh": 18.0,
        "humidity_pct": 65.0,
        "stops": 4,
        "avg_speed_kmph": 58.0,
        "hour_of_day": 9,
        "vehicle_type": "truck",
        "fuel_type": "diesel",
        "road_type": "highway",
        "traffic_level": "medium",
        "priority": "high",
        "elevation_gain_m": 120.0,
    }
    result = predictor.predict_single(sample)
    print("Prediction:", result)
