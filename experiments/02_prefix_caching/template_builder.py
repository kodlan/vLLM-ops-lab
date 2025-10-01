"""
Template Builder - Generates prompts for prefix caching experiments.

Creates two types of workloads:
1. High reuse: Same long prefix (system prompt) + different suffixes (questions)
2. No reuse: Unique prompts with no shared prefix
"""

import random
import string


# A long system prompt that will be reused across requests
SYSTEM_PROMPT = """You are a helpful AI assistant specialized in answering questions clearly and concisely.

Guidelines:
- Provide accurate, factual information
- Keep responses focused and relevant
- Use simple language when possible
- If uncertain, acknowledge limitations
- Be respectful and professional

Context: You are helping users with general knowledge questions. Answer based on your training data.

Remember to:
1. Read the question carefully
2. Think step by step
3. Provide a clear answer
4. Keep it brief unless detail is requested

"""

# Sample questions to append after the system prompt
QUESTIONS = [
    "What is the capital of France?",
    "How does photosynthesis work?",
    "What is the speed of light?",
    "Who wrote Romeo and Juliet?",
    "What is the largest planet in our solar system?",
    "How many continents are there?",
    "What is the boiling point of water?",
    "Who painted the Mona Lisa?",
    "What is the chemical symbol for gold?",
    "How many days are in a leap year?",
    "What is the tallest mountain on Earth?",
    "Who invented the telephone?",
    "What is the largest ocean?",
    "How many bones are in the human body?",
    "What is the fastest land animal?",
]


def generate_high_reuse_prompts(count: int = 10, prefix: str = SYSTEM_PROMPT) -> list[str]:
    """
    Generate prompts with shared prefix (high cache reuse).

    All prompts share the same long system prompt prefix,
    only the question at the end varies.
    """
    prompts = []
    for i in range(count):
        question = QUESTIONS[i % len(QUESTIONS)]
        prompt = f"{prefix}Question: {question}\nAnswer:"
        prompts.append(prompt)
    return prompts


def generate_no_reuse_prompts(count: int = 10, length: int = 200) -> list[str]:
    """
    Generate unique prompts with no shared prefix (no cache reuse).

    Each prompt is completely unique, so APC provides no benefit.
    """
    prompts = []
    for i in range(count):
        # Generate unique random prefix for each prompt
        unique_prefix = ''.join(random.choices(string.ascii_letters + ' ', k=length))
        question = QUESTIONS[i % len(QUESTIONS)]
        prompt = f"Context: {unique_prefix}\n\nQuestion: {question}\nAnswer:"
        prompts.append(prompt)
    return prompts


def get_prefix_length(prompts: list[str]) -> int:
    """Calculate the common prefix length across prompts."""
    if not prompts:
        return 0

    prefix_len = 0
    min_len = min(len(p) for p in prompts)

    for i in range(min_len):
        chars = set(p[i] for p in prompts)
        if len(chars) == 1:
            prefix_len += 1
        else:
            break

    return prefix_len


if __name__ == "__main__":
    print("=== High Reuse Prompts ===")
    high_reuse = generate_high_reuse_prompts(3)
    prefix_len = get_prefix_length(high_reuse)
    print(f"Common prefix length: {prefix_len} chars")
    print(f"System prompt length: {len(SYSTEM_PROMPT)} chars")
    for i, p in enumerate(high_reuse):
        print(f"\n--- Prompt {i+1} (total {len(p)} chars) ---")
        print(p[:100] + "..." if len(p) > 100 else p)

    print("\n\n=== No Reuse Prompts ===")
    no_reuse = generate_no_reuse_prompts(3)
    prefix_len = get_prefix_length(no_reuse)
    print(f"Common prefix length: {prefix_len} chars")
    for i, p in enumerate(no_reuse):
        print(f"\n--- Prompt {i+1} (total {len(p)} chars) ---")
        print(p[:100] + "..." if len(p) > 100 else p)