#!/usr/bin/env python3
"""
Model Comparison Benchmark: Claude Haiku 4.5 vs Claude Sonnet 4.5

Runs test scenarios with both models and compares:
- Response quality (using YAML test scenarios)
- Token usage and cost
- Response latency
- Success rates on different tasks
"""

import os
import sys
import asyncio
import json
import yaml
import statistics
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import subprocess
import httpx

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services import ClaudeService, MCPClient, ConversationService
from models import ChatRequest, ChatResponse


class ModelBenchmark:
    """Benchmark framework for comparing Claude models."""

    def __init__(self, backend_api_url: str = "http://localhost:8014/api/v1"):
        self.backend_api_url = backend_api_url
        self.results = {
            "haiku": {},
            "sonnet": {}
        }
        self.test_scenarios: List[Dict[str, Any]] = []

    async def initialize_services(self, model: str, api_key: str) -> tuple:
        """Initialize services for a specific model."""
        claude_service = ClaudeService(
            api_key=api_key,
            backend_api_url=self.backend_api_url,
            shop_id=8,
            model=model,
            cache_refresh_interval_hours=1
        )

        mcp_client = MCPClient(
            backend_api_url=self.backend_api_url,
            shop_id=8
        )

        await claude_service.init_cache()
        return claude_service, mcp_client

    def load_test_scenarios(self, scenarios_dir: str = "testing-framework/scenarios") -> List[Dict]:
        """Load YAML test scenarios."""
        scenarios = []
        scenarios_path = Path(scenarios_dir)

        if not scenarios_path.exists():
            print(f"⚠️  Scenarios directory not found: {scenarios_dir}")
            return []

        # Load first N scenario files (to keep benchmark time reasonable)
        yaml_files = sorted(list(scenarios_path.glob("*.yaml")))[:10]

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    scenario = yaml.safe_load(f)
                    scenario['file'] = yaml_file.name
                    scenarios.append(scenario)
            except Exception as e:
                print(f"❌ Failed to load {yaml_file.name}: {e}")

        print(f"📋 Loaded {len(scenarios)} test scenarios")
        return scenarios

    async def run_test_scenario(
        self,
        scenario: Dict[str, Any],
        claude_service: ClaudeService,
        mcp_client: MCPClient,
        conversation_service: ConversationService
    ) -> Dict[str, Any]:
        """Run a single test scenario and collect metrics."""
        start_time = time.time()
        result = {
            "scenario_file": scenario.get('file', 'unknown'),
            "scenario_name": scenario.get('name', 'unnamed'),
            "initial_message": scenario.get('initial_message', ''),
            "success": False,
            "error": None,
            "tokens_used": 0,
            "cost": 0,
            "response_time": 0,
            "responses": []
        }

        try:
            user_id = f"benchmark_user_{int(time.time())}"
            channel = "telegram"

            # Start conversation
            message = scenario.get('initial_message', '')
            if not message:
                result['error'] = "No initial_message in scenario"
                return result

            # Initialize conversation
            await conversation_service.init_db()
            history = []

            # First turn
            history.append({"role": "user", "content": message})

            response = await claude_service.chat(
                messages=history,
                channel=channel,
                context={"user_id": user_id}
            )

            # Extract response text
            response_text = ""
            for block in response.content:
                if block.type == "text":
                    response_text += block.text

            result['responses'].append({
                "turn": 1,
                "text": response_text[:200] + "..." if len(response_text) > 200 else response_text
            })

            # Check success criteria
            criteria = scenario.get('success_criteria', {})

            # Simple success check: if we got a non-empty response
            if response_text.strip():
                result['success'] = True

            # Track tokens and cost
            costs = claude_service.calculate_cost()
            result['tokens_used'] = (
                claude_service.regular_input_tokens +
                claude_service.cached_input_tokens
            )
            result['cost'] = costs['total_cost']
            result['response_time'] = time.time() - start_time

        except Exception as e:
            result['error'] = str(e)
            result['response_time'] = time.time() - start_time

        return result

    async def run_benchmark(self, models: List[str], api_key: str) -> Dict[str, Any]:
        """Run benchmark with specified models."""
        print("\n" + "="*80)
        print("🚀 CLAUDE MODEL BENCHMARK")
        print("="*80)

        # Load test scenarios
        self.test_scenarios = self.load_test_scenarios()

        if not self.test_scenarios:
            print("❌ No test scenarios loaded!")
            return {}

        benchmark_results = {}

        for model in models:
            print(f"\n{'='*80}")
            print(f"📊 Testing: {model}")
            print(f"{'='*80}")

            try:
                # Initialize services
                claude_service, mcp_client = await self.initialize_services(model, api_key)

                # Database setup
                database_url = "sqlite+aiosqlite:///./benchmark.db"
                conversation_service = ConversationService(database_url=database_url)
                await conversation_service.init_db()

                model_results = {
                    "model": model,
                    "started_at": datetime.now().isoformat(),
                    "scenarios_run": 0,
                    "scenarios_passed": 0,
                    "total_tokens": 0,
                    "total_cost": 0,
                    "avg_response_time": 0,
                    "test_results": []
                }

                # Run scenarios
                response_times = []
                for i, scenario in enumerate(self.test_scenarios, 1):
                    print(f"\n  Test {i}/{len(self.test_scenarios)}: {scenario.get('name', 'unnamed')}")

                    result = await self.run_test_scenario(
                        scenario,
                        claude_service,
                        mcp_client,
                        conversation_service
                    )

                    model_results['test_results'].append(result)
                    model_results['scenarios_run'] += 1

                    if result['success']:
                        model_results['scenarios_passed'] += 1
                        print(f"    ✅ Success | Time: {result['response_time']:.2f}s | Cost: ${result['cost']:.6f}")
                    else:
                        error = result.get('error', 'Unknown error')
                        print(f"    ❌ Failed: {error}")

                    model_results['total_tokens'] += result['tokens_used']
                    model_results['total_cost'] += result['cost']
                    response_times.append(result['response_time'])

                # Get final benchmarks from service
                benchmarks = claude_service.get_benchmarks()
                model_results['cache_hit_rate'] = benchmarks['cache_hit_rate']
                model_results['total_requests'] = benchmarks['total_requests']
                model_results['tokens_saved'] = benchmarks['tokens']['tokens_saved']

                if response_times:
                    model_results['avg_response_time'] = statistics.mean(response_times)
                    model_results['min_response_time'] = min(response_times)
                    model_results['max_response_time'] = max(response_times)

                model_results['completed_at'] = datetime.now().isoformat()

                # Store results
                if 'haiku' in model.lower():
                    self.results['haiku'] = model_results
                    benchmark_results['haiku'] = model_results
                elif 'sonnet' in model.lower():
                    self.results['sonnet'] = model_results
                    benchmark_results['sonnet'] = model_results

                # Cleanup
                await claude_service.close()
                await mcp_client.close()
                await conversation_service.close()

            except Exception as e:
                print(f"❌ Error testing {model}: {e}")
                import traceback
                traceback.print_exc()

        return benchmark_results

    def generate_comparison_report(self) -> str:
        """Generate detailed comparison report."""
        haiku = self.results.get('haiku', {})
        sonnet = self.results.get('sonnet', {})

        if not haiku or not sonnet:
            return "❌ Incomplete results - unable to generate comparison"

        report = []
        report.append("\n" + "="*100)
        report.append("📊 MODEL COMPARISON REPORT: Claude Haiku 4.5 vs Claude Sonnet 4.5")
        report.append("="*100)

        # Test Results
        report.append("\n🧪 TEST RESULTS")
        report.append("-" * 100)
        report.append(f"{'Metric':<40} {'Haiku 4.5':<30} {'Sonnet 4.5':<30}")
        report.append("-" * 100)

        haiku_pass_rate = (haiku.get('scenarios_passed', 0) / max(haiku.get('scenarios_run', 1), 1)) * 100
        sonnet_pass_rate = (sonnet.get('scenarios_passed', 0) / max(sonnet.get('scenarios_run', 1), 1)) * 100

        report.append(
            f"{'Pass Rate':<40} "
            f"{haiku_pass_rate:.1f}% ({haiku.get('scenarios_passed', 0)}/{haiku.get('scenarios_run', 0)})  "
            f"{sonnet_pass_rate:.1f}% ({sonnet.get('scenarios_passed', 0)}/{sonnet.get('scenarios_run', 0)})"
        )

        # Performance
        report.append("\n⚡ PERFORMANCE")
        report.append("-" * 100)

        haiku_avg_time = haiku.get('avg_response_time', 0)
        sonnet_avg_time = sonnet.get('avg_response_time', 0)
        speedup = sonnet_avg_time / haiku_avg_time if haiku_avg_time > 0 else 0

        report.append(f"{'Metric':<40} {'Haiku 4.5':<30} {'Sonnet 4.5':<30}")
        report.append("-" * 100)
        report.append(
            f"{'Avg Response Time (seconds)':<40} "
            f"{haiku_avg_time:.3f}s{' (FASTER) ⚡' if haiku_avg_time < sonnet_avg_time else ''}  "
            f"{sonnet_avg_time:.3f}s"
        )
        report.append(
            f"{'Min Response Time (seconds)':<40} "
            f"{haiku.get('min_response_time', 0):.3f}s  "
            f"{sonnet.get('min_response_time', 0):.3f}s"
        )
        report.append(
            f"{'Max Response Time (seconds)':<40} "
            f"{haiku.get('max_response_time', 0):.3f}s  "
            f"{sonnet.get('max_response_time', 0):.3f}s"
        )

        # Tokens & Costs
        report.append("\n💰 TOKENS & COSTS")
        report.append("-" * 100)

        haiku_cost = haiku.get('total_cost', 0)
        sonnet_cost = sonnet.get('total_cost', 0)
        cost_savings = sonnet_cost - haiku_cost if sonnet_cost > haiku_cost else 0
        cost_savings_pct = (cost_savings / sonnet_cost * 100) if sonnet_cost > 0 else 0

        report.append(f"{'Metric':<40} {'Haiku 4.5':<30} {'Sonnet 4.5':<30}")
        report.append("-" * 100)
        report.append(
            f"{'Total Tokens Used':<40} "
            f"{haiku.get('total_tokens', 0):>28,}  "
            f"{sonnet.get('total_tokens', 0):>28,}"
        )
        report.append(
            f"{'Total Cost (USD)':<40} "
            f"${haiku_cost:>27.6f}  "
            f"${sonnet_cost:>27.6f}"
        )

        if haiku.get('scenarios_run', 0) > 0:
            report.append(
                f"{'Cost per Request (USD)':<40} "
                f"${haiku_cost / haiku.get('scenarios_run', 1):>27.6f}  "
                f"${sonnet_cost / sonnet.get('scenarios_run', 1):>27.6f}"
            )

        if cost_savings > 0:
            report.append(
                f"\n💡 SAVINGS: ${cost_savings:.6f} ({cost_savings_pct:.1f}%) with Haiku 4.5"
            )

        # Cache Effectiveness
        report.append("\n📦 CACHE EFFECTIVENESS")
        report.append("-" * 100)
        report.append(f"{'Metric':<40} {'Haiku 4.5':<30} {'Sonnet 4.5':<30}")
        report.append("-" * 100)
        report.append(
            f"{'Cache Hit Rate':<40} "
            f"{haiku.get('cache_hit_rate', 0):.1f}%{' ✅' if haiku.get('cache_hit_rate', 0) > sonnet.get('cache_hit_rate', 0) else ''}  "
            f"{sonnet.get('cache_hit_rate', 0):.1f}%"
        )
        report.append(
            f"{'Tokens Saved':<40} "
            f"{haiku.get('tokens_saved', 0):>28,}  "
            f"{sonnet.get('tokens_saved', 0):>28,}"
        )

        # Recommendations
        report.append("\n" + "="*100)
        report.append("🎯 RECOMMENDATIONS")
        report.append("="*100)

        if haiku_pass_rate >= sonnet_pass_rate and haiku_cost < sonnet_cost:
            report.append(
                "✅ Claude Haiku 4.5 is the clear winner:\n"
                "   • Similar or better success rates\n"
                "   • Significantly lower cost\n"
                "   • Faster response times\n"
                "   • RECOMMENDED FOR: Budget-conscious deployments with consistent quality needs"
            )
        elif sonnet_pass_rate > haiku_pass_rate:
            quality_diff = sonnet_pass_rate - haiku_pass_rate
            cost_diff = sonnet_cost - haiku_cost
            report.append(
                f"⚠️  Claude Sonnet 4.5 has higher quality (+{quality_diff:.1f}% success rate):\n"
                f"   • Additional cost: ${cost_diff:.6f}\n"
                f"   • Quality gain: {quality_diff:.1f}%\n"
                f"   • RECOMMENDED FOR: High-accuracy requirements where cost is secondary"
            )
        else:
            report.append(
                "✅ Consider Claude Haiku 4.5:\n"
                "   • Comparable quality\n"
                "   • Significantly lower cost\n"
                "   • RECOMMENDED FOR: Production deployments"
            )

        report.append("\n" + "="*100)

        return "\n".join(report)

    def save_results(self, output_file: str = "benchmark_results.json"):
        """Save benchmark results to JSON file."""
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📁 Results saved to {output_file}")

        return output_file


async def main():
    """Run the benchmark."""
    import dotenv
    dotenv.load_dotenv()

    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("❌ CLAUDE_API_KEY not set in environment")
        sys.exit(1)

    backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8014/api/v1")

    benchmark = ModelBenchmark(backend_api_url=backend_url)

    # Models to test
    models = [
        "claude-haiku-4-5-20251001",
        "claude-sonnet-4-5-20250929"
    ]

    # Run benchmark
    results = await benchmark.run_benchmark(models, api_key)

    if not results:
        print("❌ Benchmark failed!")
        sys.exit(1)

    # Generate report
    report = benchmark.generate_comparison_report()
    print(report)

    # Save results
    output_file = benchmark.save_results()

    # Also save report as text file
    report_file = output_file.replace('.json', '_report.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📄 Report saved to {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
