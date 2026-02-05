"""
Week 6 — Evaluation metrics (pure functions).

Metrics: mean absolute error (MAE), mean squared error (MSE), R².
Used by the evaluation harness for baseline comparison.
"""

from typing import List, Sequence


def mean_absolute_error(truths: Sequence[float], predictions: Sequence[float]) -> float:
    """MAE = mean(|truth - pred|)."""
    if not truths or len(truths) != len(predictions):
        raise ValueError("truths and predictions must be same-length non-empty sequences")
    return sum(abs(t - p) for t, p in zip(truths, predictions)) / len(truths)


def mean_squared_error(truths: Sequence[float], predictions: Sequence[float]) -> float:
    """MSE = mean((truth - pred)^2)."""
    if not truths or len(truths) != len(predictions):
        raise ValueError("truths and predictions must be same-length non-empty sequences")
    return sum((t - p) ** 2 for t, p in zip(truths, predictions)) / len(truths)


def r2_score(truths: Sequence[float], predictions: Sequence[float]) -> float:
    """R² = 1 - SS_res / SS_tot; 1.0 = perfect, 0 = baseline mean, can be negative."""
    if not truths or len(truths) != len(predictions):
        raise ValueError("truths and predictions must be same-length non-empty sequences")
    mean_t = sum(truths) / len(truths)
    ss_tot = sum((t - mean_t) ** 2 for t in truths)
    ss_res = sum((t - p) ** 2 for t, p in zip(truths, predictions))
    if ss_tot == 0:
        return 0.0
    return 1.0 - (ss_res / ss_tot)


def compute_all(truths: Sequence[float], predictions: Sequence[float]) -> dict:
    """Return dict with mae, mse, r2."""
    return {
        "mae": mean_absolute_error(truths, predictions),
        "mse": mean_squared_error(truths, predictions),
        "r2": r2_score(truths, predictions),
    }
