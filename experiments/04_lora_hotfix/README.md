# Experiment 4: LoRA Hotfix Serving Platform

Demonstrates dynamic LoRA adapter loading/unloading without server restart.

## What is LoRA?

**LoRA (Low-Rank Adaptation)** is a parameter-efficient fine-tuning technique that:
- Freezes the base model weights
- Adds small trainable "adapter" matrices to specific layers
- Produces adapters that are typically 0.1-1% the size of the full model

### Why LoRA for Serving?

| Benefit | Description |
|---------|-------------|
| Memory Efficient | Multiple adapters share one base model in GPU memory |
| Fast Switching | Swap behavior without model reload |
| Multi-Tenant | Different customers can have different adapters |
| Hotfix Capable | Update adapter without downtime |

## vLLM LoRA Support

### Required Configuration

```yaml
environment:
  - VLLM_ALLOW_RUNTIME_LORA_UPDATING=True  # Enable dynamic loading

command:
  - --enable-lora          # Core LoRA support
  - --max-loras=4          # Max adapters in a batch
  - --max-lora-rank=64     # Max rank (8,16,32,64,128,256)
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/load_lora_adapter` | POST | Load adapter dynamically |
| `/v1/unload_lora_adapter` | POST | Unload adapter |
| `/v1/models` | GET | List loaded models/adapters |

### Loading an Adapter

```bash
curl -X POST http://localhost:8000/v1/load_lora_adapter \
  -H "Content-Type: application/json" \
  -d '{"lora_name": "my-adapter", "lora_path": "/adapters/my-adapter"}'
```

### Using an Adapter

Simply use the adapter name as the `model` parameter:

```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "my-adapter",
    "prompt": "Hello",
    "max_tokens": 50
  }'
```

### In-Place Replace (Hotfix)

Replace an adapter without unloading first:

```bash
curl -X POST http://localhost:8000/v1/load_lora_adapter \
  -H "Content-Type: application/json" \
  -d '{
    "lora_name": "my-adapter",
    "lora_path": "/adapters/my-adapter-v2",
    "load_inplace": true
  }'
```

## Experiment Goals

1. **Dynamic Loading**: Load/unload adapters without server restart
2. **Hotfix Capability**: Replace adapter in-place while serving
3. **Stability**: Verify streaming requests complete during swap

## Quick Start

```bash
# Start LoRA-enabled server
make exp4-up

# Wait for server to be ready
make health

# Download sample adapters (optional)
cd experiments/04_lora_hotfix
python setup_adapters.py

# Manage adapters
python adapter_manager.py --list
python adapter_manager.py --load my-adapter /adapters/path

# Run hotfix test
python hotfix_harness.py

# Run benchmarks
make exp4-benchmark

# Stop server
make exp4-down
```

## Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | LoRA-enabled vLLM configuration |
| `adapter_manager.py` | CLI for loading/unloading adapters |
| `setup_adapters.py` | Download sample adapters from HuggingFace |
| `hotfix_harness.py` | Test adapter swap during streaming |
| `benchmark.py` | Measure load/unload/swap latency |
| `report.md` | Results and conclusions |

## Sample Adapters

Available on HuggingFace for Qwen2.5-0.5B:

| Adapter | Description |
|---------|-------------|
| `lewtun/Qwen2.5-0.5B-SFT-LoRA` | General SFT adapter |

## References

- [vLLM LoRA Documentation](https://docs.vllm.ai/en/stable/features/lora.html)
- [LoRARequest API](https://docs.vllm.ai/en/latest/api/vllm/lora/request/)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
