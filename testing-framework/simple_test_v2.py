#!/usr/bin/env python3
"""
Simple test runner for AI Agent Service V2.
Tests basic functionality without complex AI-to-AI interactions.
"""

import asyncio
import httpx
import yaml
import json
import sys
from pathlib import Path
from datetime import datetime


async def test_scenario(scenario_file: str, ai_agent_url: str = "http://localhost:8002"):
    """Test a scenario by sending the initial message."""
    print(f"\n{'='*80}")
    print(f"🧪 Testing scenario: {scenario_file}")
    print(f"{'='*80}\n")

    # Load scenario
    scenario_path = Path(__file__).parent / "scenarios" / scenario_file
    with open(scenario_path, 'r', encoding='utf-8') as f:
        scenario = yaml.safe_load(f)

    scenario_name = scenario["name"]
    initial_message = scenario["initial_message"]

    print(f"📝 Scenario: {scenario_name}")
    print(f"👤 Initial message: {initial_message}\n")

    # Send request to AI Agent
    user_id = f"simple_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        start_time = datetime.now()

        response = await client.post(
            f"{ai_agent_url}/chat",
            json={
                "message": initial_message,
                "user_id": user_id,
                "channel": "telegram"
            }
        )

        duration = (datetime.now() - start_time).total_seconds()

        if response.status_code == 200:
            result = response.json()
            response_text = result["text"]

            print(f"✅ Response received in {duration:.2f}s:")
            print(f"{'-'*80}")
            print(response_text)
            print(f"{'-'*80}\n")

            # Check cache stats
            stats_response = await client.get(f"{ai_agent_url}/cache-stats")
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"📊 Cache Stats:")
                print(f"   Hit rate: {stats['cache_hit_rate']:.1f}%")
                print(f"   Total requests: {stats['total_requests']}")
                print(f"   Tokens saved: {stats['tokens_saved']:,}")
                print(f"   Cost savings: ${stats['cost_savings_usd']:.3f}\n")

            return {"success": True, "duration": duration, "response": response_text}
        else:
            print(f"❌ Error: {response.status_code} - {response.text}\n")
            return {"success": False, "error": response.text}


async def test_all_scenarios():
    """Test all scenarios in the scenarios directory."""
    scenarios_dir = Path(__file__).parent / "scenarios"
    scenario_files = sorted(scenarios_dir.glob("*.yaml"))

    print(f"\n🚀 Testing {len(scenario_files)} scenarios...")

    results = []
    for scenario_file in scenario_files:
        try:
            result = await test_scenario(scenario_file.name)
            results.append({
                "scenario": scenario_file.name,
                **result
            })
        except Exception as e:
            print(f"❌ Error in {scenario_file.name}: {str(e)}\n")
            results.append({
                "scenario": scenario_file.name,
                "success": False,
                "error": str(e)
            })

    # Summary
    successful = sum(1 for r in results if r.get("success", False))
    total_duration = sum(r.get("duration", 0) for r in results)

    print(f"\n{'='*80}")
    print(f"📊 SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Passed: {successful}/{len(results)}")
    print(f"⏱️  Total time: {total_duration:.1f}s")
    print(f"⚡ Avg time: {total_duration/len(results):.1f}s per scenario")
    print(f"{'='*80}\n")

    # Save results
    report_dir = Path(__file__).parent / "reports" / "simple-tests"
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = report_dir / f"test_run_{timestamp}.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"📄 Report saved: {report_file}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test single scenario
        asyncio.run(test_scenario(sys.argv[1]))
    else:
        # Test all scenarios
        asyncio.run(test_all_scenarios())
