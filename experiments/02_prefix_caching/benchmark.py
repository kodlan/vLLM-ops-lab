"""
Prefix Caching Benchmark - Measures APC effectiveness.

Compares TTFT for:
1. High prefix reuse (same system prompt, different questions)
2. No prefix reuse (unique prompts)
"""

import argparse
import statistics
import sys
import time

sys.path.insert(0, "../..")
from shared import VLLMClient, get_vllm_metrics, timer

from template_builder import generate_high_reuse_prompts, generate_no_reuse_prompts, get_prefix_length


def measure_ttft_batch(
    client: VLLMClient, prompts: list[str], max_tokens: int = 20, show_progress: bool = True
) -> list[float]:
    """
    Measure TTFT for a batch of prompts.

    Returns list of TTFT values in seconds.
    """
    ttfts = []
    total = len(prompts)

    for i, prompt in enumerate(prompts):
        if show_progress:
            print(f"  [{i+1}/{total}]", end=" ", flush=True)

        start = time.perf_counter()
        # Use streaming to measure time to first token
        for _token in client.complete_stream(prompt, max_tokens=max_tokens):
            ttft = time.perf_counter() - start
            ttfts.append(ttft)

            if show_progress:
                print(f"{ttft*1000:.0f}ms", flush=True)

            # Consume rest of stream
            for _ in client.complete_stream(prompt, max_tokens=1):
                pass
            break

    return ttfts


def run_benchmark(client: VLLMClient, num_prompts: int = 10, max_tokens: int = 20):
    """Run the prefix caching benchmark."""

    print("=" * 70)
    print("Prefix Caching Benchmark")
    print("=" * 70)

    if not client.health_check():
        print("ERROR: Server not healthy")
        return None

    # Get initial metrics
    initial_metrics = get_vllm_metrics(client.base_url)

    # Generate prompts
    print(f"\nGenerating {num_prompts} prompts for each scenario...")
    high_reuse_prompts = generate_high_reuse_prompts(num_prompts)
    no_reuse_prompts = generate_no_reuse_prompts(num_prompts)

    prefix_len = get_prefix_length(high_reuse_prompts)
    print(f"High-reuse common prefix: {prefix_len} chars")
    print(f"No-reuse common prefix: {get_prefix_length(no_reuse_prompts)} chars")

    # Warm up
    print("\nWarming up...")
    client.complete("Hello", max_tokens=5)

    # Benchmark high reuse scenario
    print(f"\n--- High Prefix Reuse ({num_prompts} requests) ---")
    print("Sending requests with shared system prompt...")

    with timer() as t_high:
        high_reuse_ttfts = measure_ttft_batch(client, high_reuse_prompts, max_tokens)

    print(f"Total time: {t_high.elapsed_ms:.0f}ms")

    # Brief pause
    time.sleep(1)

    # Benchmark no reuse scenario
    print(f"\n--- No Prefix Reuse ({num_prompts} requests) ---")
    print("Sending requests with unique prefixes...")

    with timer() as t_no:
        no_reuse_ttfts = measure_ttft_batch(client, no_reuse_prompts, max_tokens)

    print(f"Total time: {t_no.elapsed_ms:.0f}ms")

    # Get final metrics from vLLM
    final_metrics = get_vllm_metrics(client.base_url)

    # Calculate statistics
    print("\n" + "=" * 70)
    print("Results")
    print("=" * 70)

    if high_reuse_ttfts:
        print("\nHigh Prefix Reuse TTFT:")
        print(f"  Min:  {min(high_reuse_ttfts) * 1000:.1f}ms")
        print(f"  Max:  {max(high_reuse_ttfts) * 1000:.1f}ms")
        print(f"  Mean: {statistics.mean(high_reuse_ttfts) * 1000:.1f}ms")
        if len(high_reuse_ttfts) > 1:
            print(f"  Stdev: {statistics.stdev(high_reuse_ttfts) * 1000:.1f}ms")

    if no_reuse_ttfts:
        print("\nNo Prefix Reuse TTFT:")
        print(f"  Min:  {min(no_reuse_ttfts) * 1000:.1f}ms")
        print(f"  Max:  {max(no_reuse_ttfts) * 1000:.1f}ms")
        print(f"  Mean: {statistics.mean(no_reuse_ttfts) * 1000:.1f}ms")
        if len(no_reuse_ttfts) > 1:
            print(f"  Stdev: {statistics.stdev(no_reuse_ttfts) * 1000:.1f}ms")

    # Comparison
    if high_reuse_ttfts and no_reuse_ttfts:
        high_mean = statistics.mean(high_reuse_ttfts) * 1000
        no_mean = statistics.mean(no_reuse_ttfts) * 1000
        diff = no_mean - high_mean
        pct = (diff / no_mean) * 100 if no_mean > 0 else 0

        print("\nComparison:")
        print(f"  High reuse mean: {high_mean:.1f}ms")
        print(f"  No reuse mean:   {no_mean:.1f}ms")
        print(f"  Difference:      {diff:.1f}ms ({pct:.1f}% faster with reuse)")

    # vLLM server metrics
    if final_metrics:
        print("\nvLLM Server Metrics (cumulative):")
        if "ttft_avg_ms" in final_metrics:
            print(f"  Avg TTFT: {final_metrics['ttft_avg_ms']:.1f}ms")
        if "e2e_latency_avg_ms" in final_metrics:
            print(f"  Avg E2E:  {final_metrics['e2e_latency_avg_ms']:.1f}ms")

    print("\n" + "=" * 70)

    return {
        "high_reuse_ttft_ms": statistics.mean(high_reuse_ttfts) * 1000 if high_reuse_ttfts else None,
        "no_reuse_ttft_ms": statistics.mean(no_reuse_ttfts) * 1000 if no_reuse_ttfts else None,
    }


def main():
    parser = argparse.ArgumentParser(description="Prefix Caching Benchmark")
    parser.add_argument("--url", default="http://localhost:8000", help="vLLM server URL")
    parser.add_argument("--prompts", type=int, default=10, help="Number of prompts per scenario")
    parser.add_argument("--max-tokens", type=int, default=20, help="Max tokens per response")
    args = parser.parse_args()

    client = VLLMClient(base_url=args.url)
    run_benchmark(client, num_prompts=args.prompts, max_tokens=args.max_tokens)


if __name__ == "__main__":
    main()