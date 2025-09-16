"""
OpenAI-compatible client wrapper for vLLM.

vLLM exposes an OpenAI-compatible API, so we use the official openai library
pointed at our local vLLM server.
"""

import os

import requests
from openai import OpenAI


class VLLMClient:
    """Client for vLLM's OpenAI-compatible API using the openai library."""

    def __init__(self, base_url: str = "http://localhost:8000", model: str | None = None):
        """
        Initialize the client.

        Args:
            base_url: vLLM server URL (default: http://localhost:8000)
            model: Model name. If not provided, reads from MODEL_NAME env var.
        """
        self.base_url = base_url.rstrip("/")
        self.model = model or os.getenv("MODEL_NAME", "Qwen/Qwen2.5-0.5B-Instruct")

        # OpenAI client pointed at vLLM server
        # api_key is required but not used by vLLM
        self.client = OpenAI(
            base_url=f"{self.base_url}/v1",
            api_key="not-needed",
        )

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

    def complete(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a text completion.

        Args:
            prompt: The text prompt to complete
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic, higher = more random)

        Returns:
            The generated text completion
        """
        response = self.client.completions.create(
            model=self.model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].text


if __name__ == "__main__":
    client = VLLMClient()
    if client.health_check():
        print("vLLM server is healthy!")
        result = client.complete("Hello, I am", max_tokens=20)
        print(f"Completion: {result}")
    else:
        print("vLLM server is not available")