"""
Workload Generator - Creates mixed short/medium/long prompts.

Used to test chunked prefill fairness by simulating a mixed workload
where short prompts shouldn't be blocked by long ones.
"""

import random


# Base text to repeat for creating long prompts
FILLER_TEXT = """
The quick brown fox jumps over the lazy dog. This is a sample sentence used to pad prompts.
Machine learning models process text token by token, and longer prompts take more time to prefill.
In production systems, we often see a mix of short and long requests arriving concurrently.
"""

# Short questions that complete the prompt
QUESTIONS = [
    "What is 2 + 2?",
    "Name a color.",
    "What is the capital of France?",
    "How many days in a week?",
    "What is the opposite of hot?",
]


def generate_prompt(length: str = "short") -> str:
    """
    Generate a prompt of specified length.

    Args:
        length: "short" (~50 tokens), "medium" (~500 tokens), "long" (~2000 tokens)

    Returns:
        The generated prompt string
    """
    question = random.choice(QUESTIONS)

    if length == "short":
        # ~50 tokens
        return f"Answer briefly: {question}\nAnswer:"

    elif length == "medium":
        # ~500 tokens
        padding = (FILLER_TEXT * 3).strip()
        return f"Context: {padding}\n\nQuestion: {question}\nAnswer:"

    elif length == "long":
        # ~2000 tokens
        padding = (FILLER_TEXT * 15).strip()
        return f"Context: {padding}\n\nQuestion: {question}\nAnswer:"

    else:
        raise ValueError(f"Unknown length: {length}")


def generate_mixed_workload(
    num_short: int = 10,
    num_medium: int = 5,
    num_long: int = 2,
    shuffle: bool = True,
) -> list[dict]:
    """
    Generate a mixed workload of prompts.

    Args:
        num_short: Number of short prompts
        num_medium: Number of medium prompts
        num_long: Number of long prompts
        shuffle: Whether to randomize order

    Returns:
        List of dicts with 'prompt', 'length', and 'id' keys
    """
    workload = []

    for i in range(num_short):
        workload.append({
            "id": f"short-{i+1}",
            "length": "short",
            "prompt": generate_prompt("short"),
        })

    for i in range(num_medium):
        workload.append({
            "id": f"medium-{i+1}",
            "length": "medium",
            "prompt": generate_prompt("medium"),
        })

    for i in range(num_long):
        workload.append({
            "id": f"long-{i+1}",
            "length": "long",
            "prompt": generate_prompt("long"),
        })

    if shuffle:
        random.shuffle(workload)

    return workload


def estimate_tokens(text: str) -> int:
    """Rough estimate of token count (1 token ≈ 4 chars)."""
    return len(text) // 4


if __name__ == "__main__":
    print("=== Prompt Length Examples ===\n")

    for length in ["short", "medium", "long"]:
        prompt = generate_prompt(length)
        tokens = estimate_tokens(prompt)
        print(f"{length.upper()}: ~{tokens} tokens, {len(prompt)} chars")
        print(f"  Preview: {prompt[:80]}...")
        print()

    print("\n=== Mixed Workload Example ===\n")
    workload = generate_mixed_workload(num_short=3, num_medium=2, num_long=1)
    for item in workload:
        tokens = estimate_tokens(item["prompt"])
        print(f"  {item['id']}: ~{tokens} tokens")