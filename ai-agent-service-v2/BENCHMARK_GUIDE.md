# 🚀 Claude Model Benchmark Guide

**Claude Haiku 4.5 vs Claude Sonnet 4.5 Comparison**

## Overview

This benchmark compares two Claude models across different dimensions:
- **Response Quality** - Task completion success rate
- **Performance** - Response latency and throughput
- **Cost Efficiency** - Token usage and pricing
- **Cache Effectiveness** - Prompt caching benefits

## Quick Start

### 1. Install Dependencies

```bash
cd ai-agent-service-v2
pip install -r requirements.txt
pip install pyyaml  # For loading test scenarios
```

### 2. Set Up Environment Variables

Create or update `.env`:
```bash
CLAUDE_API_KEY=sk-ant-...  # Your Anthropic API key
BACKEND_API_URL=http://localhost:8014/api/v1
DEFAULT_SHOP_ID=8
```

### 3. Start Required Services

**Terminal 1: Backend API**
```bash
cd ../backend
python main.py  # Runs on port 8014
```

**Terminal 2: MCP Server**
```bash
cd ../mcp-server
./start.sh  # Runs on port 8000
```

### 4. Run the Benchmark

```bash
cd ai-agent-service-v2
python benchmark_models.py
```

## Output

The benchmark generates two files:

### 1. `benchmark_results.json`
Detailed metrics in JSON format:
```json
{
  "haiku": {
    "model": "claude-haiku-4-5-20251001",
    "scenarios_run": 10,
    "scenarios_passed": 9,
    "total_tokens": 45230,
    "total_cost": 0.0234,
    "avg_response_time": 1.23,
    "cache_hit_rate": 82.3,
    ...
  },
  "sonnet": {
    "model": "claude-sonnet-4-5-20250929",
    "scenarios_run": 10,
    "scenarios_passed": 10,
    "total_tokens": 52100,
    "total_cost": 0.1234,
    "avg_response_time": 2.15,
    "cache_hit_rate": 85.1,
    ...
  }
}
```

### 2. `benchmark_results_report.txt`
Human-readable comparison report with recommendations.

## Key Metrics

### 📊 Test Results
- **Pass Rate**: Percentage of successful test scenarios
- **Scenarios Run**: Number of YAML test scenarios executed

### ⚡ Performance
- **Avg Response Time**: Average latency per request
- **Min/Max Response Time**: Performance range
- **Throughput**: Estimated requests per second

### 💰 Tokens & Costs

**Claude Haiku 4.5 Pricing:**
- Input: $0.80 per 1M tokens
- Output: $4.00 per 1M tokens
- Cache Read: $0.08 per 1M (90% discount)
- Cache Write: $1.00 per 1M (25% premium)

**Claude Sonnet 4.5 Pricing:**
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens
- Cache Read: $0.30 per 1M (90% discount)
- Cache Write: $3.75 per 1M (25% premium)

### 📦 Cache Effectiveness
- **Cache Hit Rate**: Percentage of requests hitting cached blocks
- **Tokens Saved**: Total tokens saved by caching

## Test Scenarios

The benchmark uses YAML scenarios from `testing-framework/scenarios/`:

```yaml
name: "Успешное оформление заказа"
description: "Full order creation flow"
initial_message: "Здравствуйте! Хочу заказать букет роз..."

success_criteria:
  products_shown: true
  order_created: true
  goal_achieved: true
```

Current scenarios include:
- ✅ Budget customer queries
- ✅ Regular order creation
- ✅ Order tracking
- ✅ Delivery validation
- ✅ Payment operations
- ✅ VIP customer requests
- ✅ Complex scenarios (multi-turn conversations)
- ✅ Kaspi Pay integration
- ✅ Order updates and cancellations

## Interpreting Results

### When to Use Haiku 4.5 ✅

```
✅ Use if:
  • Success rate ≥ Sonnet's rate
  • Cost < 50% of Sonnet
  • Response time < 2s
  • Cache hit rate > 70%

🎯 Perfect for:
  • Product browsing queries
  • Simple order tracking
  • FAQ & help requests
  • High-volume, simple tasks
```

### When to Use Sonnet 4.5 ✅

