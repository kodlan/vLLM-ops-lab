# vLLM Ops Lab

A hands-on learning project for understanding vLLM as an inference engine through practical experiments.

## Overview

This repo contains a series of experiments that demonstrate key vLLM features:

1. [**Sleep Mode Router**](experiments/01_sleep_mode_router/) - Multi-model switching on a single GPU
2. **Prefix Caching** - Automatic prefix caching (APC) performance analysis
3. **Chunked Prefill** - Long-context fairness and latency optimization
4. **LoRA Hotfix** - Dynamic adapter loading without server restart
5. **Quantization** - GPTQ/AWQ tradeoff matrix
6. **Streaming Torture** - Reliability under cancellation and load

## Requirements

- Docker with NVIDIA GPU support
- NVIDIA GPU with CUDA support
- ~4GB+ VRAM (experiments use small models by default)
- Python 3.10+

## Python Setup

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  

# Install dependencies
pip install -r requirements.txt
```

## Quickstart

```bash
# 1. Setup environment
cp .env.example .env

# 2. Start vLLM server
make infra-up

# 3. Wait for model to load, then check health
make health

# 4. Test with a simple prompt
make test-prompt

# 5. When done
make infra-down
```

## Project Structure

```
vLLM-ops-lab/
├── infra/                    # Base vLLM configuration
├── shared/                   # Shared Python utilities
└── experiments/
    ├── 01_sleep_mode_router/
    ├── 02_prefix_caching/
    ├── 03_chunked_prefill/
    ├── 04_lora_hotfix/
    ├── 05_quantization/
    └── 06_streaming_torture/
```

## Available Make Targets

| Target | Description |
|--------|-------------|
| `make setup` | Create .env from template |
| `make infra-up` | Start base vLLM server |
| `make infra-down` | Stop base server |
| `make infra-logs` | View server logs |
| `make health` | Check server health |
| `make test-prompt` | Send a test completion |

## Configuration

Edit `.env` to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME` | `Qwen/Qwen2.5-0.5B-Instruct` | Model to serve |
| `VLLM_MAX_MODEL_LEN` | `4096` | Max sequence length |
| `VLLM_GPU_MEMORY_UTILIZATION` | `0.8` | GPU memory fraction |