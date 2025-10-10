"""
Test Orchestrator - Manages test execution and coordinates AI components.
"""
import asyncio
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

import config
from logger_analyzer import TestLogger
from ai_manager_service import AIManager
from ai_client_service import AIClient

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    datefmt=config.LOG_DATE_FORMAT
)

logger = logging.getLogger(__name__)
console = Console()


class TestOrchestrator:
    """
    Orchestrates test execution between AI Manager and AI Client.
    Loads scenarios, manages dialog flow, and generates reports.
    """

    def __init__(self, scenario_file: str):
        """
        Initialize orchestrator with scenario.

        Args:
            scenario_file: Path to YAML scenario file (relative to scenarios/)
        """
        self.scenario_file = scenario_file
        self.scenario = self._load_scenario(scenario_file)

        # Extract scenario parameters
        self.test_name = self.scenario.get('name', 'Untitled Test')
        self.description = self.scenario.get('description', '')
        self.persona_name = self.scenario.get('persona', 'default_customer')
        self.initial_message = self.scenario.get('initial_message', '')
        self.max_turns = self.scenario.get('max_turns', config.DEFAULT_MAX_TURNS)
        self.timeout = self.scenario.get('timeout_seconds', config.DEFAULT_TIMEOUT_SECONDS)
        self.success_criteria = self.scenario.get('success_criteria', {})

        # Initialize logger
        self.test_logger = TestLogger(
            test_name=self.test_name,
            scenario_name=scenario_file
        )

        # Will be initialized in run()
        self.manager: Optional[AIManager] = None
        self.client: Optional[AIClient] = None

        logger.info(f"🎭 Test orchestrator initialized: {self.test_name}")

    def _load_scenario(self, scenario_file: str) -> Dict[str, Any]:
        """Load scenario from YAML file."""
        scenario_path = config.SCENARIOS_DIR / scenario_file

        if not scenario_path.exists():
            raise FileNotFoundError(f"Scenario not found: {scenario_path}")

        with open(scenario_path, 'r', encoding='utf-8') as f:
            scenario = yaml.safe_load(f)

        logger.info(f"📄 Loaded scenario: {scenario.get('name', scenario_file)}")
        return scenario

    async def run(self) -> Dict[str, Any]:
        """
        Execute the test scenario.

        Returns:
            Test results dictionary
        """
        console.print(Panel.fit(
            f"[bold cyan]{self.test_name}[/bold cyan]\n"
            f"{self.description}",
            title="🚀 Starting Test"
        ))

        start_time = datetime.now()
        result = "failure"
        analysis = {}

        try:
            # Initialize AI components
            self.manager = AIManager(
                test_logger=self.test_logger,
                shop_id=config.SHOP_ID,
                mcp_server_url=config.MCP_SERVER_URL
            )

            self.client = AIClient(
                persona_name=self.persona_name,
                test_logger=self.test_logger,
                initial_goal=self.initial_message
            )

            # Run conversation with timeout
            try:
                conversation_result = await asyncio.wait_for(
                    self._run_conversation(),
                    timeout=self.timeout
                )
                result = conversation_result
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Test timed out after {self.timeout} seconds")
                result = "timeout"

            # Analyze results
            analysis = self._analyze_results()

            # If analysis shows success, update result
            if analysis.get('overall_success', False):
                result = "success"

        except Exception as e:
            logger.error(f"❌ Test failed with exception: {str(e)}", exc_info=True)
            result = "failure"
            analysis = {
                "error": str(e),
                "overall_success": False
            }

        finally:
            # Cleanup
            if self.manager:
                await self.manager.close()

            # Finalize and generate reports
            duration = (datetime.now() - start_time).total_seconds()
            self.test_logger.finalize(
                test_result=result,
                analysis=analysis
            )

            # Print result
            result_emoji = "✅" if result == "success" else "❌" if result == "failure" else "⏱️"
            console.print(Panel.fit(
                f"{result_emoji} [bold]{result.upper()}[/bold]\n"
                f"Duration: {duration:.1f}s\n"
                f"Report: {self.test_logger.report_dir}",
                title="📊 Test Complete"
            ))

        return {
            "result": result,
            "duration": duration,
            "analysis": analysis,
            "report_dir": str(self.test_logger.report_dir)
        }

    async def _run_conversation(self) -> str:
        """
        Run the conversation between client and manager.

        Returns:
            Result: "success" or "failure"
        """
        console.print("\n[bold cyan]💬 Starting Conversation...[/bold cyan]\n")

        # Client sends initial message
        client_message = await self.client.generate_initial_message()

        turn = 1
        while turn <= self.max_turns:
            console.print(f"\n[dim]--- Turn {turn}/{self.max_turns} ---[/dim]")

            # Manager processes and responds
            manager_response = await self.manager.process_message(client_message)

            # Client processes manager's response and decides next action
            next_client_message = await self.client.process_manager_response(manager_response)

            # Check if conversation should continue
            if not next_client_message or not self.client.should_continue(self.max_turns):
                console.print("\n[green]✓ Conversation completed naturally[/green]")
                return "success" if self.client.goal_achieved else "failure"

            client_message = next_client_message
            turn += 1

        console.print("\n[yellow]⚠ Reached maximum turns[/yellow]")
        return "failure"

    def _analyze_results(self) -> Dict[str, Any]:
        """
        Analyze test results against success criteria.

        Returns:
            Analysis dictionary
        """
        analysis = {
            "success_criteria": {},
            "recommendations": [],
            "overall_success": False
        }

        # Check client's perspective
        client_analysis = self.client.get_conversation_analysis()

        # Analyze based on success criteria
        criteria_met = 0
        total_criteria = len(self.success_criteria)

        for criterion, expected_value in self.success_criteria.items():
            if criterion == "order_created":
                # Check if create_order tool was called
                order_created = any(
                    tc.tool_name == "create_order" and tc.success
                    for tc in self.test_logger.tool_calls
                )
                analysis["success_criteria"][criterion] = order_created
                if order_created == expected_value:
                    criteria_met += 1
                else:
                    if expected_value:
                        analysis["recommendations"].append(
                            "Заказ не был создан. Менеджер должен был собрать данные и оформить заказ."
                        )

            elif criterion == "goal_achieved":
                achieved = client_analysis.get('goal_achieved', False)
                analysis["success_criteria"][criterion] = achieved
                if achieved == expected_value:
                    criteria_met += 1
                else:
                    if expected_value:
                        analysis["recommendations"].append(
                            "Цель клиента не достигнута. Менеджер должен был лучше помочь клиенту."
                        )

            elif criterion == "products_shown":
                # Check if list_products was called AND returned non-empty results
                products_shown = any(
                    tc.tool_name == "list_products" and
                    tc.success and
                    tc.result and
                    (isinstance(tc.result, list) and len(tc.result) > 0 or
                     isinstance(tc.result, str) and tc.result != "[]")
                    for tc in self.test_logger.tool_calls
                )
                analysis["success_criteria"][criterion] = products_shown
                if products_shown == expected_value:
                    criteria_met += 1
                else:
                    if expected_value:
                        analysis["recommendations"].append(
                            "Менеджер не показал продукты из каталога или каталог пустой."
                        )

            elif criterion == "price_filter_used":
                # Check if list_products was called with price filters
                price_filter_used = any(
                    tc.tool_name == "list_products" and
                    tc.success and
                    (tc.arguments.get('min_price') is not None or
                     tc.arguments.get('max_price') is not None)
                    for tc in self.test_logger.tool_calls
                )
                analysis["success_criteria"][criterion] = price_filter_used
                if price_filter_used == expected_value:
                    criteria_met += 1
                else:
                    if expected_value:
                        analysis["recommendations"].append(
                            "Менеджер не использовал фильтр по цене при показе продуктов."
                        )

        # Calculate overall success
        if total_criteria > 0:
            success_rate = criteria_met / total_criteria
            analysis["overall_success"] = success_rate >= 0.7  # 70% threshold
        else:
            # No criteria defined, check if client achieved goal
            analysis["overall_success"] = client_analysis.get('goal_achieved', False)

        # Add general recommendations
        if not analysis["overall_success"]:
            analysis["recommendations"].append(
                "Проверьте логи диалога для выявления проблем в коммуникации."
            )

        # Add tool usage statistics
        tool_stats = {}
        for tc in self.test_logger.tool_calls:
            if tc.tool_name not in tool_stats:
                tool_stats[tc.tool_name] = 0
            tool_stats[tc.tool_name] += 1

        analysis["tool_usage"] = tool_stats
        analysis["client_analysis"] = client_analysis

        return analysis


