# 🔬 AI Agent Benchmark Comparison Report

**Generated**: 2025-10-09 13:49:16
**Scenarios Tested**: 40
**Agents Compared**: v1 (port 8000) vs v2 (port 8002)

---

## 📊 Executive Summary

### AI Agent v1 (Current Production)
- ✅ Success Rate: **72.5%** (29/40 passed)
- ⚡ Avg Response Time: **17.69s**
- 💾 Cache Hit Rate: **0.0%**
- 💰 Total Cost: **$0.0**
- 🔄 Avg Turns: **2.0**
- ❌ Total Errors: **38**

### AI Agent v2 (New Version)
- ✅ Success Rate: **75.0%** (30/40 passed)
- ⚡ Avg Response Time: **16.46s**
- 💾 Cache Hit Rate: **0.0%**
- 💰 Total Cost: **$1.18**
- 🔄 Avg Turns: **1.9**
- ❌ Total Errors: **37**

---

## 🎯 Performance Comparison

| Metric | v1 | v2 | Improvement |
|--------|----|----|-------------|
| **Response Time** | 17.69s | 16.46s | **+7.0%** |
| **Cache Hit Rate** | 0.0% | 0.0% | **N/A** |
| **Cost per Test** | $0.0 | $0.0295 | **N/A** |
| **Success Rate** | 72.5% | 75.0% | **+3.4%** |

---

## 📈 Detailed Scenario Results

### Scenario-by-Scenario Comparison


#### 01_budget_customer

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 15.04s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 14.93s | 0.0% | $0.054 | 1 |


#### 02_regular_customer

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 37.43s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 33.44s | 0.0% | $0.0461 | 1 |


#### 03_new_customer_questions

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 6.16s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 25.34s | 0.0% | $0.0178 | 1 |


#### 04_vip_demanding_customer

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 50.28s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 33.55s | 0.0% | $0.0378 | 1 |


#### 05_order_tracking

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 39.95s | 0.0% | $0.0 | 3 |
| v2 | ✅ | 40.28s | 0.0% | $0.0696 | 3 |


#### 06_successful_order

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 28.05s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 25.31s | 0.0% | $0.0444 | 1 |


#### 07_modify_order

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 32.58s | 0.0% | $0.0 | 2 |
| v2 | ✅ | 30.2s | 0.0% | $0.0511 | 2 |


#### 08_order_cancellation

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 29.77s | 0.0% | $0.0 | 2 |
| v2 | ✅ | 26.97s | 0.0% | $0.0365 | 2 |


#### 09_check_working_hours

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 23.35s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 16.98s | 0.0% | $0.0148 | 1 |


#### 10_existing_customer_reorder

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 6.97s | 0.0% | $0.0 | 1 |
| v2 | ❌ | 40.9s | 0.0% | $0.0196 | 2 |


#### 11_track_with_tracking_id

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 52.01s | 0.0% | $0.0 | 4 |
| v2 | ✅ | 37.24s | 0.0% | $0.0622 | 4 |


#### 12_multiple_orders_history

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 34.83s | 0.0% | $0.0 | 2 |
| v2 | ✅ | 36.78s | 0.0% | $0.0671 | 2 |


#### 13_check_availability_before_order

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 31.99s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 42.83s | 0.0% | $0.0712 | 1 |


#### 14_pickup_simple

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 13.85s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 27.81s | 0.0% | $0.0401 | 1 |


#### 14_preview_cost_before_ordering

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 30.44s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 18.77s | 0.0% | $0.0177 | 1 |


#### 15_bestsellers_recommendation

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 45.0s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 27.54s | 0.0% | $0.0362 | 1 |


#### 15_pickup_natural_language

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 31.2s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 10.75s | 0.0% | $0.0308 | 1 |


#### 16_pickup_vs_delivery_comparison

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 34.4s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 27.03s | 0.0% | $0.0646 | 1 |


#### 16_smart_search_budget

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 64.18s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 26.83s | 0.0% | $0.0456 | 1 |


#### 17_save_client_address

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 6.36s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 24.31s | 0.0% | $0.0157 | 1 |