```
✅ Use if:
  • Success rate > Haiku's rate
  • Complex reasoning required
  • Multi-step operations
  • Priority on quality > cost

🎯 Perfect for:
  • Complex VIP requests
  • Multi-turn conversations
  • Kaspi Pay operations
  • Order modifications
```

### Hybrid Strategy 🔄

```
Recommended approach:
1. Use Haiku 4.5 as default (fast + cheap)
2. Detect complexity → Fall back to Sonnet 4.5 if needed
3. Monitor success rates in production
4. Adjust model selection based on real metrics
```

## Customizing the Benchmark

### Add More Test Scenarios

1. Create YAML file in `testing-framework/scenarios/`:
```yaml
name: "My Custom Test"
description: "Tests specific functionality"
initial_message: "User's question or request"
success_criteria:
  some_criteria: true
  another_criteria: false
```

2. Benchmark will automatically pick it up

### Modify Benchmark Parameters

Edit `benchmark_models.py`:

```python
# Change models tested
models = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-5-20250929",
    # Add more here
]

# Limit scenarios (for faster testing)
yaml_files = sorted(list(scenarios_path.glob("*.yaml")))[:5]  # Only first 5
```

### Run Specific Model Only

```python
# In main():
models = ["claude-haiku-4-5-20251001"]  # Only Haiku
# or
models = ["claude-sonnet-4-5-20250929"]  # Only Sonnet
```

## Troubleshooting

### Backend API Not Available
```
❌ Error: Connection refused on port 8014
✅ Solution: Start backend first (./scripts/start-backend.sh)
```

### MCP Server Not Running
```
❌ Error: MCP tools failing
✅ Solution: Start MCP server (mcp-server/start.sh)
```

### Out of Memory
```
❌ Error: sqlite3.OperationalError: database is locked
✅ Solution:
  rm benchmark.db
  python benchmark_models.py
```

### CLAUDE_API_KEY Not Set
```
❌ Error: CLAUDE_API_KEY not set
✅ Solution:
  export CLAUDE_API_KEY=sk-ant-...
  python benchmark_models.py
```

### Scenarios Not Loading
```
❌ Error: No test scenarios loaded
✅ Solution:
  • Check testing-framework/scenarios/ exists
  • Verify YAML files are valid
  • Check file permissions
```

## Performance Optimization Tips

### For Faster Benchmarking:
1. Reduce scenarios: `[:5]` instead of `[:10]`
2. Disable database persistence: Use in-memory SQLite
3. Run in parallel batches (advanced)

### For More Accurate Results:
1. Run multiple times (5-10 iterations)
2. Use real user data scenarios
3. Test during stable network conditions
4. Warm up cache first

## Results Interpretation Examples

### Example 1: Haiku is Better ⭐

```
Pass Rate:          90% (9/10)              92% (10/10)
Avg Response Time:  1.2s ⚡                1.9s
Cost per Request:   $0.0023                $0.0123
Cache Hit Rate:     82%                    85%

✅ RECOMMENDATION: Use Haiku 4.5
   • Similar quality (only 2% difference)
   • 5x faster response time
   • 5x cheaper
   • Excellent cache hit rate
```

### Example 2: Sonnet is Worth It ⭐

```
Pass Rate:          80% (8/10)              95% (10/10) ✅
Avg Response Time:  1.8s                   2.1s
Cost per Request:   $0.0021                $0.0115
Cache Hit Rate:     75%                    88%

⚠️ RECOMMENDATION: Consider Sonnet 4.5
   • 15% higher success rate (important!)
   • 5x increase in cost
   • Only 0.3s slower
   • Better cache efficiency
   • Worth it if quality is critical
```

## Next Steps

1. **Run Benchmark**: `python benchmark_models.py`
2. **Review Report**: Check `benchmark_results_report.txt`
3. **Update main.py**: Adjust model selection based on results
4. **Monitor Production**: Track actual success rates with chosen model
5. **Re-benchmark**: Run again after major changes

## References

- [Claude Models Documentation](https://docs.anthropic.com/en/docs/about-claude/models-overview)
- [Prompt Caching Guide](https://docs.anthropic.com/en/docs/build-a-system-with-claude/prompt-caching)
- [API Pricing](https://www.anthropic.com/pricing)

---

**Happy Benchmarking! 🚀**
