"""
Metrics utilities for measuring vLLM performance.
"""

import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

import requests
from prometheus_client.parser import text_string_to_metric_families


@dataclass
class TimingResult:
    """Result of a timed operation."""

    elapsed_seconds: float = 0.0

    @property
    def elapsed_ms(self) -> float:
        """Elapsed time in milliseconds."""
        return self.elapsed_seconds * 1000


@contextmanager
def timer() -> Iterator[TimingResult]:
    """
    Context manager for measuring elapsed time.

    Usage:
        with timer() as t:
            do_something()
        print(f"Took {t.elapsed_ms:.2f}ms")
    """
    result = TimingResult()
    start = time.perf_counter()
    try:
        yield result
    finally:
        result.elapsed_seconds = time.perf_counter() - start


def get_vllm_metrics(base_url: str = "http://localhost:8000") -> dict | None:
    """
    Fetch and parse vLLM's Prometheus metrics.

    vLLM exposes server-side metrics at /metrics endpoint.
    These are more accurate than client-side measurements
    since they don't include network latency.

    Args:
        base_url: vLLM server URL

    Returns:
        Dict with parsed metrics or None if unavailable.
        Keys include:
        - ttft_avg_ms: Average time to first token (ms)
        - tpot_avg_ms: Average time per output token (ms)
        - e2e_latency_avg_ms: Average end-to-end request latency (ms)
        - requests_total: Total requests processed
        - tokens_total: Total tokens generated
    """
    try:
        resp = requests.get(f"{base_url}/metrics", timeout=5)
        resp.raise_for_status()
        return _parse_prometheus_metrics(resp.text)
    except requests.RequestException:
        return None


def _parse_prometheus_metrics(text: str) -> dict:
    """Parse Prometheus format metrics using prometheus-client library."""
    metrics = {}

    # Metrics we care about and how to process them
    histogram_metrics = {
        "vllm:time_to_first_token_seconds": "ttft",
        "vllm:time_per_output_token_seconds": "tpot",
        "vllm:e2e_request_latency_seconds": "e2e_latency",
    }
    gauge_metrics = {
        "vllm:num_requests_running": "requests_running",
        "vllm:num_requests_waiting": "requests_waiting",
    }
    counter_metrics = {
        "vllm:request_success_total": "requests_success",
    }

    for family in text_string_to_metric_families(text):
        name = family.name

        # Handle histograms (compute average from sum/count)
        if name in histogram_metrics:
            key = histogram_metrics[name]
            for sample in family.samples:
                if sample.name.endswith("_sum"):
                    metrics[f"{key}_sum"] = sample.value
                elif sample.name.endswith("_count"):
                    metrics[f"{key}_count"] = int(sample.value)

            # Compute average in ms
            sum_val = metrics.get(f"{key}_sum", 0)
            count_val = metrics.get(f"{key}_count", 0)
            if count_val > 0:
                metrics[f"{key}_avg_ms"] = (sum_val / count_val) * 1000

        # Handle gauges
        elif name in gauge_metrics:
            key = gauge_metrics[name]
            for sample in family.samples:
                metrics[key] = int(sample.value)

        # Handle counters
        elif name in counter_metrics:
            key = counter_metrics[name]
            for sample in family.samples:
                metrics[key] = int(sample.value)

    return metrics


def get_gpu_memory_mb() -> dict | None:
    """
    Get GPU memory usage via nvidia-smi.

    Returns:
        Dict with 'used_mb', 'total_mb', 'free_mb' or None if unavailable.
    """
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used,memory.total,memory.free",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(",")
            return {
                "used_mb": int(parts[0].strip()),
                "total_mb": int(parts[1].strip()),
                "free_mb": int(parts[2].strip()),
            }
    except (subprocess.SubprocessError, FileNotFoundError, ValueError):
        pass
    return None


if __name__ == "__main__":
    # Test timer
    with timer() as t:
        time.sleep(0.1)
    print(f"Timer test: {t.elapsed_ms:.2f}ms")

    # Test GPU memory
    mem = get_gpu_memory_mb()
    if mem:
        print(f"GPU memory: {mem['used_mb']}MB / {mem['total_mb']}MB")
    else:
        print("GPU memory: not available")

    # Test vLLM metrics (requires server running)
    metrics = get_vllm_metrics()
    if metrics:
        print(f"vLLM metrics: {metrics}")
    else:
        print("vLLM metrics: server not available")