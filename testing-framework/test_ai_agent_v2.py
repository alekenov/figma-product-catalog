#!/usr/bin/env python3
"""
Test runner for AI Agent Service V2 via HTTP API.
Simpler than test_orchestrator.py because agent service handles everything internally.
"""

import asyncio
import httpx
import yaml
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from ai_client_service import AIClientService
from config import CLAUDE_API_KEY, SHOP_ID


class AIAgentV2Tester:
    """Test runner for AI Agent Service V2."""

    def __init__(
        self,
        ai_agent_url: str = "http://localhost:8002",
        shop_id: int = SHOP_ID
    ):
        """Initialize tester."""
        self.ai_agent_url = ai_agent_url
        self.shop_id = shop_id
        self.client = httpx.AsyncClient(timeout=120.0)

        # Initialize AI client (plays customer role)
        self.ai_client = AIClientService(
            api_key=CLAUDE_API_KEY,
            shop_id=shop_id
        )

    async def call_agent(self, message: str, user_id: str) -> str:
        """Call AI Agent Service V2."""
        response = await self.client.post(
            f"{self.ai_agent_url}/chat",
            json={
                "message": message,
                "user_id": user_id,
                "channel": "telegram"
            }
        )
        response.raise_for_status()
        result = response.json()
        return result["text"]

    async def run_scenario(self, scenario_file: str) -> Dict[str, Any]:
        """Run a single test scenario."""
        print(f"\n{'='*80}")
        print(f"🧪 Running scenario: {scenario_file}")
        print(f"{'='*80}\n")

        # Load scenario
        scenario_path = Path(__file__).parent / "scenarios" / scenario_file
        with open(scenario_path, 'r', encoding='utf-8') as f:
            scenario = yaml.safe_load(f)

        # Extract scenario details
        scenario_name = scenario["name"]
        initial_message = scenario["initial_message"]
        persona = scenario.get("persona", "budget_customer")
        max_turns = scenario.get("max_turns", 15)

        # Generate unique user ID for this test
        user_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Conversation history
        conversation = []
        turn = 0
        start_time = datetime.now()

        print(f"📝 Scenario: {scenario_name}")
        print(f"👤 Persona: {persona}")
        print(f"🆔 User ID: {user_id}\n")

        # Initial message from client
        print(f"[Turn {turn}] 👤 CLIENT: {initial_message}")
        conversation.append({
            "turn": turn,
            "role": "client",
            "message": initial_message
        })

        # Send to agent
        manager_response = await self.call_agent(initial_message, user_id)
        print(f"[Turn {turn}] 🤖 AGENT: {manager_response[:200]}...\n")
        conversation.append({
            "turn": turn,
            "role": "agent",
            "message": manager_response
        })

        # Continue conversation
        for turn in range(1, max_turns):
            # Client responds
            client_message = await self.ai_client.respond(
                manager_message=manager_response,
                persona=persona,
                conversation_history=conversation
            )

            # Check if client wants to end
            if self._is_conversation_complete(client_message):
                print(f"[Turn {turn}] ✅ Client satisfied, ending conversation")
                break

            print(f"[Turn {turn}] 👤 CLIENT: {client_message}")
            conversation.append({
                "turn": turn,
                "role": "client",
                "message": client_message
            })

            # Agent responds
            manager_response = await self.call_agent(client_message, user_id)
            print(f"[Turn {turn}] 🤖 AGENT: {manager_response[:200]}...\n")
            conversation.append({
                "turn": turn,
                "role": "agent",
                "message": manager_response
            })

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()

        # Generate report
        report = {
            "scenario": scenario_name,
            "scenario_file": scenario_file,
            "persona": persona,
            "user_id": user_id,
            "start_time": start_time.isoformat(),
            "duration_seconds": duration,
            "turns": turn + 1,
            "conversation": conversation,
            "success": turn < max_turns  # Simple success check
        }

        print(f"\n{'='*80}")
        print(f"✅ Scenario completed in {duration:.1f}s ({turn + 1} turns)")
        print(f"{'='*80}\n")

        return report

    def _is_conversation_complete(self, message: str) -> bool:
        """Check if conversation should end."""
        completion_phrases = [
            "спасибо, всё",
            "отлично, спасибо",
            "идеально, спасибо",
            "perfect, thanks",
            "great, thank you",
            "все понятно, спасибо"
        ]
        message_lower = message.lower()
        return any(phrase in message_lower for phrase in completion_phrases)

    async def close(self):
        """Cleanup resources."""
        await self.client.aclose()
        await self.ai_client.close()


async def run_test(scenario_file: str):
    """Run a single test scenario."""
    tester = AIAgentV2Tester()

    try:
        report = await tester.run_scenario(scenario_file)

        # Save report
        report_dir = Path(__file__).parent / "reports" / "ai-agent-v2"
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f"{scenario_file.replace('.yaml', '')}_{timestamp}.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"📊 Report saved: {report_file}")

        return report

    finally:
        await tester.close()


async def run_all_tests():
    """Run all scenarios in the scenarios directory."""
    scenarios_dir = Path(__file__).parent / "scenarios"
    scenario_files = sorted(scenarios_dir.glob("*.yaml"))

    print(f"\n🚀 Running {len(scenario_files)} scenarios...\n")

    reports = []
    for scenario_file in scenario_files:
        try:
            report = await run_test(scenario_file.name)
            reports.append(report)
        except Exception as e:
            print(f"❌ Error in {scenario_file.name}: {str(e)}")
            continue

    # Summary
    successful = sum(1 for r in reports if r["success"])
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY: {successful}/{len(reports)} scenarios passed")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run single scenario
        scenario_file = sys.argv[1]
        asyncio.run(run_test(scenario_file))
    else:
        # Run all scenarios
        asyncio.run(run_all_tests())
