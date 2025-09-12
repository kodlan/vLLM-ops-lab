"""
OpenAI-compatible client wrapper for vLLM.

vLLM exposes an OpenAI-compatible API on port 8000 by default.
This wrapper provides a simple interface for interacting with it.
"""

import os

import requests


class VLLMClient:
    """Simple client for vLLM's OpenAI-compatible API."""

    def __init__(self, base_url: str = "http://localhost:8000", model: str | None = None):
        """
        Initialize the client.

        Args:
            base_url: vLLM server URL (default: http://localhost:8000)
            model: Model name. If not provided, reads from MODEL_NAME env var.
        """
        self.base_url = base_url.rstrip("/")
        self.model = model or os.getenv("MODEL_NAME", "Qwen/Qwen2.5-0.5B-Instruct")

    def health_check(self) -> bool:
        """
        Check if the vLLM server is healthy.

        Returns:
            True if server responds to health check, False otherwise.
        """
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            return resp.status_code == 200
        except requests.RequestException:
            return False


if __name__ == "__main__":
    client = VLLMClient()
    if client.health_check():
        print("vLLM server is healthy!")
    else:
        print("vLLM server is not available")