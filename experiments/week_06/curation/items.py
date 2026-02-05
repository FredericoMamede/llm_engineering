"""
Day 1 — Canonical Item schema.

A single product with price and text fields for regression.
Serializable for train/val/test splits and optional HuggingFace Hub.
"""

from typing import Optional

from pydantic import BaseModel


# Used for prompt-based evaluation (course convention).
PREFIX = "Price is $"
QUESTION = "What does this cost to the nearest dollar?"


class Item(BaseModel):
    """
    One product data point: identity, price (target), and text for prediction.
    full = raw scrubbed text; summary = LLM-rewritten (optional preprocessing).
    """

    title: str
    category: str
    price: float
    full: Optional[str] = None
    weight: Optional[float] = None
    summary: Optional[str] = None
    prompt: Optional[str] = None
    id: Optional[int] = None

    def make_prompt(self, text: str) -> None:
        """Set prompt for evaluation format (question + text + prefix)."""
        self.prompt = f"{QUESTION}\n\n{text}\n\n{PREFIX}{round(self.price)}.00"

    def test_prompt(self) -> str:
        """Return prompt up to prefix (for model input)."""
        if not self.prompt:
            return ""
        return self.prompt.split(PREFIX)[0] + PREFIX

    @property
    def text_for_model(self) -> str:
        """Prefer summary (LLM-rewritten) for models; fallback to full."""
        return self.summary if self.summary else (self.full or "")

    def __repr__(self) -> str:
        return f"<Item {self.title!r} = ${self.price}>"

    @classmethod
    def from_hub(cls, dataset_name: str) -> tuple[list["Item"], list["Item"], list["Item"]]:
        """Load train, validation, test from HuggingFace Hub. Requires datasets + hub auth."""
        from datasets import load_dataset

        ds = load_dataset(dataset_name)
        return (
            [cls.model_validate(row) for row in ds["train"]],
            [cls.model_validate(row) for row in ds["validation"]],
            [cls.model_validate(row) for row in ds["test"]],
        )

    @staticmethod
    def push_to_hub(
        dataset_name: str,
        train: list["Item"],
        val: list["Item"],
        test: list["Item"],
    ) -> None:
        """Push train/val/test to HuggingFace Hub. Requires datasets + hub auth."""
        from datasets import Dataset, DatasetDict

        DatasetDict(
            {
                "train": Dataset.from_list([i.model_dump() for i in train]),
                "validation": Dataset.from_list([i.model_dump() for i in val]),
                "test": Dataset.from_list([i.model_dump() for i in test]),
            }
        ).push_to_hub(dataset_name)
