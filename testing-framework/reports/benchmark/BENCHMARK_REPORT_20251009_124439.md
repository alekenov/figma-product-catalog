# 🔬 AI Agent Benchmark Comparison Report

**Generated**: 2025-10-09 12:44:39
**Scenarios Tested**: 40
**Agents Compared**: v1 (port 8000) vs v2 (port 8002)

---

## 📊 Executive Summary

### AI Agent v1 (Current Production)
- ✅ Success Rate: **100.0%** (40/40 passed)
- ⚡ Avg Response Time: **22.07s**
- 💾 Cache Hit Rate: **0.0%**
- 💰 Total Cost: **$0.0**
- 🔄 Avg Turns: **1.2**
- ❌ Total Errors: **0**

### AI Agent v2 (New Version)
- ✅ Success Rate: **97.5%** (39/40 passed)
- ⚡ Avg Response Time: **18.25s**
- 💾 Cache Hit Rate: **0.0%**
- 💰 Total Cost: **$0.0**
- 🔄 Avg Turns: **1.2**
- ❌ Total Errors: **1**

---

## 🎯 Performance Comparison

| Metric | v1 | v2 | Improvement |
|--------|----|----|-------------|
| **Response Time** | 22.07s | 18.25s | **+17.3%** |
| **Cache Hit Rate** | 0.0% | 0.0% | **N/A** |
| **Cost per Test** | $0.0 | $0.0 | **N/A** |
| **Success Rate** | 100.0% | 97.5% | **-2.5%** |

---

## 📈 Detailed Scenario Results

### Scenario-by-Scenario Comparison


#### 01_budget_customer

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 16.69s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 12.25s | 0.0% | $0.0 | 1 |


#### 02_regular_customer

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 10.97s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 23.03s | 0.0% | $0.0 | 1 |


#### 03_new_customer_questions

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 9.65s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 8.61s | 0.0% | $0.0 | 1 |


#### 04_vip_demanding_customer

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 36.71s | 0.0% | $0.0 | 1 |
| v2 | ❌ | 179.41s | 0.0% | $0.0 | 2 |


#### 05_order_tracking

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 43.32s | 0.0% | $0.0 | 3 |
| v2 | ✅ | 31.24s | 0.0% | $0.0 | 3 |


#### 06_successful_order

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 29.58s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 12.35s | 0.0% | $0.0 | 1 |


#### 07_modify_order

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 24.93s | 0.0% | $0.0 | 2 |
| v2 | ✅ | 29.35s | 0.0% | $0.0 | 2 |


#### 08_order_cancellation

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 10.61s | 0.0% | $0.0 | 2 |
| v2 | ✅ | 29.17s | 0.0% | $0.0 | 2 |


#### 09_check_working_hours

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 11.29s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 20.01s | 0.0% | $0.0 | 1 |


#### 10_existing_customer_reorder

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 10.7s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 25.12s | 0.0% | $0.0 | 1 |


#### 11_track_with_tracking_id

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 66.17s | 0.0% | $0.0 | 4 |
| v2 | ✅ | 37.19s | 0.0% | $0.0 | 4 |


#### 12_multiple_orders_history

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 11.81s | 0.0% | $0.0 | 2 |
| v2 | ✅ | 20.72s | 0.0% | $0.0 | 2 |


#### 13_check_availability_before_order

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 9.28s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 29.53s | 0.0% | $0.0 | 1 |


#### 14_pickup_simple

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 4.29s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 14.02s | 0.0% | $0.0 | 1 |


#### 14_preview_cost_before_ordering

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 24.0s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 26.13s | 0.0% | $0.0 | 1 |


#### 15_bestsellers_recommendation

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 30.27s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 21.69s | 0.0% | $0.0 | 1 |


#### 15_pickup_natural_language

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 41.17s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 20.46s | 0.0% | $0.0 | 1 |


#### 16_pickup_vs_delivery_comparison

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 26.35s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 21.19s | 0.0% | $0.0 | 1 |


#### 16_smart_search_budget

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 43.65s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 14.19s | 0.0% | $0.0 | 1 |


#### 17_save_client_address

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 6.26s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 7.52s | 0.0% | $0.0 | 1 |


#### 18_client_profile_addresses

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 5.89s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 15.22s | 0.0% | $0.0 | 1 |


#### 19_cancel_order_reason

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 4.6s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 12.19s | 0.0% | $0.0 | 1 |


#### 20_realistic_time_selection

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 23.04s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 20.89s | 0.0% | $0.0 | 1 |


#### 21_delivery_time_validation

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 25.51s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 20.34s | 0.0% | $0.0 | 1 |


#### 22_impossible_delivery_request

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 25.37s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 13.71s | 0.0% | $0.0 | 1 |


#### 23_urgent_asap_delivery

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 12.89s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 33.98s | 0.0% | $0.0 | 1 |


#### 24_impossible_delivery_time

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 17.23s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 16.16s | 0.0% | $0.0 | 1 |


#### 25_asap_delivery_madina

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 6.33s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 16.53s | 0.0% | $0.0 | 1 |


#### 26_e2e_order_creation_with_tracking

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 34.21s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 16.07s | 0.0% | $0.0 | 1 |


#### 27_e2e_order_update_multiple_fields

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 39.15s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 18.98s | 0.0% | $0.0 | 1 |


#### 28_e2e_order_cancellation

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 24.04s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 14.11s | 0.0% | $0.0 | 1 |


#### 29_e2e_full_customer_journey

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 26.2s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 16.58s | 0.0% | $0.0 | 1 |


#### 30_detailed_bouquet_comparison

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 34.88s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 20.6s | 0.0% | $0.0 | 1 |


#### 31_bouquet_with_additions

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 36.44s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 29.46s | 0.0% | $0.0 | 1 |


#### 32_price_calculation_verification

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 24.25s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 26.48s | 0.0% | $0.0 | 1 |


#### 33_status_check_after_each_update

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 27.89s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 22.25s | 0.0% | $0.0 | 1 |


#### 34_track_before_and_after_update

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 53.83s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 24.06s | 0.0% | $0.0 | 1 |


#### 35_update_nonexistent_tracking_id

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 10.49s | 0.0% | $0.0 | 2 |
| v2 | ✅ | 23.07s | 0.0% | $0.0 | 2 |


#### 36_invalid_date_format

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 53.82s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 16.54s | 0.0% | $0.0 | 1 |


#### 37_multiple_updates_same_field

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | ✅ | 36.8s | 0.0% | $0.0 | 1 |
| v2 | ✅ | 20.74s | 0.0% | $0.0 | 1 |


---

## 💡 Recommendations

⚠️ **v2 has lower success rate** - investigate failures before production

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
