# Sleep Mode Benchmark Report

## Test Configuration
- Model: Qwen/Qwen2.5-0.5B-Instruct
- GPU: 8192MB total
- vLLM: v0.14.1

## Results

### Memory Usage
| State | Memory Used | Notes |
|-------|-------------|-------|
| Awake | 7202MB | Model loaded on GPU |
| Sleeping | 1930MB | Weights offloaded to CPU |
| **Freed** | **5272MB (73.2%)** | Available for other uses |

### Wake Latency
| Metric | Value |
|--------|-------|
| Min | 11ms |
| Max | 11ms |
| Mean | 11ms |
| Stdev | 0ms |

### vLLM Server Metrics
| Metric | Value |
|--------|-------|
| Avg TTFT | 45.5ms |
| Avg E2E Latency | 84.4ms |

## Raw Output

```
======================================================================
Sleep Mode Benchmark
======================================================================

Warming up...

Baseline vLLM metrics: {'requests_running': 0, 'requests_waiting': 0, 'ttft_count': 1, 'ttft_sum': 0.04548454284667969, 'ttft_avg_ms': 45.48454284667969, 'e2e_latency_count': 1, 'e2e_latency_sum': 0.08438873291015625, 'e2e_latency_avg_ms': 84.38873291015625}

GPU Memory (awake): 7202MB used / 8192MB total

Measuring sleep memory...
GPU Memory (sleeping): 1930MB used
Memory freed: 5272MB (73.2%)

Benchmarking wake latency (3 iterations)...
  Iteration 1/3... wake: 11ms
  Iteration 2/3... wake: 11ms
  Iteration 3/3... wake: 11ms

======================================================================
Results
======================================================================

Wake Latency (client-measured):
  Min:    11ms
  Max:    11ms
  Mean:   11ms
  Stdev:  0ms

Memory:
  Awake:    7202MB
  Sleeping: 1930MB
  Freed:    5272MB (73.2%)

vLLM Server Metrics:
  Avg TTFT: 45.5ms
  Avg E2E:  84.4ms

======================================================================
```

## Conclusions

1. **Sleep mode frees significant memory**: 73% of GPU memory freed when sleeping
2. **Wake is very fast**: ~11ms to wake from sleep (vs seconds for cold start)
3. **Production viable**: Low wake latency makes sleep mode practical for idle model management