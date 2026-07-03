"""
EcoRoute Backend - Fuel Prediction Service
==========================================

Wraps the persisted ML pipeline and adds cost computation.

Author : EcoRoute Backend Team
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, Dict, List

from ..core.config import settings
from ..schemas.api import FuelPredictionFeatures, FuelPredictionResult

logger = logging.getLogger("ecoroute.services.fuel")


class FuelPredictionService:
    """Singleton service that loads the ML pipeline lazily and serves predictions."""

    _instance: "FuelPredictionService | None" = None
    _lock = threading.Lock()

    def __new__(cls) -> "FuelPredictionService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialise()
        return cls._instance

    # ------------------------------------------------------------------ #
    def _initialise(self) -> None:
        self._predictor = None
        self._load_error: str | None = None
        try:
            self._load_predictor()
        except Exception as exc:
            self._load_error = str(exc)
            logger.warning("Model load deferred: %s", exc)

    def _load_predictor(self):
        """Lazy import to avoid circular dependency with the ml package."""
        import sys
        from pathlib import Path as _Path

        project_root = _Path(__file__).resolve().parents[3]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from ml.inference import FuelPredictor

        self._predictor = FuelPredictor(model_path=settings.model_path)
        logger.info(
            "FuelPredictionService ready | model=%s",
            self._predictor.model_name,
        )

    # ------------------------------------------------------------------ #
    @property
    def is_ready(self) -> bool:
        return self._predictor is not None

    @property
    def load_error(self) -> str | None:
        return self._load_error

    # ------------------------------------------------------------------ #
    def predict(self, features: FuelPredictionFeatures) -> FuelPredictionResult:
        """Predict fuel usage + CO2 + cost for a single trip."""
        if not self.is_ready:
            # Try to load again in case the model was just trained
            try:
                self._load_predictor()
            except Exception as exc:
                raise RuntimeError(
                    f"Model not available: {self._load_error or exc}"
                ) from exc

        payload = features.model_dump()
        result = self._predictor.predict_single(payload)
        cost_inr = result["fuel_used_l"] * settings.fuel_price_per_liter
        return FuelPredictionResult(
            fuel_used_l=result["fuel_used_l"],
            co2_emission_kg=result["co2_emission_kg"],
            model_name=result["model_name"],
            model_r2=result["model_r2"],
            model_mae=result["model_mae"],
            estimated_cost_inr=round(cost_inr, 2),
        )

    # ------------------------------------------------------------------ #
    def predict_batch(
        self, features_list: List[FuelPredictionFeatures]
    ) -> List[FuelPredictionResult]:
        """Predict for a batch of trips."""
        if not features_list:
            return []
        if not self.is_ready:
            self._load_predictor()
        payloads = [f.model_dump() for f in features_list]
        results = self._predictor.predict(payloads)
        return [
            FuelPredictionResult(
                fuel_used_l=r["fuel_used_l"],
                co2_emission_kg=r["co2_emission_kg"],
                model_name=r["model_name"],
                model_r2=r["model_r2"],
                model_mae=r["model_mae"],
                estimated_cost_inr=round(r["fuel_used_l"] * settings.fuel_price_per_liter, 2),
            )
            for r in results
        ]


# Convenience accessor
fuel_service = FuelPredictionService()