#### 18_client_profile_addresses

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 5.85s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 21.85s | 0.0% | $0.0252 | 1 |


#### 19_cancel_order_reason

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 7.91s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 23.0s | 0.0% | $0.0253 | 1 |


#### 20_realistic_time_selection

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 21.3s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 28.56s | 0.0% | $0.0712 | 1 |


#### 21_delivery_time_validation

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 50.03s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 21.69s | 0.0% | $0.033 | 1 |


#### 22_impossible_delivery_request

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 28.96s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 17.8s | 0.0% | $0.0159 | 1 |


#### 23_urgent_asap_delivery

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 5.78s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 18.96s | 0.0% | $0.0168 | 1 |


#### 24_impossible_delivery_time

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ❌ | 24.4s | 0.0% | $0.0 | 2 |
| v2 | ✅ | 16.15s | 0.0% | $0.0351 | 1 |


#### 25_asap_delivery_madina

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 6.61s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 10.25s | 0.0% | $0.0174 | 1 |


#### 26_e2e_order_creation_with_tracking

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 41.05s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 20.78s | 0.0% | $0.0198 | 1 |


#### 27_e2e_order_update_multiple_fields

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 3.78s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 28.59s | 0.0% | $0.0432 | 1 |


#### 28_e2e_order_cancellation

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ❌ | 103.57s | 0.0% | $0.0 | 5 |
| v2 | ✅ | 12.16s | 0.0% | $0.0357 | 1 |


#### 29_e2e_full_customer_journey

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ❌ | 17.67s | 0.0% | $0.0 | 4 |
| v2 | ❌ | 4.24s | 0.0% | $0.0 | 4 |


#### 30_detailed_bouquet_comparison

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ❌ | 4.34s | 0.0% | $0.0 | 4 |
| v2 | ❌ | 4.15s | 0.0% | $0.0 | 4 |


#### 31_bouquet_with_additions

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ❌ | 4.1s | 0.0% | $0.0 | 4 |
| v2 | ❌ | 4.2s | 0.0% | $0.0 | 4 |


#### 32_price_calculation_verification

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ❌ | 4.26s | 0.0% | $0.0 | 4 |
| v2 | ❌ | 4.22s | 0.0% | $0.0 | 4 |


#### 33_status_check_after_each_update

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ❌ | 4.21s | 0.0% | $0.0 | 4 |
| v2 | ❌ | 4.33s | 0.0% | $0.0 | 4 |


#### 34_track_before_and_after_update

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ❌ | 4.23s | 0.0% | $0.0 | 4 |
| v2 | ❌ | 4.4s | 0.0% | $0.0 | 4 |


#### 35_update_nonexistent_tracking_id

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ❌ | 4.7s | 0.0% | $0.0 | 4 |
| v2 | ❌ | 4.13s | 0.0% | $0.0 | 4 |


#### 36_invalid_date_format

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ❌ | 4.46s | 0.0% | $0.0 | 4 |
| v2 | ❌ | 4.59s | 0.0% | $0.0 | 4 |


#### 37_multiple_updates_same_field

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ❌ | 4.31s | 0.0% | $0.0 | 4 |
| v2 | ❌ | 4.11s | 0.0% | $0.0 | 4 |


---

## 💡 Recommendations

✅ **v2 shows equal or better success rate** - safe to deploy

⚡ **v2 is faster** - improved user experience


---

## 🚀 Next Steps

1. **Review failing scenarios** (if any) and identify root causes
2. **Validate quality** of responses from v2
3. **Update Telegram bot** to use v2 if benchmarks are satisfactory
4. **Monitor production metrics** after deployment
5. **Keep v1 as fallback** during initial v2 rollout

---

## 📝 Notes

- All tests run with identical scenarios and validation criteria
- Cache metrics reflect system warm-up and prompt caching efficiency
- Cost estimates based on Claude API pricing (Sonnet 4.5)
- Response times include network latency and processing time

**Report generated by**: `benchmark_comparison.py`
**Full results**: `benchmark_{timestamp}.json`
