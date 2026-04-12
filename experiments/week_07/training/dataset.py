"""
Week 7 — Build SFT dataset from Items (prompt + completion).

Same format as course Week 7 Day 2: QUESTION + text + PREFIX + completion (rounded price).
"""

import json
import os
from pathlib import Path
from typing import List, Optional

from experiments.week_06.curation import Item
from experiments.week_06.curation.items import PREFIX, QUESTION


def _text_for_item(item: Item) -> str:
    """Use summary or full for prompt text."""
    return item.text_for_model or item.title or ""


def build_prompt_completion(item: Item, do_round: bool = True) -> tuple[str, str]:
    """
    Build (prompt, completion) for one Item.
    prompt = QUESTION + text + PREFIX (no answer); completion = price string.
    """
    text = _text_for_item(item)
    prompt = f"{QUESTION}\n\n{text}\n\n{PREFIX}"
    completion = f"{round(item.price)}.00" if do_round else str(item.price)
    return prompt, completion


def items_to_prompt_completion_list(
    items: List[Item],
    do_round: bool = True,
) -> List[dict]:
    """Convert list of Items to list of {prompt, completion} dicts."""
    out = []
    for item in items:
        prompt, completion = build_prompt_completion(item, do_round=do_round)
        out.append({"prompt": prompt, "completion": completion})
    return out


def save_prompt_completion_jsonl(
    items: List[Item],
    path: Path,
    do_round: bool = True,
) -> None:
    """Write prompt/completion pairs to JSONL for SFT."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pairs = items_to_prompt_completion_list(items, do_round=do_round)
    with open(path, "w") as f:
        for row in pairs:
            f.write(json.dumps(row) + "\n")


def load_data_for_prompts(
    data_source: str = "synthetic",
    hub_dataset: str = "",
    local_dir: Optional[Path] = None,
    seed: int = 42,
) -> tuple[List[Item], List[Item], List[Item]]:
    """
    Load train/val/test using Week 6 loaders.
    data_source: synthetic | hub | local
    """
    if data_source == "hub" and hub_dataset:
        from experiments.week_06.curation import load_from_hf
        return load_from_hf(hub_dataset)
    if data_source == "local" and local_dir and Path(local_dir).exists():
        from experiments.week_06.curation import load_from_local
        return load_from_local(Path(local_dir))
    from experiments.week_06.curation import generate_synthetic
    return generate_synthetic(n_train=300, n_val=80, n_test=100, seed=seed)


def main() -> None:
    """CLI: build prompt/completion JSONL from data (default: synthetic)."""
    import argparse
    p = argparse.ArgumentParser(description="Build SFT prompt/completion dataset from Items")
    p.add_argument("--data_source", default="synthetic", choices=["synthetic", "hub", "local"])
    p.add_argument("--hub_dataset", default=os.environ.get("W6_HUB_DATASET", ""))
    p.add_argument("--local_dir", type=Path, default=None)
    p.add_argument("--out_dir", type=Path, default=Path("data/prompts"))
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    train, val, test = load_data_for_prompts(
        data_source=args.data_source,
        hub_dataset=args.hub_dataset,
        local_dir=args.local_dir,
        seed=args.seed,
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    save_prompt_completion_jsonl(train, args.out_dir / "train.jsonl")
    save_prompt_completion_jsonl(val, args.out_dir / "val.jsonl")
    save_prompt_completion_jsonl(test, args.out_dir / "test.jsonl")
    print(f"Wrote train ({len(train)}), val ({len(val)}), test ({len(test)}) to {args.out_dir}")


if __name__ == "__main__":
    main()
