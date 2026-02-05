"""
Week 6 — Evaluation harness.

Single entry point for evaluating any predictor on a test set.
Same metrics (MAE, MSE, R²) and test set for all baselines.
"""

import re
from typing import Callable, List, Optional, Sequence

from .metrics import compute_all


def post_process(value: object) -> float:
    """
    Convert predictor output to float.
    Handles string like "$123.45" or "123.45" via first number match.
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.replace("$", "").replace(",", "").strip()
        match = re.search(r"[-+]?\d*\.?\d+", s)
        return float(match.group()) if match else 0.0
    return 0.0


def evaluate(
    predictor: Callable[[object], object],
    data: Sequence[object],
    size: Optional[int] = None,
) -> dict:
    """
    Run predictor on data and return metrics.

    predictor: function that takes one item (e.g. Item) and returns price (number or string).
    data: sequence of items with .price (truth) and whatever predictor needs (e.g. .summary).
    size: max number of items to evaluate; None = all.

    Returns dict: n, mae, mse, r2, truths, predictions (for optional plotting).
    """
    subset = list(data)[: (size or len(data))]
    if not subset:
        return {"n": 0, "mae": 0.0, "mse": 0.0, "r2": 0.0, "truths": [], "predictions": []}

    truths: List[float] = []
    predictions: List[float] = []
    for item in subset:
        truth = getattr(item, "price", None)
        if truth is None:
            continue
        truths.append(float(truth))
        pred = post_process(predictor(item))
        predictions.append(pred)

    if not truths:
        return {"n": 0, "mae": 0.0, "mse": 0.0, "r2": 0.0, "truths": [], "predictions": []}

    metrics = compute_all(truths, predictions)
    return {
        "n": len(truths),
        "mae": metrics["mae"],
        "mse": metrics["mse"],
        "r2": metrics["r2"],
        "truths": truths,
        "predictions": predictions,
    }
