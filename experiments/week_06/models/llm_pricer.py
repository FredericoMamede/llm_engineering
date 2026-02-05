"""
Day 5 — LLM-based price prediction: zero-shot and fine-tuned.

Prompt: estimate price from product description; response post-processed to float.
Fine-tuning can regress vs base (see evaluation/FAILURE_MODES.md).
Cost: per-call for zero-shot; fine-tuned has training cost then per-call inference.
"""

from typing import Optional

from ..curation.items import Item


PROMPT_TEMPLATE = "Estimate the price of this product. Respond with the price, no explanation.\n\n{text}"


def messages_for_item(item: Item) -> list[dict]:
    """User message only (no system). Zero-shot and fine-tuned use same format at inference."""
    text = item.text_for_model or item.full or ""
    return [{"role": "user", "content": PROMPT_TEMPLATE.format(text=text)}]


def zero_shot_predictor(
    model_name: str = "openai/gpt-4o-mini",
) -> callable:
    """
    Return (item) -> response string. Harness post_processes to float.
    Cost: one completion per item; token usage depends on description length.
    """
    def predict(item: Item):
        try:
            from litellm import completion
        except ImportError:
            return 0.0
        messages = messages_for_item(item)
        response = completion(model=model_name, messages=messages)
        return response.choices[0].message.content or "0"
    return predict


def fine_tuned_predictor(
    fine_tuned_model_name: str,
    api_key: Optional[str] = None,
) -> callable:
    """
    Return (item) -> response string using OpenAI fine-tuned model.
    fine_tuned_model_name: e.g. ft:gpt-4.1-nano-...:org:...:pricer:...
    Cost: inference only (training is separate). When fine-tuning regresses vs base,
    see FAILURE_MODES.md (overfitting, small data, hyperparameters).
    """
    def predict(item: Item):
        try:
            from openai import OpenAI
        except ImportError:
            return "0"
        client = OpenAI(api_key=api_key)
        messages = messages_for_item(item)
        response = client.chat.completions.create(
            model=fine_tuned_model_name,
            messages=messages,
        )
        return response.choices[0].message.content or "0"
    return predict


def make_jsonl_for_finetuning(items: list[Item], path: str) -> None:
    """
    Write JSONL for OpenAI fine-tuning: each line {"messages": [user, assistant]}.
    Assistant content is price only (e.g. "$123.00"). Does not leak extra info.
    """
    import json
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            user_msg = messages_for_item(item)[0]
            assistant_msg = {"role": "assistant", "content": f"${item.price:.2f}"}
            line = json.dumps({"messages": [user_msg, assistant_msg]}, ensure_ascii=False) + "\n"
            f.write(line)
