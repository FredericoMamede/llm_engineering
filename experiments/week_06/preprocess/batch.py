"""
Day 2 — Batch preprocessing of items.

Sequential processing with progress; cost-aware (see comments).
Toggle preprocessing via Preprocessor.use_preprocessing.
"""

from typing import Callable, List, Optional

from ..curation.items import Item
from .preprocessor import Preprocessor


def process_items(
    items: List[Item],
    preprocessor: Preprocessor,
    batch_size: Optional[int] = None,
    use_summary_from: str = "full",
) -> None:
    """
    Rewrite item text in place; set item.summary.

    batch_size: not used for parallelization here (sequential); reserved for future
    batch API (e.g. Groq batch). Cost scales linearly with len(items) when preprocessing ON.
    use_summary_from: 'full' or 'summary' — source field for input text.
    """
    source_attr = use_summary_from
    for item in items:
        text = getattr(item, source_attr, None) or item.full or ""
        if not text:
            continue
        item.summary = preprocessor.preprocess(text)


def process_items_with_progress(
    items: List[Item],
    preprocessor: Preprocessor,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> None:
    """Same as process_items; progress_callback(n_done, n_total) if provided."""
    n = len(items)
    for i, item in enumerate(items):
        text = item.full or ""
        if text:
            item.summary = preprocessor.preprocess(text)
        if progress_callback:
            progress_callback(i + 1, n)
