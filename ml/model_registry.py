"""
EcoRoute - Model Registry & Builders
====================================

Defines constructors for every candidate regressor plus a unified
``build_model(name)`` factory used by the training pipeline.

Author : EcoRoute ML Team
"""

from __future__ import annotations

import logging
from typing import Callable, Dict

from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression

logger = logging.getLogger("ecoroute.models")

# Optional gradient-boosting libraries are imported lazily so the project
# still runs even if a particular wheel is unavailable.
try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except Exception:  # pragma: no cover
    HAS_XGB = False

try:
    from lightgbm import LGBMRegressor
    HAS_LGB = True
except Exception:  # pragma: no cover
    HAS_LGB = False

try:
    from catboost import CatBoostRegressor
    HAS_CB = True
except Exception:  # pragma: no cover
    HAS_CB = False


# --------------------------------------------------------------------------- #
# Builders
# --------------------------------------------------------------------------- #
def build_linear_regression() -> LinearRegression:
    return LinearRegression(n_jobs=1)


def build_random_forest() -> RandomForestRegressor:
    return RandomForestRegressor(
        n_estimators=100,
        max_depth=14,
        min_samples_leaf=6,
        n_jobs=1,
        random_state=42,
    )


def build_gradient_boosting() -> GradientBoostingRegressor:
    return GradientBoostingRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        random_state=42,
    )


def build_xgboost():
    if not HAS_XGB:
        raise ImportError("xgboost is not installed")
    return XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.06,
        subsample=0.9,
        colsample_bytree=0.9,
        n_jobs=1,
        random_state=42,
        tree_method="hist",
        objective="reg:squarederror",
    )


def build_lightgbm():
    if not HAS_LGB:
        raise ImportError("lightgbm is not installed")
    return LGBMRegressor(
        n_estimators=300,
        max_depth=-1,
        num_leaves=63,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        n_jobs=1,
        random_state=42,
        verbosity=-1,
    )


def build_catboost():
    if not HAS_CB:
        raise ImportError("catboost is not installed")
    return CatBoostRegressor(
        iterations=500,
        depth=6,
        learning_rate=0.05,
        l2_leaf_reg=3.0,
        random_seed=42,
        verbose=False,
        allow_writing_files=False,
        thread_count=1,
    )


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #
MODEL_REGISTRY: Dict[str, Callable] = {
    "linear_regression": build_linear_regression,
    "random_forest": build_random_forest,
    "gradient_boosting": build_gradient_boosting,
    "xgboost": build_xgboost,
    "lightgbm": build_lightgbm,
    "catboost": build_catboost,
}


def list_available_models() -> list[str]:
    """Return only models whose backend is installed."""
    available = []
    for name, builder in MODEL_REGISTRY.items():
        try:
            builder()
            available.append(name)
        except ImportError:
            logger.warning("Model %s is unavailable (missing dependency)", name)
    return available


def build_model(name: str):
    """Instantiate a model by registry name."""
    if name not in MODEL_REGISTRY:
        raise KeyError(f"Unknown model {name!r}. Choices: {list(MODEL_REGISTRY)}")
    return MODEL_REGISTRY[name]()
