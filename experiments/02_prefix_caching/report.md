# Prefix Caching Benchmark Report

## Test Configuration
- Model: Qwen/Qwen2.5-0.5B-Instruct
- GPU: 8192MB total
- vLLM: v0.14.1
- Prompts per scenario: 10
- High-reuse common prefix: 539 chars
- No-reuse common prefix: 9 chars

## Results Summary

### With APC Enabled (`--enable-prefix-caching`)

| Scenario | Mean TTFT | Min | Max | Stdev |
|----------|-----------|-----|-----|-------|
| High Prefix Reuse | 12.3ms | 12.1ms | 13.0ms | 0.3ms |
| No Prefix Reuse | 18.2ms | 17.2ms | 19.9ms | 0.9ms |

**Improvement: 32.2% faster with prefix reuse**

### With APC Disabled (`--no-enable-prefix-caching`)

| Scenario | Mean TTFT | Min | Max | Stdev |
|----------|-----------|-----|-----|-------|
| High Prefix Reuse | 17.6ms | 17.3ms | 18.3ms | 0.3ms |
| No Prefix Reuse | 18.0ms | 17.3ms | 19.2ms | 0.6ms |

**Improvement: 2.3% faster with prefix reuse** (negligible)

## Analysis

| Metric | APC Enabled | APC Disabled | Difference |
|--------|-------------|--------------|------------|
| High-reuse TTFT | 12.3ms | 17.6ms | **5.3ms faster (30%)** |
| No-reuse TTFT | 18.2ms | 18.0ms | ~same |

### Key Findings

1. **APC provides significant benefit for prefix reuse**: 32% faster TTFT when requests share a common prefix
2. **No penalty for unique prompts**: APC doesn't hurt performance when there's no reuse
3. **Cache working as expected**: With APC disabled, both scenarios have similar TTFT (~17-18ms)

## Raw Output

### APC Enabled
```
======================================================================
Prefix Caching Benchmark
======================================================================

Generating 10 prompts for each scenario...
High-reuse common prefix: 539 chars
No-reuse common prefix: 9 chars

Warming up...

--- High Prefix Reuse (10 requests) ---
Sending requests with shared system prompt...
  [1/10] 13ms
  [2/10] 12ms
  [3/10] 12ms
  [4/10] 12ms
  [5/10] 12ms
  [6/10] 12ms
  [7/10] 12ms
  [8/10] 12ms
  [9/10] 12ms
  [10/10] 12ms
Total time: 913ms

--- No Prefix Reuse (10 requests) ---
Sending requests with unique prefixes...
  [1/10] 20ms
  [2/10] 18ms
  [3/10] 18ms
  [4/10] 18ms
  [5/10] 18ms
  [6/10] 18ms
  [7/10] 17ms
  [8/10] 20ms
  [9/10] 18ms
  [10/10] 18ms
Total time: 945ms

======================================================================
Results
======================================================================

High Prefix Reuse TTFT:
  Min:  12.1ms
  Max:  13.0ms
  Mean: 12.3ms
  Stdev: 0.3ms

No Prefix Reuse TTFT:
  Min:  17.2ms
  Max:  19.9ms
  Mean: 18.2ms
  Stdev: 0.9ms

Comparison:
  High reuse mean: 12.3ms
  No reuse mean:   18.2ms
  Difference:      5.8ms (32.2% faster with reuse)

vLLM Server Metrics (cumulative):
  Avg TTFT: 15.9ms
  Avg E2E:  65.6ms

======================================================================
```

### APC Disabled
```
======================================================================
Prefix Caching Benchmark
======================================================================

Generating 10 prompts for each scenario...
High-reuse common prefix: 539 chars
No-reuse common prefix: 9 chars

Warming up...

--- High Prefix Reuse (10 requests) ---
Sending requests with shared system prompt...
  [1/10] 18ms
  [2/10] 18ms
  [3/10] 17ms
  [4/10] 17ms
  [5/10] 17ms
  [6/10] 17ms
  [7/10] 17ms
  [8/10] 17ms
  [9/10] 17ms
  [10/10] 18ms
Total time: 974ms

--- No Prefix Reuse (10 requests) ---
Sending requests with unique prefixes...
  [1/10] 19ms
  [2/10] 18ms
  [3/10] 17ms
  [4/10] 18ms
  [5/10] 18ms
  [6/10] 18ms
  [7/10] 18ms
  [8/10] 19ms
  [9/10] 18ms
  [10/10] 18ms
Total time: 914ms

======================================================================
Results
======================================================================

High Prefix Reuse TTFT:
  Min:  17.3ms
  Max:  18.3ms
  Mean: 17.6ms
  Stdev: 0.3ms

No Prefix Reuse TTFT:
  Min:  17.3ms
  Max:  19.2ms
  Mean: 18.0ms
  Stdev: 0.6ms

Comparison:
  High reuse mean: 17.6ms
  No reuse mean:   18.0ms
  Difference:      0.4ms (2.3% faster with reuse)

vLLM Server Metrics (cumulative):
  Avg TTFT: 14.1ms
  Avg E2E:  87.8ms

======================================================================
```

## Conclusions

1. **Enable APC for production workloads with shared prefixes**: System prompts, RAG contexts, and batch processing benefit significantly
2. **APC is safe to enable always**: No measurable penalty for unique prompts
3. **Design prompts for reuse**: Put stable content (instructions, context) at the beginning for maximum cache benefit