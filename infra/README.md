# Infrastructure - Base vLLM Configuration

Base Docker Compose configuration that all experiments extend.

## Usage

```bash
# From project root
make infra-up      # Start vLLM server
make infra-down    # Stop server
make health        # Check if server is ready
```

## vLLM Configuration Options

These flags are set in `docker-compose.base.yml`:

| Flag | Value | Purpose |
|------|-------|---------|
| `--max-model-len` | `${VLLM_MAX_MODEL_LEN}` | Maximum sequence length (prompt + response). Higher = more memory. |
| `--dtype=half` | FP16 | Half precision. Halves memory vs FP32 with minimal quality loss. |
| `--gpu-memory-utilization` | `${VLLM_GPU_MEMORY_UTILIZATION}` | Fraction of GPU memory vLLM can use (0.0-1.0). |
| `--max-num-seqs=16` | 16 | Max concurrent sequences. Controls batching and throughput. |

## Environment Variables

Set in `.env` (copy from `.env.example`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `MODEL_NAME` | `Qwen/Qwen2.5-0.5B-Instruct` | HuggingFace model to load |
| `VLLM_MAX_MODEL_LEN` | `4096` | Max sequence length |
| `VLLM_GPU_MEMORY_UTILIZATION` | `0.8` | GPU memory fraction |
| `HF_TOKEN` | (empty) | Required for gated models only |

## Extending for Experiments

Each experiment creates its own `docker-compose.yml` that adds experiment-specific flags:

```yaml
include:
  - ../../infra/docker-compose.base.yml

services:
  vllm:
    command:
      # ... base flags ...
      - --enable-sleep-mode  # Experiment-specific
```