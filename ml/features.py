"""
EcoRoute - Feature Engineering
==============================

Transforms raw delivery records into model-ready features.

Categorical encoding strategy
-----------------------------
* Low-cardinality categoricals (vehicle_type, fuel_type, road_type,
  traffic_level, priority) -> one-hot encoding (interpretable + fast).
* Cyclical features (hour_of_day) -> sin/cos encoding.

Numeric features are kept as-is; scaling is handled inside the model
pipeline so we can serialize a single sklearn Pipeline artifact.

Author : EcoRoute ML Team
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logger = logging.getLogger("ecoroute.features")

# --------------------------------------------------------------------------- #
# Feature specification
# --------------------------------------------------------------------------- #
TARGET_FUEL = "fuel_used_l"
TARGET_TIME = "delivery_time_h"
TARGET_CO2 = "co2_emission_kg"

NUMERIC_FEATURES: List[str] = [
    "distance_km",
    "elevation_gain_m",
    "load_weight_kg",
    "kerb_weight_kg",
    "load_capacity_kg",
    "maintenance_score",
    "temperature_c",
    "rainfall_mm",
    "wind_speed_kmh",
    "humidity_pct",
    "stops",
    "avg_speed_kmph",
    "hour_sin",
    "hour_cos",
]

CATEGORICAL_FEATURES: List[str] = [
    "vehicle_type",
    "fuel_type",
    "road_type",
    "traffic_level",
    "priority",
]

FEATURE_COLUMNS: List[str] = NUMERIC_FEATURES + CATEGORICAL_FEATURES


# --------------------------------------------------------------------------- #
# Transformations
# --------------------------------------------------------------------------- #
def add_cyclical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add sin/cos encoding for hour_of_day."""
    df = df.copy()
    df["hour_sin"] = np.sin(2 * np.pi * df["hour_of_day"] / 24.0)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour_of_day"] / 24.0)
    return df


def build_preprocessor() -> ColumnTransformer:
    """Construct the sklearn ColumnTransformer used inside every model pipeline.

    Returns
    -------
    ColumnTransformer
        Encodes categoricals (one-hot) and scales numerics.
    """
    numeric_tf = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
        ]
    )
    categorical_tf = Pipeline(
        steps=[
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_tf, NUMERIC_FEATURES),
            ("cat", categorical_tf, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def prepare_features(
    df: pd.DataFrame, target: str = TARGET_FUEL
) -> Tuple[pd.DataFrame, pd.Series]:
    """Return (X, y) ready for model training.

    Parameters
    ----------
    df : raw delivery dataframe
    target : one of fuel_used_l / delivery_time_h / co2_emission_kg
    """
    df = add_cyclical_features(df)
    if target not in df.columns:
        raise ValueError(f"Target {target!r} not found in dataframe columns")
    X = df[FEATURE_COLUMNS].copy()
    y = df[target].copy()
    logger.info("Feature matrix shape: %s | target: %s", X.shape, target)
    return X, y


def load_dataset(path: str | Path = "data/raw/deliveries.csv") -> pd.DataFrame:
    """Load the generated deliveries dataset."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {path}. Run `python ml/data_generation.py` first."
        )
    df = pd.read_csv(path)
    logger.info("Loaded %d rows from %s", len(df), path)
    return df


if __name__ == "__main__":
    # Smoke test
    logging.basicConfig(level=logging.INFO)
    df = load_dataset()
    X, y = prepare_features(df)
    print("X shape:", X.shape)
    print("y shape:", y.shape)
    print("Feature columns:", list(X.columns))
