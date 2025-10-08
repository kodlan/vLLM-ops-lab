"""
Chunked Prefill Benchmark - Measures fairness under mixed workload.

Sends short and long prompts concurrently to test whether
chunked prefill prevents long prompts from blocking short ones.
"""

import argparse
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, "../..")
from shared import VLLMClient, get_vllm_metrics, timer

from workload_generator import generate_mixed_workload, estimate_tokens


def measure_single_ttft(client: VLLMClient, prompt: str, max_tokens: int = 10) -> float:
    """Measure TTFT for a single prompt. Returns seconds."""
    start = time.perf_counter()
    stream = client.complete_stream(prompt, max_tokens=max_tokens)
    for _token in stream:
        ttft = time.perf_counter() - start
        # Consume rest of stream
        for _ in stream:
            pass
        return ttft
    return time.perf_counter() - start


def run_concurrent_workload(
    client: VLLMClient,
    workload: list[dict],
    max_tokens: int = 10,
    max_workers: int = 8,
) -> list[dict]:
    """
    Run workload concurrently and measure TTFT for each request.

    Returns list of results with 'id', 'length', 'ttft_ms', 'tokens'.
    """
    results = []

    def process_item(item):
        ttft = measure_single_ttft(client, item["prompt"], max_tokens)
        return {
            "id": item["id"],
            "length": item["length"],
            "ttft_ms": ttft * 1000,
            "tokens": estimate_tokens(item["prompt"]),
        }

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_item, item): item for item in workload}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"  {result['id']}: {result['ttft_ms']:.0f}ms (~{result['tokens']} tokens)")

    return results


def calculate_percentile(values: list[float], percentile: int) -> float:
    """Calculate percentile value."""
    if not values:
        return 0
    sorted_values = sorted(values)
    index = int(len(sorted_values) * percentile / 100)
    return sorted_values[min(index, len(sorted_values) - 1)]


def run_benchmark(
    client: VLLMClient,
    num_short: int = 10,
    num_long: int = 3,
    max_tokens: int = 10,
):
    """Run the chunked prefill fairness benchmark."""

    print("=" * 70)
    print("Chunked Prefill Benchmark")
    print("=" * 70)

    if not client.health_check():
        print("ERROR: Server not healthy")
        return None

    # Generate workload
    print(f"\nGenerating workload: {num_short} short + {num_long} long prompts...")
    workload = generate_mixed_workload(
        num_short=num_short,
        num_medium=0,
        num_long=num_long,
        shuffle=True,
    )

    # Show workload order
    print("Request order:")
    for item in workload:
        tokens = estimate_tokens(item["prompt"])
        print(f"  {item['id']}: ~{tokens} tokens")

    # Warm up
    print("\nWarming up...")
    client.complete("Hello", max_tokens=5)

    # Run concurrent workload
    print(f"\nSending {len(workload)} requests concurrently...")
    with timer() as t:
        results = run_concurrent_workload(client, workload, max_tokens)

    print(f"\nTotal time: {t.elapsed_ms:.0f}ms")

    # Analyze results by length
    short_ttfts = [r["ttft_ms"] for r in results if r["length"] == "short"]
    long_ttfts = [r["ttft_ms"] for r in results if r["length"] == "long"]

    # Get vLLM metrics
    metrics = get_vllm_metrics(client.base_url)

    # Print results
    print("\n" + "=" * 70)
    print("Results")
    print("=" * 70)

    if short_ttfts:
        print(f"\nShort Prompt TTFT ({len(short_ttfts)} requests):")
        print(f"  Min:  {min(short_ttfts):.1f}ms")
        print(f"  Max:  {max(short_ttfts):.1f}ms")
        print(f"  Mean: {statistics.mean(short_ttfts):.1f}ms")
        print(f"  p50:  {calculate_percentile(short_ttfts, 50):.1f}ms")
        print(f"  p95:  {calculate_percentile(short_ttfts, 95):.1f}ms")
        if len(short_ttfts) > 1:
            print(f"  Stdev: {statistics.stdev(short_ttfts):.1f}ms")

    if long_ttfts:
        print(f"\nLong Prompt TTFT ({len(long_ttfts)} requests):")
        print(f"  Min:  {min(long_ttfts):.1f}ms")
        print(f"  Max:  {max(long_ttfts):.1f}ms")
        print(f"  Mean: {statistics.mean(long_ttfts):.1f}ms")

    # Fairness analysis
    if short_ttfts and long_ttfts:
        print("\nFairness Analysis:")
        short_mean = statistics.mean(short_ttfts)
        short_p95 = calculate_percentile(short_ttfts, 95)
        long_mean = statistics.mean(long_ttfts)

        print(f"  Short mean vs Long mean: {short_mean:.1f}ms vs {long_mean:.1f}ms")
        print(f"  Short p95: {short_p95:.1f}ms")

        if short_p95 > long_mean:
            print("  WARNING: Short p95 > Long mean (possible head-of-line blocking)")
        else:
            print("  OK: Short prompts not excessively delayed")

    if metrics:
        print("\nvLLM Server Metrics:")
        if "ttft_avg_ms" in metrics:
            print(f"  Avg TTFT: {metrics['ttft_avg_ms']:.1f}ms")
        if "e2e_latency_avg_ms" in metrics:
            print(f"  Avg E2E:  {metrics['e2e_latency_avg_ms']:.1f}ms")

    print("\n" + "=" * 70)

    return {
        "short_ttft_mean_ms": statistics.mean(short_ttfts) if short_ttfts else None,
        "short_ttft_p95_ms": calculate_percentile(short_ttfts, 95) if short_ttfts else None,
        "long_ttft_mean_ms": statistics.mean(long_ttfts) if long_ttfts else None,
    }


def main():
    parser = argparse.ArgumentParser(description="Chunked Prefill Benchmark")
    parser.add_argument("--url", default="http://localhost:8000", help="vLLM server URL")
    parser.add_argument("--short", type=int, default=10, help="Number of short prompts")
    parser.add_argument("--long", type=int, default=3, help="Number of long prompts")
    parser.add_argument("--max-tokens", type=int, default=10, help="Max tokens per response")
    args = parser.parse_args()

    client = VLLMClient(base_url=args.url)
    run_benchmark(client, num_short=args.short, num_long=args.long, max_tokens=args.max_tokens)


if __name__ == "__main__":
    main()