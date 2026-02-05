"""
Day 1 — Load items from HuggingFace or local files; train/val/test split.
"""

import json
import os
import random
from pathlib import Path
from typing import Optional

from .items import Item
from .parser import parse

CHUNK_SIZE = 1000


def _parse_chunk(datapoints: list, category: str) -> list[Item]:
    out = []
    for dp in datapoints:
        item = parse(dp, category)
        if item is not None:
            out.append(item)
    return out


def load_from_hf(
    dataset_name: str,
) -> tuple[list[Item], list[Item], list[Item]]:
    """Load train/val/test from HuggingFace Hub (e.g. username/items_lite)."""
    return Item.from_hub(dataset_name)


def load_from_raw_dataset(
    datapoints: list[dict],
    category: str = "Products",
    seed: int = 42,
    val_ratio: float = 0.0125,
    test_ratio: float = 0.0125,
) -> tuple[list[Item], list[Item], list[Item]]:
    """
    Parse raw records and split into train/val/test.
    val_ratio and test_ratio are fractions of total items (course uses ~10k val, ~10k test on 800k).
    """
    items = []
    for i in range(0, len(datapoints), CHUNK_SIZE):
        chunk = datapoints[i : i + CHUNK_SIZE]
        items.extend(_parse_chunk(chunk, category))
    random.seed(seed)
    random.shuffle(items)
    n = len(items)
    n_val = max(1, int(n * val_ratio))
    n_test = max(1, int(n * test_ratio))
    n_train = n - n_val - n_test
    if n_train < 1:
        n_train, n_val, n_test = n, 0, 0
    train = items[:n_train]
    val = items[n_train : n_train + n_val]
    test = items[n_train + n_val : n_train + n_val + n_test]
    return train, val, test


def load_from_local(
    data_dir: Path,
    train_file: str = "train.jsonl",
    val_file: str = "val.jsonl",
    test_file: str = "test.jsonl",
) -> tuple[list[Item], list[Item], list[Item]]:
    """Load train/val/test from JSONL files (one JSON object per line)."""
    def load_jsonl(path: Path) -> list[Item]:
        if not path.exists():
            return []
        items = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                items.append(Item.model_validate(json.loads(line)))
        return items

    return (
        load_jsonl(data_dir / train_file),
        load_jsonl(data_dir / val_file),
        load_jsonl(data_dir / test_file),
    )


def save_train_val_test(
    train: list[Item],
    val: list[Item],
    test: list[Item],
    data_dir: Path,
    train_file: str = "train.jsonl",
    val_file: str = "val.jsonl",
    test_file: str = "test.jsonl",
) -> None:
    """Write train/val/test to JSONL for reproducibility."""
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    for name, items, fname in [
        ("train", train, train_file),
        ("val", val, val_file),
        ("test", test, test_file),
    ]:
        path = data_dir / fname
        with open(path, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item.model_dump(), ensure_ascii=False) + "\n")


def generate_synthetic(
    n_train: int = 200,
    n_val: int = 50,
    n_test: int = 50,
    seed: int = 42,
) -> tuple[list[Item], list[Item], list[Item]]:
    """
    Minimal synthetic data so the pipeline runs without external data.
    Prices and text are fake but structurally valid for harness and baselines.
    """
    random.seed(seed)
    categories = ["Electronics", "Appliances", "Home"]
    templates = [
        "Compact {adj} {noun} with {feature}.",
        "{adj} {noun} for home use. {feature}.",
    ]
    adjs = ["portable", "premium", "basic", "heavy-duty", "lightweight"]
    nouns = ["device", "unit", "kit", "set", "model"]
    features = ["energy efficient", "easy to install", "durable", "quiet", "fast"]

    def one_item(price_lo: float, price_hi: float) -> Item:
        price = round(random.uniform(price_lo, price_hi), 2)
        t = random.choice(templates).format(
            adj=random.choice(adjs),
            noun=random.choice(nouns),
            feature=random.choice(features),
        )
        full = t * (600 // len(t) + 1)
        return Item(
            title=f"{random.choice(adjs)} {random.choice(nouns)}",
            category=random.choice(categories),
            price=price,
            full=full[:4000],
            weight=random.uniform(0.5, 50.0) if random.random() > 0.3 else 0.0,
            summary=t,
        )

    train = [one_item(1.0, 800.0) for _ in range(n_train)]
    val = [one_item(1.0, 800.0) for _ in range(n_val)]
    test = [one_item(1.0, 800.0) for _ in range(n_test)]
    for i, item in enumerate(train):
        item.id = i
    for i, item in enumerate(val):
        item.id = n_train + i
    for i, item in enumerate(test):
        item.id = n_train + n_val + i
    return train, val, test
