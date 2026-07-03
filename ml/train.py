"""
EcoRoute - Training Pipeline
============================

End-to-end pipeline that:

1. Loads the synthetic delivery dataset.
2. Engineers features.
3. Trains every candidate model with default hyperparameters.
4. Tunes the best 3 models with Optuna.
5. Evaluates everything with MAE / RMSE / R2 + 5-fold CV.
6. Persists the best model (joblib) + a JSON metrics report.

Run:
    python -m ml.train              # full pipeline
    python -m ml.train --quick      # fast smoke run (5k samples, no Optuna)

Author : EcoRoute ML Team
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline

from .features import (
    FEATURE_COLUMNS,
    TARGET_FUEL,
    build_preprocessor,
    load_dataset,
    prepare_features,
)
from .model_registry import build_model, list_available_models
from .search_spaces import SEARCH_SPACES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("ecoroute.train")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
REPORTS_DIR = PROJECT_ROOT / "ml" / "reports"


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #
def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Return MAE / RMSE / R2 for a regression task."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = r2_score(y_true, y_pred)
    mape = float(np.mean(np.abs((y_true - y_pred) / np.clip(y_true, 1e-3, None))) * 100)
    return {"mae": round(mae, 4), "rmse": round(rmse, 4), "r2": round(r2, 4), "mape": round(mape, 2)}


# --------------------------------------------------------------------------- #
# Single model evaluation
# --------------------------------------------------------------------------- #
def evaluate_model(
    name: str,
    estimator,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    cv_folds: int = 3,
    skip_cv: bool = False,
) -> Dict[str, object]:
    """Train + evaluate a single model. Returns a metrics dict."""
    logger.info("Training %s ...", name)
    t0 = time.time()
    estimator.fit(X_train, y_train)
    fit_seconds = round(time.time() - t0, 2)

    y_pred = estimator.predict(X_test)
    metrics = compute_metrics(y_test.values, y_pred)
    metrics["fit_seconds"] = fit_seconds

    # Cross-validated R2 (more robust generalization estimate).
    # Skipped for memory-intensive models on small boxes.
    if skip_cv:
        metrics["cv_r2_mean"] = metrics["r2"]
        metrics["cv_r2_std"] = 0.0
        logger.info(
            "%s -> MAE=%.4f RMSE=%.4f R2=%.4f (CV skipped) (%.1fs)",
            name, metrics["mae"], metrics["rmse"], metrics["r2"], fit_seconds,
        )
        return metrics

    kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
    cv_scores = cross_val_score(
        estimator, X_train, y_train, cv=kf, scoring="r2", n_jobs=1
    )
    metrics["cv_r2_mean"] = round(float(cv_scores.mean()), 4)
    metrics["cv_r2_std"] = round(float(cv_scores.std()), 4)
    logger.info(
        "%s -> MAE=%.4f RMSE=%.4f R2=%.4f CV-R2=%.4f±%.4f (%.1fs)",
        name, metrics["mae"], metrics["rmse"], metrics["r2"],
        metrics["cv_r2_mean"], metrics["cv_r2_std"], fit_seconds,
    )
    return metrics


# --------------------------------------------------------------------------- #
# Optuna tuning
# --------------------------------------------------------------------------- #
def tune_model(
    name: str,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_trials: int = 25,
) -> Tuple[object, Dict[str, object]]:
    """Run an Optuna study for the given model. Returns (best_estimator, study_summary).

    The estimator returned is the raw model (no preprocessor) - the caller
    wraps it in a Pipeline before final fit + persistence.
    """
    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)

    def objective(trial: optuna.Trial) -> float:
        estimator = SEARCH_SPACES[name](trial)
        # Wrap in pipeline so the ColumnTransformer handles categoricals
        pipe = Pipeline(
            steps=[("preprocessor", build_preprocessor()), ("model", estimator)]
        )
        kf = KFold(n_splits=3, shuffle=True, random_state=42)
        scores = cross_val_score(
            pipe, X_train, y_train, cv=kf, scoring="r2", n_jobs=1
        )
        return float(scores.mean())

    study = optuna.create_study(direction="maximize", study_name=f"ecoroute_{name}")
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    logger.info(
        "%s Optuna best R2=%.4f (trial %d)",
        name, study.best_value, study.best_trial.number,
    )
    # Return the raw model with best params; the caller wraps it in a Pipeline
    # and calls pipe.fit() which fits the model on the full training set.
    best_estimator = SEARCH_SPACES[name](study.best_trial)
    summary = {
        "best_value": round(study.best_value, 4),
        "best_params": dict(study.best_params),
        "n_trials": n_trials,
    }
    return best_estimator, summary


# --------------------------------------------------------------------------- #
# Main pipeline
# --------------------------------------------------------------------------- #
def run_pipeline(
    dataset_path: str | Path = "data/raw/deliveries.csv",
    target: str = TARGET_FUEL,
    quick: bool = False,
    n_trials: int = 25,
    top_k_tune: int = 3,
    sample_size: int | None = 12000,
) -> Dict[str, object]:
    """Run the full training pipeline.

    Returns a summary dict containing all metrics + the path to the saved
    best model.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Loading dataset from %s ...", dataset_path)
    df = load_dataset(dataset_path)
    if quick:
        df = df.sample(n=min(5000, len(df)), random_state=42).reset_index(drop=True)
        n_trials = 5
        top_k_tune = 2
        sample_size = None
    elif sample_size is not None and len(df) > sample_size:
        logger.info("Subsampling to %d rows for memory efficiency", sample_size)
        df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)

    X, y = prepare_features(df, target=target)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info(
        "Train=%d  Test=%d  Features=%d", len(X_train), len(X_test), X.shape[1]
    )

    available = list_available_models()
    logger.info("Available models: %s", available)

    # Models where cross_val_score is too memory-intensive on small boxes
    CV_SKIP_MODELS = {"gradient_boosting", "catboost"}

    # ------------------------------------------------------------------ #
    # Stage 1 - default-hyperparameter benchmark for every model
    # ------------------------------------------------------------------ #
    baseline_metrics: Dict[str, Dict] = {}
    baseline_estimators: Dict[str, Pipeline] = {}

    for name in available:
        pre = build_preprocessor()
        est = build_model(name)
        pipe = Pipeline(steps=[("preprocessor", pre), ("model", est)])
        try:
            m = evaluate_model(
                name, pipe, X_train, y_train, X_test, y_test,
                skip_cv=name in CV_SKIP_MODELS,
            )
            baseline_metrics[name] = m
            baseline_estimators[name] = pipe
        except Exception as exc:  # pragma: no cover
            logger.exception("Model %s failed: %s", name, exc)

    # ------------------------------------------------------------------ #
    # Stage 2 - Optuna-tune the top-K models by R2
    # ------------------------------------------------------------------ #
    ranked = sorted(
        baseline_metrics.items(), key=lambda kv: kv[1]["r2"], reverse=True
    )
    top_k = [name for name, _ in ranked[:top_k_tune]]
    logger.info("Top-%d models to tune: %s", top_k_tune, top_k)

    tuned_metrics: Dict[str, Dict] = {}
    tuned_estimators: Dict[str, Pipeline] = {}
    tuning_summaries: Dict[str, Dict] = {}

    for name in top_k:
        logger.info("Tuning %s with Optuna (%d trials) ...", name, n_trials)
        # We tune only the model; the preprocessor is fixed.
        best_est, summary = tune_model(
            name, X_train, y_train, n_trials=n_trials
        )
        pipe = Pipeline(
            steps=[("preprocessor", build_preprocessor()), ("model", best_est)]
        )
        # Refit on training set so the saved pipeline is fully trained
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        tuned_m = compute_metrics(y_test.values, y_pred)
        tuned_m["fit_seconds"] = summary
        tuned_metrics[name] = tuned_m
        tuned_estimators[name] = pipe
        tuning_summaries[name] = summary

    # ------------------------------------------------------------------ #
    # Stage 3 - pick the overall best model (tuned vs baseline)
    # ------------------------------------------------------------------ #
    all_results = {**baseline_metrics, **tuned_metrics}
    best_name = max(all_results, key=lambda k: all_results[k]["r2"])
    best_pipe = tuned_estimators.get(best_name, baseline_estimators.get(best_name))
    best_metrics = all_results[best_name]

    logger.info("=== BEST MODEL: %s | R2=%.4f ===", best_name, best_metrics["r2"])

    # Persist best model
    model_path = MODELS_DIR / "best_model.joblib"
    joblib.dump(
        {
            "pipeline": best_pipe,
            "model_name": best_name,
            "target": target,
            "feature_columns": FEATURE_COLUMNS,
            "metrics": best_metrics,
        },
        model_path,
    )
    logger.info("Best model persisted -> %s", model_path)

    # Persist full report
    report = {
        "target": target,
        "dataset_size": len(df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "feature_columns": FEATURE_COLUMNS,
        "baseline_metrics": baseline_metrics,
        "tuned_metrics": tuned_metrics,
        "tuning_summaries": tuning_summaries,
        "best_model": best_name,
        "best_metrics": best_metrics,
        "all_results_ranked": [
            {"model": k, **v} for k, v in sorted(
                all_results.items(), key=lambda kv: kv[1]["r2"], reverse=True
            )
        ],
    }
    report_path = REPORTS_DIR / "training_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    logger.info("Training report persisted -> %s", report_path)

    # Also save a CSV of metrics for quick comparison
    metrics_csv = REPORTS_DIR / "model_comparison.csv"
    pd.DataFrame(
        [{"model": k, **v} for k, v in all_results.items()]
    ).to_csv(metrics_csv, index=False)
    logger.info("Model comparison CSV -> %s", metrics_csv)

    return report


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(description="EcoRoute training pipeline")
    parser.add_argument("--dataset", type=str, default="data/raw/deliveries.csv")
    parser.add_argument("--target", type=str, default=TARGET_FUEL)
    parser.add_argument("--quick", action="store_true", help="Fast smoke run")
    parser.add_argument("--trials", type=int, default=25)
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    import os
    os.chdir(PROJECT_ROOT)

    run_pipeline(
        dataset_path=args.dataset,
        target=args.target,
        quick=args.quick,
        n_trials=args.trials,
        top_k_tune=args.top_k,
    )


if __name__ == "__main__":
    main()