async def run_test(scenario_file: str) -> Dict[str, Any]:
    """
    Convenience function to run a single test.

    Args:
        scenario_file: Scenario YAML filename

    Returns:
        Test results
    """
    orchestrator = TestOrchestrator(scenario_file)
    return await orchestrator.run()


async def run_multiple_tests(scenario_files: list[str]) -> list[Dict[str, Any]]:
    """
    Run multiple tests sequentially.

    Args:
        scenario_files: List of scenario YAML filenames

    Returns:
        List of test results
    """
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(
            f"Running {len(scenario_files)} tests...",
            total=len(scenario_files)
        )

        for i, scenario_file in enumerate(scenario_files, 1):
            progress.update(task, description=f"Test {i}/{len(scenario_files)}: {scenario_file}")

            result = await run_test(scenario_file)
            results.append(result)

            progress.advance(task)

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        console.print("[red]Usage: python test_orchestrator.py <scenario.yaml>[/red]")
        console.print("\nAvailable scenarios:")
        for scenario in config.SCENARIOS_DIR.glob("*.yaml"):
            console.print(f"  - {scenario.name}")
        sys.exit(1)

    scenario = sys.argv[1]
    result = asyncio.run(run_test(scenario))

    sys.exit(0 if result["result"] == "success" else 1)
