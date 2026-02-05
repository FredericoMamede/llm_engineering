"""
Day 1 — Parse raw product records into canonical Item.

Cleans malformed/missing values, normalizes text, validates price range.
Mirrors course Day 1 logic (McAuley-Lab/Amazon-Reviews-2023 style).
"""

import json
import re
from typing import Any, Optional

from .items import Item


MIN_CHARS = 600
MIN_PRICE = 0.5
MAX_PRICE = 999.49
MAX_TEXT_EACH = 3000
MAX_TEXT_TOTAL = 4000

REMOVALS = [
    "Part Number",
    "Best Sellers Rank",
    "Batteries Included?",
    "Batteries Required?",
    "Item model number",
]


def simplify(text_list: Any) -> str:
    """Single line, limited length; no leading/trailing junk."""
    s = str(text_list).replace("\n", " ").replace("\r", "").replace("\t", "")
    while "  " in s:
        s = s.replace("  ", " ")
    return s.strip()[:MAX_TEXT_EACH]


def scrub(
    title: str,
    description: Any,
    features: Any,
    details: dict,
) -> str:
    """
    Build one cleansed product text: title + description + features + details.
    Removes noisy keys and long part-number-like tokens.
    """
    details = dict(details)
    for key in REMOVALS:
        details.pop(key, None)
    out = title + "\n"
    if description:
        out += simplify(description) + "\n"
    if features:
        out += simplify(features) + "\n"
    if details:
        out += json.dumps(details) + "\n"
    # Remove tokens that look like part numbers (long alphanumeric with both letters and digits).
    out = re.sub(
        r"\b(?=[A-Z0-9]{7,}\b)(?=.*[A-Z])(?=.*\d)[A-Z0-9]+\b",
        "",
        out,
        flags=re.IGNORECASE,
    )
    out = out.strip()[:MAX_TEXT_TOTAL]
    return out


def get_weight(details: dict) -> float:
    """Parse 'Item Weight' string to pounds; 0 if missing or unparseable."""
    weight_str = details.get("Item Weight")
    if not weight_str:
        return 0.0
    parts = weight_str.split()
    if len(parts) < 2:
        return 0.0
    try:
        amount = float(parts[0])
    except ValueError:
        return 0.0
    unit = parts[1].lower()
    if unit == "pounds":
        return amount
    if unit == "ounces":
        return amount / 16.0
    if unit == "grams":
        return amount / 453.592
    if unit == "milligrams":
        return amount / 453_592.0
    if unit == "kilograms":
        return amount / 0.453592
    if len(parts) >= 3 and unit == "hundredths" and parts[2].lower() == "pounds":
        return amount / 100.0
    return 0.0


def parse(datapoint: dict, category: str) -> Optional[Item]:
    """
    One raw record -> Item or None.
    Requires valid price in [MIN_PRICE, MAX_PRICE] and enough text (>= MIN_CHARS after scrub).
    """
    try:
        price = float(datapoint["price"])
    except (ValueError, KeyError, TypeError):
        return None
    if not (MIN_PRICE <= price <= MAX_PRICE):
        return None
    title = datapoint.get("title") or ""
    description = datapoint.get("description")
    features = datapoint.get("features")
    raw_details = datapoint.get("details")
    if raw_details is None:
        details = {}
    elif isinstance(raw_details, dict):
        details = raw_details
    else:
        try:
            details = json.loads(raw_details) if isinstance(raw_details, str) else {}
        except json.JSONDecodeError:
            details = {}
    weight = get_weight(details)
    full = scrub(title, description, features, details)
    if len(full) < MIN_CHARS:
        return None
    return Item(
        title=title,
        category=category,
        price=price,
        full=full,
        weight=weight,
    )
