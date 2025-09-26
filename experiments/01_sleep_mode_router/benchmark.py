"""
Sleep Mode Benchmarks - Measures wake latency and memory savings.

Uses vLLM's server-side metrics for accurate timing measurements.
"""

import argparse
import statistics
import sys
import time

# Add project root to path for shared imports
sys.path.insert(0, "../..")
from shared import get_gpu_memory_mb, get_vllm_metrics, timer

from router import SleepModeRouter


def run_benchmark(router: SleepModeRouter, iterations: int = 3):
    """Run the sleep mode benchmark suite."""

    print("=" * 70)
    print("Sleep Mode Benchmark")
    print("=" * 70)

    # Check server is ready
    if not router.health_check():
        print("ERROR: Server not healthy")
        return None

    # Warm up
    print("\nWarming up...")
    router.complete("Hello", max_tokens=10)

    # Get baseline metrics from vLLM
    baseline_metrics = get_vllm_metrics(router.base_url)
    print(f"\nBaseline vLLM metrics: {baseline_metrics}")

    # Initial memory
    mem_awake = get_gpu_memory_mb()
    print(f"\nGPU Memory (awake): {mem_awake['used_mb']}MB used / {mem_awake['total_mb']}MB total")

    # Measure memory while sleeping
    print("\nMeasuring sleep memory...")
    if router.sleep():
        time.sleep(1)
        mem_sleeping = get_gpu_memory_mb()
        print(f"GPU Memory (sleeping): {mem_sleeping['used_mb']}MB used")
        mem_freed = mem_awake['used_mb'] - mem_sleeping['used_mb']
        print(f"Memory freed: {mem_freed}MB ({mem_freed / mem_awake['used_mb'] * 100:.1f}%)")
        router.wake()
        time.sleep(1)
    else:
        print("Failed to sleep for memory measurement")
        mem_sleeping = None
        mem_freed = 0

    # Benchmark wake latency
    print(f"\nBenchmarking wake latency ({iterations} iterations)...")
    wake_latencies = []

    for i in range(iterations):
        print(f"  Iteration {i + 1}/{iterations}...", end=" ", flush=True)

        # Sleep first
        if not router.sleep():
            print("sleep failed")
            continue

        time.sleep(0.5)

        # Measure wake time
        with timer() as t:
            success = router.wake()

        if success:
            wake_latencies.append(t.elapsed_seconds)
            print(f"wake: {t.elapsed_ms:.0f}ms")
        else:
            print("wake failed")

        time.sleep(0.5)

    # Get final metrics from vLLM
    final_metrics = get_vllm_metrics(router.base_url)

    # Print results
    print("\n" + "=" * 70)
    print("Results")
    print("=" * 70)

    if wake_latencies:
        print(f"\nWake Latency (client-measured):")
        print(f"  Min:    {min(wake_latencies) * 1000:.0f}ms")
        print(f"  Max:    {max(wake_latencies) * 1000:.0f}ms")
        print(f"  Mean:   {statistics.mean(wake_latencies) * 1000:.0f}ms")
        if len(wake_latencies) > 1:
            print(f"  Stdev:  {statistics.stdev(wake_latencies) * 1000:.0f}ms")

    print(f"\nMemory:")
    print(f"  Awake:    {mem_awake['used_mb']}MB")
    if mem_sleeping:
        print(f"  Sleeping: {mem_sleeping['used_mb']}MB")
        print(f"  Freed:    {mem_freed}MB ({mem_freed / mem_awake['used_mb'] * 100:.1f}%)")

    if final_metrics:
        print(f"\nvLLM Server Metrics:")
        if "ttft_avg_ms" in final_metrics:
            print(f"  Avg TTFT: {final_metrics['ttft_avg_ms']:.1f}ms")
        if "e2e_latency_avg_ms" in final_metrics:
            print(f"  Avg E2E:  {final_metrics['e2e_latency_avg_ms']:.1f}ms")

    print("\n" + "=" * 70)

    return {
        "wake_latency_ms": statistics.mean(wake_latencies) * 1000 if wake_latencies else None,
        "memory_freed_mb": mem_freed,
        "memory_awake_mb": mem_awake['used_mb'],
        "memory_sleeping_mb": mem_sleeping['used_mb'] if mem_sleeping else None,
    }


def main():
    parser = argparse.ArgumentParser(description="Sleep Mode Benchmark")
    parser.add_argument("--url", default="http://localhost:8000", help="vLLM server URL")
    parser.add_argument("--iterations", type=int, default=3, help="Number of iterations")
    args = parser.parse_args()

    router = SleepModeRouter(base_url=args.url)
    run_benchmark(router, iterations=args.iterations)


if __name__ == "__main__":
    main()