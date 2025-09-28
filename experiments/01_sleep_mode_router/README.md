# Experiment 1: Sleep Mode Router

## What is Sleep Mode?

Sleep Mode is a vLLM feature that allows you to "hibernate" a loaded model to free GPU memory without fully unloading it. When the model wakes up, it's faster than a cold start because weights are restored from CPU RAM rather than loaded from disk.

### Why is this useful?

On a single GPU, you can't keep multiple large models resident simultaneously. Sleep Mode enables:

- **Multi-model serving**: Switch between models on demand (e.g., "summarize" model vs "code" model)
- **Memory efficiency**: Free GPU memory when a model is idle
- **Faster switching**: Wake from sleep is faster than loading from scratch

### How it works

1. **Sleep**: Model weights are offloaded to CPU RAM, KV cache is discarded
2. **Wake**: Weights are copied back to GPU (faster than disk load)
3. **GPU memory**: Freed during sleep, reclaimed on wake

## vLLM Configuration

Sleep mode requires two settings:

```yaml
environment:
  - VLLM_SERVER_DEV_MODE=1    # Required! Sleep API only available in dev mode

command:
  - --enable-sleep-mode       # Enable sleep/wake capability
```

### Why dev mode?

The sleep/wake HTTP endpoints are considered experimental and only exposed when `VLLM_SERVER_DEV_MODE=1` is set.

## Sleep Mode API

When sleep mode is enabled, vLLM exposes these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sleep?level=1` | POST | Put model to sleep (level 1 = offload to CPU) |
| `/sleep?level=2` | POST | Put model to sleep (level 2 = discard weights) |
| `/wake_up` | POST | Wake model, restore to GPU |
| `/is_sleeping` | GET | Check if model is sleeping |

## Running This Experiment

```bash
# From project root
make exp1-up        # Start sleep-mode enabled server
make health         # Wait for healthy
make exp1-benchmark # Run benchmarks
make exp1-down      # Stop server
```

## What We Measure

1. **Wake latency vs cold start**: How much faster is waking vs full reload?
2. **Memory during sleep**: Is GPU memory actually freed?
3. **Request handling**: Do in-flight requests complete before sleep?

## Expected Results

- Wake latency should be significantly lower than cold start
- GPU memory should drop substantially when sleeping
- Server should remain stable through sleep/wake cycles

## Results

See [report.md](report.md) for benchmark results.