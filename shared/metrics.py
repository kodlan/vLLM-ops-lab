"""
Metrics utilities for measuring vLLM performance.
"""

import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator


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


if __name__ == "__main__":
    # Quick test
    with timer() as t:
        time.sleep(0.1)
    print(f"Sleep took {t.elapsed_ms:.2f}ms")