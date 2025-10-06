# Experiment 3: Chunked Prefill (Long-Context Fairness)

## What is Chunked Prefill?

In LLM inference, processing a prompt has two phases:
1. **Prefill**: Process all input tokens, compute KV cache (compute-bound)
2. **Decode**: Generate output tokens one at a time (memory-bound)

Without chunked prefill, a long prompt must complete its entire prefill before other requests can be processed. This causes **head-of-line blocking** - short prompts wait behind long ones.

### The Problem

Imagine these requests arrive:
1. Long prompt (4000 tokens) - arrives first
2. Short prompt (50 tokens) - arrives 10ms later

Without chunked prefill:
- Short prompt waits for entire long prefill (~500ms)
- Short prompt TTFT: ~500ms (unfair!)

With chunked prefill:
- Long prefill is broken into chunks (e.g., 512 tokens each)
- Short prompt can be processed between chunks
- Short prompt TTFT: ~50ms (fair!)

### How it works

1. vLLM breaks long prefills into smaller chunks
2. After each chunk, the scheduler can process other requests
3. Decode operations (token generation) are interleaved
4. Result: Better fairness, more stable tail latencies

## vLLM Configuration

Chunked prefill is controlled with these flags:

```yaml
command:
  # Enable chunked prefill
  - --enable-chunked-prefill

  # Max tokens per prefill chunk (default: 512)
  - --max-num-batched-tokens=512
```

In vLLM V1, chunked prefill is enabled by default.

## Running This Experiment

```bash
# From project root

# Test with chunked prefill enabled
make exp3-up
make health
make exp3-benchmark
make exp3-down

# Compare with chunked prefill disabled
make exp3-up-no-chunk
make health
make exp3-benchmark
make exp3-down
```

## What We Measure

1. **TTFT p95 for short prompts**: Under mixed workload with long prompts
2. **Fairness**: Do short prompts get stuck behind long ones?
3. **Throughput impact**: Any cost to chunking?

## Expected Results

- With chunked prefill: Short prompt TTFT stays low even with long prompts
- Without chunked prefill: Short prompt TTFT spikes when long prompts arrive
- p95 TTFT should be more stable with chunked prefill

## Results

See [report.md](report.md) for benchmark results.