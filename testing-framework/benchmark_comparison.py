#!/usr/bin/env python3
"""
Benchmark Comparison: AI Agent v1 vs v2

This script runs identical test scenarios against both AI Agent versions
and generates a comprehensive comparison report.

Usage:
    python3 benchmark_comparison.py
    python3 benchmark_comparison.py --scenarios 26 27 28  # Test specific scenarios
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
import yaml
import httpx
from dataclasses import dataclass, asdict

# Configuration
SHOP_ID = 8  # Default shop ID


@dataclass
class BenchmarkMetrics:
    """Metrics collected for each test run"""
    scenario_name: str
    agent_version: str
    agent_url: str

    # Performance
    total_time_seconds: float
    average_response_time: float
    turns_count: int

    # Cost & Efficiency
    total_input_tokens: int
    total_output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    cache_hit_rate: float
    estimated_cost_usd: float
    cost_savings_usd: float

    # Quality
    success: bool
    validation_passed: bool
    error_count: int
    last_message: str

    # Timestamps
    started_at: str
    completed_at: str


class BenchmarkRunner:
    """Runs benchmark tests on both AI Agent versions"""

    # AI Agent URLs
    V1_URL = "http://localhost:8000"
    V2_URL = "http://localhost:8002"

    # Claude pricing (per 1M tokens)
    INPUT_COST = 3.00
    OUTPUT_COST = 15.00
    CACHE_WRITE_COST = 3.75
    CACHE_READ_COST = 0.30

    def __init__(self, scenarios_dir: str = "scenarios"):
        self.scenarios_dir = Path(scenarios_dir)
        self.results: List[BenchmarkMetrics] = []

    async def run_scenario_on_agent(
        self,
        scenario_path: Path,
        agent_url: str,
        agent_version: str
    ) -> BenchmarkMetrics:
        """Run a single scenario on specified agent"""

        # Load scenario
        with open(scenario_path, 'r', encoding='utf-8') as f:
            scenario = yaml.safe_load(f)

        scenario_name = scenario_path.stem
        print(f"  Running {scenario_name} on {agent_version}...", end=" ", flush=True)

        started_at = datetime.now().isoformat()
        start_time = time.time()

        # Initialize session
        session_id = f"benchmark_{agent_version}_{scenario_name}_{int(time.time())}"

        # Tracking variables
        turns = 0
        total_input_tokens = 0
        total_output_tokens = 0
        cache_creation_tokens = 0
        cache_read_tokens = 0
        error_count = 0
        last_message = ""
        response_times = []

        max_turns = scenario.get('max_turns', 15)
        timeout_seconds = scenario.get('timeout_seconds', 100)

        try:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                # Send initial message
                message = scenario.get('initial_message', '')

                for turn in range(max_turns):
                    turns += 1
                    turn_start = time.time()

                    try:
                        response = await client.post(
                            f"{agent_url}/chat",
                            json={
                                "session_id": session_id,
                                "user_id": f"benchmark_{scenario_name}",
                                "message": message,
                                "shop_id": SHOP_ID
                            }
                        )

                        response.raise_for_status()
                        data = response.json()

                        turn_time = time.time() - turn_start
                        response_times.append(turn_time)

                        # Extract metrics (may not be available in response)
                        usage = data.get('usage', {})
                        total_input_tokens += usage.get('input_tokens', 0)
                        total_output_tokens += usage.get('output_tokens', 0)
                        cache_creation_tokens += usage.get('cache_creation_input_tokens', 0)
                        cache_read_tokens += usage.get('cache_read_input_tokens', 0)

                        # Get response text (different field names)
                        last_message = data.get('text', data.get('response', ''))

                        # Check if conversation is complete
                        if self._is_conversation_complete(scenario, data, turn):
                            break

                        # Generate next message based on flow
                        message = self._generate_next_message(scenario, data, turn)
                        if not message:
                            break

                    except httpx.HTTPError as e:
                        error_count += 1
                        if error_count > 3:
                            break
                        await asyncio.sleep(1)

        except Exception as e:
            print(f"❌ Error: {e}")
            error_count += 1

        total_time = time.time() - start_time
        completed_at = datetime.now().isoformat()

        # Calculate metrics
        cache_hit_rate = (
            cache_read_tokens / (total_input_tokens + cache_creation_tokens + cache_read_tokens)
            if (total_input_tokens + cache_creation_tokens + cache_read_tokens) > 0
            else 0.0
        )

        # Calculate costs
        input_cost = (total_input_tokens / 1_000_000) * self.INPUT_COST
        output_cost = (total_output_tokens / 1_000_000) * self.OUTPUT_COST
        cache_write_cost = (cache_creation_tokens / 1_000_000) * self.CACHE_WRITE_COST
        cache_read_cost = (cache_read_tokens / 1_000_000) * self.CACHE_READ_COST

        estimated_cost = input_cost + output_cost + cache_write_cost + cache_read_cost

        # Cost savings from caching
        cost_without_cache = (
            (total_input_tokens + cache_read_tokens) / 1_000_000 * self.INPUT_COST +
            output_cost
        )
        cost_savings = max(0, cost_without_cache - estimated_cost)

        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Basic validation
        validation_passed = (
            error_count == 0 and
            turns > 0 and
            len(last_message) > 0
        )

        success = validation_passed and self._check_success_criteria(scenario, last_message)

        metrics = BenchmarkMetrics(
            scenario_name=scenario_name,
            agent_version=agent_version,
            agent_url=agent_url,
            total_time_seconds=round(total_time, 2),
            average_response_time=round(avg_response_time, 2),
            turns_count=turns,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            cache_creation_tokens=cache_creation_tokens,
            cache_read_tokens=cache_read_tokens,
            cache_hit_rate=round(cache_hit_rate * 100, 1),
            estimated_cost_usd=round(estimated_cost, 4),
            cost_savings_usd=round(cost_savings, 4),
            success=success,
            validation_passed=validation_passed,
            error_count=error_count,
            last_message=last_message[:200],
            started_at=started_at,
            completed_at=completed_at
        )

        status = "✅" if success else "⚠️"
        print(f"{status} {total_time:.1f}s ({turns} turns)")

        return metrics

    def _is_conversation_complete(self, scenario: Dict, response: Dict, turn: int) -> bool:
        """Check if conversation meets completion criteria"""
        # Simple heuristic: if we've done reasonable turns and got good response
        if turn >= 3 and len(response.get('response', '')) > 50:
            return True
        return False

    def _generate_next_message(self, scenario: Dict, response: Dict, turn: int) -> str:
        """Generate next message based on scenario flow"""
        # Simple implementation - could be enhanced with expected_flow logic
        expected_flow = scenario.get('expected_flow', [])
        if turn < len(expected_flow):
            # Extract message from flow if available
            flow_step = expected_flow[turn]
            if isinstance(flow_step, dict):
                for key in flow_step:
                    if 'update' in key.lower():
                        return "Хочу изменить адрес доставки на Абая 150"
                    elif 'status' in key.lower() or 'track' in key.lower():
                        return "Какой статус заказа?"
        return ""

    def _check_success_criteria(self, scenario: Dict, last_message: str) -> bool:
        """Check if response meets success criteria"""
        success_criteria = scenario.get('success_criteria', [])
        if not success_criteria:
            return True

        # Simple check: message should contain relevant keywords
        for criterion in success_criteria:
            if isinstance(criterion, dict):
                for key, value in criterion.items():
                    if value and not any(word in last_message.lower() for word in key.lower().split('_')):
                        return False
        return True

    async def run_benchmark(self, scenario_names: List[str] = None) -> Dict[str, Any]:
        """Run benchmark on all scenarios"""

        print("🚀 Starting Benchmark Comparison: AI Agent v1 vs v2\n")

        # Get scenarios to test
        if scenario_names:
            scenario_files = [self.scenarios_dir / f"{name}.yaml" for name in scenario_names]
        else:
            scenario_files = sorted(self.scenarios_dir.glob("*.yaml"))

        print(f"📋 Testing {len(scenario_files)} scenarios on both agents\n")

        all_results = []

        for i, scenario_path in enumerate(scenario_files, 1):
            print(f"[{i}/{len(scenario_files)}] {scenario_path.stem}")

            # Run on v1
            try:
                metrics_v1 = await self.run_scenario_on_agent(
                    scenario_path, self.V1_URL, "v1"
                )
                all_results.append(metrics_v1)
            except Exception as e:
                print(f"  ❌ v1 failed: {e}")

            # Run on v2
            try:
                metrics_v2 = await self.run_scenario_on_agent(
                    scenario_path, self.V2_URL, "v2"
                )
                all_results.append(metrics_v2)
            except Exception as e:
                print(f"  ❌ v2 failed: {e}")

            print()  # Blank line between scenarios

        self.results = all_results

        # Generate summary
        summary = self._generate_summary()

        return summary

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate benchmark summary statistics"""

        v1_results = [r for r in self.results if r.agent_version == "v1"]
        v2_results = [r for r in self.results if r.agent_version == "v2"]

        def calc_stats(results: List[BenchmarkMetrics]) -> Dict:
            if not results:
                return {}

            return {
                "total_scenarios": len(results),
                "successful": sum(1 for r in results if r.success),
                "success_rate": round(sum(1 for r in results if r.success) / len(results) * 100, 1),
                "avg_response_time": round(sum(r.average_response_time for r in results) / len(results), 2),
                "avg_total_time": round(sum(r.total_time_seconds for r in results) / len(results), 2),
                "avg_turns": round(sum(r.turns_count for r in results) / len(results), 1),
                "avg_cache_hit_rate": round(sum(r.cache_hit_rate for r in results) / len(results), 1),
                "total_cost": round(sum(r.estimated_cost_usd for r in results), 2),
                "total_cost_savings": round(sum(r.cost_savings_usd for r in results), 2),
                "total_errors": sum(r.error_count for r in results)
            }

        summary = {
            "benchmark_completed_at": datetime.now().isoformat(),
            "total_scenarios_tested": len(self.results) // 2,  # Each scenario run twice
            "v1_stats": calc_stats(v1_results),
            "v2_stats": calc_stats(v2_results),
            "comparison": {
                "response_time_improvement": self._calc_improvement(
                    v1_results, v2_results, "average_response_time", lower_is_better=True
                ),
                "cache_hit_rate_improvement": self._calc_improvement(
                    v1_results, v2_results, "cache_hit_rate", lower_is_better=False
                ),
                "cost_improvement": self._calc_improvement(
                    v1_results, v2_results, "estimated_cost_usd", lower_is_better=True
                ),
                "success_rate_improvement": self._calc_improvement(
                    v1_results, v2_results, "success", lower_is_better=False
                )
            }
        }

        return summary

    def _calc_improvement(
        self,
        v1_results: List[BenchmarkMetrics],
        v2_results: List[BenchmarkMetrics],
        metric: str,
        lower_is_better: bool = True
    ) -> str:
        """Calculate percentage improvement from v1 to v2"""
        if not v1_results or not v2_results:
            return "N/A"

        v1_avg = sum(getattr(r, metric) if not isinstance(getattr(r, metric), bool)
                     else (1 if getattr(r, metric) else 0)
                     for r in v1_results) / len(v1_results)
        v2_avg = sum(getattr(r, metric) if not isinstance(getattr(r, metric), bool)
                     else (1 if getattr(r, metric) else 0)
                     for r in v2_results) / len(v2_results)

        if v1_avg == 0:
            return "N/A"

        improvement = ((v1_avg - v2_avg) / v1_avg * 100) if lower_is_better else ((v2_avg - v1_avg) / v1_avg * 100)
        sign = "+" if improvement > 0 else ""
        return f"{sign}{improvement:.1f}%"

    def save_results(self, output_dir: str = "reports/benchmark"):
        """Save detailed results and summary report"""

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed JSON results
        json_path = output_path / f"benchmark_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "results": [asdict(r) for r in self.results],
                "summary": self._generate_summary()
            }, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Detailed results saved: {json_path}")

        # Generate and save markdown report
        md_path = output_path / f"BENCHMARK_REPORT_{timestamp}.md"
        self._generate_markdown_report(md_path)

        print(f"📄 Benchmark report saved: {md_path}")

    def _generate_markdown_report(self, output_path: Path):
        """Generate detailed markdown comparison report"""

        summary = self._generate_summary()
        v1_stats = summary['v1_stats']
        v2_stats = summary['v2_stats']
        comparison = summary['comparison']

        report = f"""# 🔬 AI Agent Benchmark Comparison Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Scenarios Tested**: {summary['total_scenarios_tested']}
**Agents Compared**: v1 (port 8000) vs v2 (port 8002)

---

## 📊 Executive Summary

### AI Agent v1 (Current Production)
- ✅ Success Rate: **{v1_stats['success_rate']}%** ({v1_stats['successful']}/{v1_stats['total_scenarios']} passed)
- ⚡ Avg Response Time: **{v1_stats['avg_response_time']}s**
- 💾 Cache Hit Rate: **{v1_stats['avg_cache_hit_rate']}%**
- 💰 Total Cost: **${v1_stats['total_cost']}**
- 🔄 Avg Turns: **{v1_stats['avg_turns']}**
- ❌ Total Errors: **{v1_stats['total_errors']}**

### AI Agent v2 (New Version)
- ✅ Success Rate: **{v2_stats['success_rate']}%** ({v2_stats['successful']}/{v2_stats['total_scenarios']} passed)
- ⚡ Avg Response Time: **{v2_stats['avg_response_time']}s**
- 💾 Cache Hit Rate: **{v2_stats['avg_cache_hit_rate']}%**
- 💰 Total Cost: **${v2_stats['total_cost']}**
- 🔄 Avg Turns: **{v2_stats['avg_turns']}**
- ❌ Total Errors: **{v2_stats['total_errors']}**

---

## 🎯 Performance Comparison

| Metric | v1 | v2 | Improvement |
|--------|----|----|-------------|
| **Response Time** | {v1_stats['avg_response_time']}s | {v2_stats['avg_response_time']}s | **{comparison['response_time_improvement']}** |
| **Cache Hit Rate** | {v1_stats['avg_cache_hit_rate']}% | {v2_stats['avg_cache_hit_rate']}% | **{comparison['cache_hit_rate_improvement']}** |
| **Cost per Test** | ${round(v1_stats['total_cost'] / v1_stats['total_scenarios'], 4)} | ${round(v2_stats['total_cost'] / v2_stats['total_scenarios'], 4)} | **{comparison['cost_improvement']}** |
| **Success Rate** | {v1_stats['success_rate']}% | {v2_stats['success_rate']}% | **{comparison['success_rate_improvement']}** |

---

## 📈 Detailed Scenario Results

### Scenario-by-Scenario Comparison

"""

        # Group results by scenario
        scenarios = {}
        for result in self.results:
            if result.scenario_name not in scenarios:
                scenarios[result.scenario_name] = {}
            scenarios[result.scenario_name][result.agent_version] = result

        for scenario_name in sorted(scenarios.keys()):
            v1 = scenarios[scenario_name].get('v1')
            v2 = scenarios[scenario_name].get('v2')

            if v1 and v2:
                v1_status = "✅" if v1.success else "❌"
                v2_status = "✅" if v2.success else "❌"

                report += f"""
#### {scenario_name}

| Agent | Status | Time | Cache Hit | Cost | Turns |
|-------|--------|------|-----------|------|-------|
| v1 | {v1_status} | {v1.total_time_seconds}s | {v1.cache_hit_rate}% | ${v1.estimated_cost_usd} | {v1.turns_count} |
| v2 | {v2_status} | {v2.total_time_seconds}s | {v2.cache_hit_rate}% | ${v2.estimated_cost_usd} | {v2.turns_count} |

"""

        report += f"""
---

## 💡 Recommendations

"""

        # Generate recommendations based on comparison
        if v2_stats['success_rate'] >= v1_stats['success_rate']:
            report += "✅ **v2 shows equal or better success rate** - safe to deploy\n\n"
        else:
            report += "⚠️ **v2 has lower success rate** - investigate failures before production\n\n"

        if v2_stats['avg_response_time'] < v1_stats['avg_response_time']:
            report += "⚡ **v2 is faster** - improved user experience\n\n"

        if v2_stats['avg_cache_hit_rate'] > v1_stats['avg_cache_hit_rate']:
            report += "💾 **v2 has better cache efficiency** - lower operational costs\n\n"

        if v2_stats['total_cost'] < v1_stats['total_cost']:
            saving_per_day = (v1_stats['total_cost'] - v2_stats['total_cost']) * 100  # Assuming 100 conversations/day
            report += f"💰 **v2 is more cost-efficient** - potential savings of ${saving_per_day:.2f}/day\n\n"

        report += """
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
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)


async def main():
    """Main entry point"""

    # Parse command line arguments
    scenario_names = None
    if len(sys.argv) > 1:
        if sys.argv[1] == '--scenarios':
            scenario_names = sys.argv[2:]
        else:
            scenario_names = sys.argv[1:]

    runner = BenchmarkRunner()

    try:
        summary = await runner.run_benchmark(scenario_names)

        # Print summary
        print("\n" + "="*70)
        print("📊 BENCHMARK SUMMARY")
        print("="*70)
        print(f"\nv1 Performance:")
        print(f"  Success Rate: {summary['v1_stats']['success_rate']}%")
        print(f"  Avg Response Time: {summary['v1_stats']['avg_response_time']}s")
        print(f"  Cache Hit Rate: {summary['v1_stats']['avg_cache_hit_rate']}%")
        print(f"  Total Cost: ${summary['v1_stats']['total_cost']}")

        print(f"\nv2 Performance:")
        print(f"  Success Rate: {summary['v2_stats']['success_rate']}%")
        print(f"  Avg Response Time: {summary['v2_stats']['avg_response_time']}s")
        print(f"  Cache Hit Rate: {summary['v2_stats']['avg_cache_hit_rate']}%")
        print(f"  Total Cost: ${summary['v2_stats']['total_cost']}")

        print(f"\nComparison:")
        print(f"  Response Time: {summary['comparison']['response_time_improvement']}")
        print(f"  Cache Hit Rate: {summary['comparison']['cache_hit_rate_improvement']}")
        print(f"  Cost: {summary['comparison']['cost_improvement']}")
        print(f"  Success Rate: {summary['comparison']['success_rate_improvement']}")

        # Save results
        runner.save_results()

        print("\n✅ Benchmark complete!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        if runner.results:
            print("Saving partial results...")
            runner.save_results()
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
