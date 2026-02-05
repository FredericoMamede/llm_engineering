"""
Day 3 — Baseline predictors.

Each exposes a callable (item) -> price (number or string; harness post_processes).
Traditional ML uses item.text_for_model (summary or full) and optional numeric features.
"""

import random
from typing import Callable, List, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LinearRegression

from ..curation.items import Item


# ----- Stateless baselines -----


def random_predictor(item: Item) -> float:
    """Predict random price in [1, 1000]. Seed caller for reproducibility."""
    return float(random.randrange(1, 1001))


def constant_predictor(train_prices: List[float]) -> Callable[[Item], float]:
    """Return a predictor that always predicts the train mean."""

    mean_price = sum(train_prices) / len(train_prices) if train_prices else 0.0

    def _predict(item: Item) -> float:
        return mean_price

    return _predict


def length_heuristic_predictor(item: Item) -> float:
    """Heuristic: longer text -> higher price (crude proxy). Clamp to [0, 1000]."""
    text = item.text_for_model or item.full or ""
    length = len(text)
    # Very rough: map length to price band (course used text_length in features).
    price = min(999.0, max(0.0, length * 0.15))
    return price


# ----- Traditional ML (need fit on train) -----


def get_features(item: Item) -> dict:
    """Numeric features for linear regression (course Day 3)."""
    w = item.weight if item.weight is not None else 0.0
    text = item.text_for_model or item.full or ""
    return {
        "weight": w,
        "weight_unknown": 1.0 if w == 0 else 0.0,
        "text_length": len(text),
    }


def linear_regression_predictor(
    train: List[Item],
    feature_columns: Optional[List[str]] = None,
) -> Callable[[Item], float]:
    """Fit LinearRegression on numeric features; predict(item) -> float."""
    if feature_columns is None:
        feature_columns = ["weight", "weight_unknown", "text_length"]
    rows = [get_features(i) for i in train]
    df = pd.DataFrame(rows)
    df["price"] = [i.price for i in train]
    X = df[feature_columns]
    y = df["price"]
    model = LinearRegression()
    model.fit(X, y)

    def _predict(item: Item) -> float:
        f = get_features(item)
        x = pd.DataFrame([f])[feature_columns]
        return max(0.0, float(model.predict(x)[0]))

    return _predict


def nlpr_linear_regression_predictor(
    train: List[Item],
    max_features: int = 2000,
) -> Callable[[Item], float]:
    """NLP + Linear Regression: CountVectorizer on summaries then LinearRegression (course Day 3)."""
    documents = [i.text_for_model or i.full or "" for i in train]
    prices = np.array([float(i.price) for i in train])
    vectorizer = CountVectorizer(max_features=max_features, stop_words="english")
    X = vectorizer.fit_transform(documents)
    model = LinearRegression()
    model.fit(X, prices)

    def _predict(item: Item) -> float:
        text = item.text_for_model or item.full or ""
        x = vectorizer.transform([text])
        return max(0.0, float(model.predict(x)[0]))

    return _predict


def random_forest_predictor(
    train: List[Item],
    max_features: int = 2000,
    n_estimators: int = 100,
    subset: Optional[int] = None,
    random_state: int = 42,
) -> Callable[[Item], float]:
    """Random Forest on bag-of-words (course Day 3). subset limits train size for speed."""
    documents = [i.text_for_model or i.full or "" for i in train]
    prices = np.array([float(i.price) for i in train])
    if subset is not None and len(documents) > subset:
        documents = documents[:subset]
        prices = prices[:subset]
    vectorizer = CountVectorizer(max_features=max_features, stop_words="english")
    X = vectorizer.fit_transform(documents)
    model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state, n_jobs=-1)
    model.fit(X, prices)

    def _predict(item: Item) -> float:
        text = item.text_for_model or item.full or ""
        x = vectorizer.transform([text])
        return max(0.0, float(model.predict(x)[0]))

    return _predict
