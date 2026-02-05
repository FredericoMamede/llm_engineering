"""
Week 6 — Baseline comparison runner.

Loads train/val/test, runs all predictors through the shared evaluation harness,
reports MAE, MSE, R², and saves a comparison table.

Usage (from repo root):
  python -m experiments.week_06.experiments.run_baseline_comparison
"""

import json
import os
import sys
from pathlib import Path

# Ensure package root (week_06) on path when run as script from repo root.
if __name__ == "__main__" and __package__ is None:
    _repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(_repo_root))

from experiments.week_06.curation import (
    load_from_hf,
    load_from_local,
    generate_synthetic,
)
from experiments.week_06.evaluation import evaluate
from experiments.week_06.models.baselines import (
    random_predictor,
    constant_predictor,
    length_heuristic_predictor,
    linear_regression_predictor,
    nlpr_linear_regression_predictor,
    random_forest_predictor,
)
from experiments.week_06.models.dnn import dnn_predictor
from experiments.week_06.models.llm_pricer import zero_shot_predictor

# ----- Config (override via env or edit) -----
DATA_SOURCE = os.environ.get("W6_DATA_SOURCE", "synthetic")  # synthetic | local | hub
HUB_DATASET = os.environ.get("W6_HUB_DATASET", "")  # e.g. username/items_lite
LOCAL_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"
EVAL_SIZE = int(os.environ.get("W6_EVAL_SIZE", "100"))  # cap test size for speed
RUN_DNN = os.environ.get("W6_RUN_DNN", "0") == "1"  # DNN is slow
RUN_LLM = os.environ.get("W6_RUN_LLM", "0") == "1"  # zero-shot needs API
FINE_TUNED_MODEL = os.environ.get("W6_FINE_TUNED_MODEL", "")  # if set, run fine-tuned
SEED = 42
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "evaluation" / "runs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    if DATA_SOURCE == "hub" and HUB_DATASET:
        return load_from_hf(HUB_DATASET)
    if DATA_SOURCE == "local" and LOCAL_DATA_DIR.exists():
        return load_from_local(LOCAL_DATA_DIR)
    train, val, test = generate_synthetic(n_train=300, n_val=80, n_test=100, seed=SEED)
    return train, val, test


def run_comparison():
    print("Loading data...")
    train, val, test = load_data()
    print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
    test_subset = test[:EVAL_SIZE]

    results = []

    # ----- Random -----
    rng = __import__("random")
    rng.seed(SEED)
    r = evaluate(random_predictor, test_subset, size=EVAL_SIZE)
    results.append({"model": "Random", "n": r["n"], "MAE": r["mae"], "MSE": r["mse"], "R2": r["r2"]})
    print(f"  Random: MAE={r['mae']:.2f}, R2={r['r2']:.2f}")

    # ----- Constant (train mean) -----
    train_prices = [i.price for i in train]
    const_fn = constant_predictor(train_prices)
    r = evaluate(const_fn, test_subset, size=EVAL_SIZE)
    results.append({"model": "Constant (mean)", "n": r["n"], "MAE": r["mae"], "MSE": r["mse"], "R2": r["r2"]})
    print(f"  Constant: MAE={r['mae']:.2f}, R2={r['r2']:.2f}")

    # ----- Length heuristic -----
    r = evaluate(length_heuristic_predictor, test_subset, size=EVAL_SIZE)
    results.append({"model": "Length heuristic", "n": r["n"], "MAE": r["mae"], "MSE": r["mse"], "R2": r["r2"]})
    print(f"  Length heuristic: MAE={r['mae']:.2f}, R2={r['r2']:.2f}")

    # ----- Linear regression (numeric) -----
    lr_fn = linear_regression_predictor(train)
    r = evaluate(lr_fn, test_subset, size=EVAL_SIZE)
    results.append({"model": "Linear regression", "n": r["n"], "MAE": r["mae"], "MSE": r["mse"], "R2": r["r2"]})
    print(f"  Linear regression: MAE={r['mae']:.2f}, R2={r['r2']:.2f}")

    # ----- NLP + Linear regression -----
    nlpr_fn = nlpr_linear_regression_predictor(train, max_features=1000)
    r = evaluate(nlpr_fn, test_subset, size=EVAL_SIZE)
    results.append({"model": "NLP+LR", "n": r["n"], "MAE": r["mae"], "MSE": r["mse"], "R2": r["r2"]})
    print(f"  NLP+LR: MAE={r['mae']:.2f}, R2={r['r2']:.2f}")

    # ----- Random Forest -----
    rf_fn = random_forest_predictor(train, max_features=1000, n_estimators=50, subset=500, random_state=SEED)
    r = evaluate(rf_fn, test_subset, size=EVAL_SIZE)
    results.append({"model": "Random Forest", "n": r["n"], "MAE": r["mae"], "MSE": r["mse"], "R2": r["r2"]})
    print(f"  Random Forest: MAE={r['mae']:.2f}, R2={r['r2']:.2f}")

    # ----- DNN (optional, slow) -----
    if RUN_DNN:
        print("  Training DNN...")
        dnn_fn = dnn_predictor(train[:500], val[:100], epochs=2, num_layers=2, hidden_size=128)
        r = evaluate(dnn_fn, test_subset, size=EVAL_SIZE)
        results.append({"model": "DNN", "n": r["n"], "MAE": r["mae"], "MSE": r["mse"], "R2": r["r2"]})
        print(f"  DNN: MAE={r['mae']:.2f}, R2={r['r2']:.2f}")

    # ----- Zero-shot LLM (optional, needs API) -----
    if RUN_LLM:
        print("  Running zero-shot LLM...")
        llm_fn = zero_shot_predictor(model_name="openai/gpt-4o-mini")
        r = evaluate(llm_fn, test_subset, size=min(20, EVAL_SIZE))
        results.append({"model": "LLM (zero-shot)", "n": r["n"], "MAE": r["mae"], "MSE": r["mse"], "R2": r["r2"]})
        print(f"  LLM zero-shot: MAE={r['mae']:.2f}, R2={r['r2']:.2f}")

    # ----- Fine-tuned (optional, if model name set) -----
    if FINE_TUNED_MODEL:
        from experiments.week_06.models.llm_pricer import fine_tuned_predictor
        ft_fn = fine_tuned_predictor(FINE_TUNED_MODEL)
        r = evaluate(ft_fn, test_subset, size=min(20, EVAL_SIZE))
        results.append({"model": "LLM (fine-tuned)", "n": r["n"], "MAE": r["mae"], "MSE": r["mse"], "R2": r["r2"]})
        print(f"  LLM fine-tuned: MAE={r['mae']:.2f}, R2={r['r2']:.2f}")

    # ----- Table -----
    print("\n" + "=" * 60)
    print("Baseline comparison (MAE, MSE, R²)")
    print("=" * 60)
    for row in results:
        print(f"  {row['model']:<20} n={row['n']}  MAE={row['MAE']:>8.2f}  MSE={row['MSE']:>10.0f}  R2={row['R2']:>6.2f}")
    print("=" * 60)

    # Surprising result: fine-tuning can regress vs base (see evaluation/FAILURE_MODES.md).
    out_path = OUTPUT_DIR / "comparison_latest.json"
    with open(out_path, "w") as f:
        json.dump({"data_source": DATA_SOURCE, "eval_size": EVAL_SIZE, "results": results}, f, indent=2)
    print(f"\nResults saved to {out_path}")

    return results


if __name__ == "__main__":
    run_comparison()
