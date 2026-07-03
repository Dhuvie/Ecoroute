"""
EcoRoute - Hyperparameter Search Spaces for Optuna
==================================================

Each function returns a dictionary of suggested hyperparameters for the
trial. Models without meaningful search spaces fall back to default builds.

Author : EcoRoute ML Team
"""

from __future__ import annotations

import logging
from typing import Callable, Dict

import optuna

from .model_registry import (
    HAS_CB,
    HAS_LGB,
    HAS_XGB,
    build_catboost,
    build_gradient_boosting,
    build_lightgbm,
    build_linear_regression,
    build_random_forest,
    build_xgboost,
)

logger = logging.getLogger("ecoroute.search_space")


# --------------------------------------------------------------------------- #
# Search spaces
# --------------------------------------------------------------------------- #
def suggest_linear_regression(trial: optuna.Trial):
    return build_linear_regression()


def suggest_random_forest(trial: optuna.Trial):
    from sklearn.ensemble import RandomForestRegressor

    return RandomForestRegressor(
        n_estimators=trial.suggest_int("n_estimators", 200, 600, step=100),
        max_depth=trial.suggest_int("max_depth", 8, 24, step=2),
        min_samples_leaf=trial.suggest_int("min_samples_leaf", 2, 8),
        max_features=trial.suggest_categorical("max_features", ["sqrt", 0.7, 0.9, 1.0]),
        n_jobs=1,
        random_state=42,
    )


def suggest_gradient_boosting(trial: optuna.Trial):
    from sklearn.ensemble import GradientBoostingRegressor

    return GradientBoostingRegressor(
        n_estimators=trial.suggest_int("n_estimators", 200, 500, step=50),
        max_depth=trial.suggest_int("max_depth", 3, 7),
        learning_rate=trial.suggest_float("learning_rate", 0.04, 0.15, log=True),
        subsample=trial.suggest_float("subsample", 0.7, 1.0),
        random_state=42,
    )


def suggest_xgboost(trial: optuna.Trial):
    if not HAS_XGB:
        raise ImportError("xgboost not installed")
    from xgboost import XGBRegressor

    return XGBRegressor(
        n_estimators=trial.suggest_int("n_estimators", 300, 800, step=100),
        max_depth=trial.suggest_int("max_depth", 4, 10),
        learning_rate=trial.suggest_float("learning_rate", 0.03, 0.12, log=True),
        subsample=trial.suggest_float("subsample", 0.7, 1.0),
        colsample_bytree=trial.suggest_float("colsample_bytree", 0.6, 1.0),
        min_child_weight=trial.suggest_int("min_child_weight", 1, 8),
        reg_alpha=trial.suggest_float("reg_alpha", 1e-3, 10.0, log=True),
        reg_lambda=trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
        n_jobs=1,
        random_state=42,
        tree_method="hist",
        objective="reg:squarederror",
    )


def suggest_lightgbm(trial: optuna.Trial):
    if not HAS_LGB:
        raise ImportError("lightgbm not installed")
    from lightgbm import LGBMRegressor

    return LGBMRegressor(
        n_estimators=trial.suggest_int("n_estimators", 400, 1000, step=100),
        num_leaves=trial.suggest_int("num_leaves", 31, 127, step=16),
        max_depth=trial.suggest_int("max_depth", -1, 12),
        learning_rate=trial.suggest_float("learning_rate", 0.02, 0.12, log=True),
        subsample=trial.suggest_float("subsample", 0.7, 1.0),
        colsample_bytree=trial.suggest_float("colsample_bytree", 0.6, 1.0),
        min_child_samples=trial.suggest_int("min_child_samples", 5, 30),
        reg_alpha=trial.suggest_float("reg_alpha", 1e-3, 10.0, log=True),
        reg_lambda=trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
        n_jobs=1,
        random_state=42,
        verbosity=-1,
    )


def suggest_catboost(trial: optuna.Trial):
    if not HAS_CB:
        raise ImportError("catboost not installed")
    from catboost import CatBoostRegressor

    return CatBoostRegressor(
        iterations=trial.suggest_int("iterations", 400, 1000, step=100),
        depth=trial.suggest_int("depth", 4, 10),
        learning_rate=trial.suggest_float("learning_rate", 0.02, 0.12, log=True),
        l2_leaf_reg=trial.suggest_float("l2_leaf_reg", 1.0, 10.0, log=True),
        bagging_temperature=trial.suggest_float("bagging_temperature", 0.0, 1.0),
        random_seed=42,
        verbose=False,
        allow_writing_files=False,
    )


SEARCH_SPACES: Dict[str, Callable[[optuna.Trial], object]] = {
    "linear_regression": suggest_linear_regression,
    "random_forest": suggest_random_forest,
    "gradient_boosting": suggest_gradient_boosting,
    "xgboost": suggest_xgboost,
    "lightgbm": suggest_lightgbm,
    "catboost": suggest_catboost,
}
