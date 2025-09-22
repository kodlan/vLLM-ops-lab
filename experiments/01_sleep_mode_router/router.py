"""
Sleep Mode Router - Demonstrates vLLM sleep/wake functionality.

This script shows how to:
1. Put a model to sleep (free GPU memory)
2. Wake a model (restore to GPU)
3. Monitor memory changes during sleep/wake cycles
"""

import argparse
import sys
import time

import requests

# Add project root to path for shared imports
sys.path.insert(0, "../..")
from shared import VLLMClient, get_gpu_memory_mb, timer


class SleepModeRouter:
    """Router that manages sleep/wake cycles for vLLM."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = VLLMClient(base_url=base_url)

    def health_check(self) -> bool:
        """Check if server is healthy."""
        return self.client.health_check()

    def sleep(self, level: int = 1) -> bool:
        """
        Put the model to sleep.

        Args:
            level: Sleep level (1 = offload weights to CPU, 2 = discard weights)

        Returns:
            True if successful, False otherwise.
        """
        try:
            resp = requests.post(f"{self.base_url}/sleep?level={level}", timeout=30)
            if resp.status_code == 200:
                return True
            else:
                print(f"Sleep returned status {resp.status_code}: {resp.text}")
                return False
        except requests.RequestException as e:
            print(f"Sleep request failed: {e}")
            return False

    def wake(self) -> bool:
        """
        Wake the model from sleep.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Note: endpoint is /wake_up not /wake
            resp = requests.post(f"{self.base_url}/wake_up", timeout=120)
            if resp.status_code == 200:
                return True
            else:
                print(f"Wake returned status {resp.status_code}: {resp.text}")
                return False
        except requests.RequestException as e:
            print(f"Wake request failed: {e}")
            return False

    def is_sleeping(self) -> bool:
        """Check if model is currently sleeping."""
        try:
            resp = requests.get(f"{self.base_url}/is_sleeping", timeout=5)
            if resp.status_code == 200:
                return resp.json().get("is_sleeping", False)
        except requests.RequestException:
            pass
        return False

    def complete(self, prompt: str, max_tokens: int = 50) -> str:
        """Generate a completion (model must be awake)."""
        return self.client.complete(prompt, max_tokens=max_tokens)


def demo_sleep_wake_cycle(router: SleepModeRouter):
    """Demonstrate a full sleep/wake cycle with memory monitoring."""

    print("=" * 60)
    print("Sleep Mode Demo")
    print("=" * 60)

    # Check initial state
    if not router.health_check():
        print("ERROR: Server not healthy. Is it running with --enable-sleep-mode?")
        return False

    # Initial memory
    mem_before = get_gpu_memory_mb()
    print(f"\n1. Initial GPU memory: {mem_before['used_mb']}MB used / {mem_before['total_mb']}MB total")

    # Test completion while awake
    print("\n2. Testing completion (model awake)...")
    with timer() as t:
        result = router.complete("Hello, I am", max_tokens=20)
    print(f"   Response: {result.strip()[:50]}...")
    print(f"   Latency: {t.elapsed_ms:.0f}ms")

    # Sleep
    print("\n3. Putting model to sleep...")
    with timer() as t:
        success = router.sleep()
    if success:
        print(f"   Sleep completed in {t.elapsed_ms:.0f}ms")
    else:
        print("   Sleep failed!")
        return False

    # Check memory after sleep
    time.sleep(1)  # Give it a moment to free memory
    mem_sleeping = get_gpu_memory_mb()
    mem_freed = mem_before['used_mb'] - mem_sleeping['used_mb']
    print(f"\n4. GPU memory while sleeping: {mem_sleeping['used_mb']}MB")
    print(f"   Memory freed: {mem_freed}MB")

    # Wake
    print("\n5. Waking model...")
    with timer() as t_wake:
        success = router.wake()
    if success:
        print(f"   Wake completed in {t_wake.elapsed_ms:.0f}ms")
    else:
        print("   Wake failed!")
        return False

    # Check memory after wake
    mem_after = get_gpu_memory_mb()
    print(f"\n6. GPU memory after wake: {mem_after['used_mb']}MB")

    # Test completion after wake
    print("\n7. Testing completion (after wake)...")
    with timer() as t:
        result = router.complete("The weather today is", max_tokens=20)
    print(f"   Response: {result.strip()[:50]}...")
    print(f"   Latency: {t.elapsed_ms:.0f}ms")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Wake latency: {t_wake.elapsed_ms:.0f}ms")
    print(f"Memory freed during sleep: {mem_freed}MB")
    print("=" * 60)

    return True


def main():
    parser = argparse.ArgumentParser(description="Sleep Mode Router Demo")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="vLLM server URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--sleep",
        action="store_true",
        help="Put model to sleep",
    )
    parser.add_argument(
        "--wake",
        action="store_true",
        help="Wake model from sleep",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run full sleep/wake demo cycle",
    )
    args = parser.parse_args()

    router = SleepModeRouter(base_url=args.url)

    if args.sleep:
        print("Putting model to sleep...")
        if router.sleep():
            print("Model is now sleeping")
        else:
            print("Failed to sleep")
            sys.exit(1)

    elif args.wake:
        print("Waking model...")
        if router.wake():
            print("Model is now awake")
        else:
            print("Failed to wake")
            sys.exit(1)

    elif args.demo:
        success = demo_sleep_wake_cycle(router)
        sys.exit(0 if success else 1)

    else:
        # Default: run demo
        success = demo_sleep_wake_cycle(router)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()