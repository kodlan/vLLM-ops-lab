# Experiment 2: Prefix Caching (Automatic Prefix Caching)

## What is Automatic Prefix Caching (APC)?

When processing a prompt, vLLM computes key-value (KV) pairs for each token in the attention mechanism. With **Automatic Prefix Caching**, vLLM detects when multiple requests share identical prompt prefixes and caches these KV values for reuse.

### Why is this useful?

Many applications use the same system prompt or context for multiple requests:
- Chatbots with fixed system instructions
- RAG applications with shared document context
- Batch processing with common prefixes

Without APC, vLLM recomputes KV values for the shared prefix every time. With APC, subsequent requests skip this computation and reuse cached values.

### How it works

1. **First request**: Full KV computation for entire prompt, prefix cached
2. **Subsequent requests with same prefix**: KV values loaded from cache, only suffix computed
3. **Cache management**: LRU eviction when cache is full

### When APC helps

- **High prefix reuse**: Many requests share long common prefixes → significant TTFT improvement
- **Long prefixes**: Longer shared prefixes = more computation saved

### When APC doesn't help

- **Unique prompts**: Each request has different prefix → no cache hits
- **Short prefixes**: Little computation to save

## vLLM Configuration

APC is controlled with these flags:

```yaml
command:
  # Enable APC (default in recent vLLM versions)
  - --enable-prefix-caching

  # Or disable for comparison
  - --no-prefix-caching
```

## Running This Experiment

```bash
# From project root

# Test with APC enabled (default)
make exp2-up
make health
make exp2-benchmark

# Compare with APC disabled
make exp2-up-no-cache
make exp2-benchmark
```

## What We Measure

1. **TTFT with high prefix reuse**: Same system prompt, different questions
2. **TTFT with no reuse**: Unique prompts each time
3. **Comparison**: APC on vs APC off

## Expected Results

- High-reuse scenario: APC on should show lower TTFT than APC off
- No-reuse scenario: Little to no difference (no cache hits)

## Results

See [report.md](report.md) for benchmark results.