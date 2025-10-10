"""
Logger and Analyzer for AI Testing Framework.
Records all interactions and generates detailed reports.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from rich.console import Console
from rich.table import Table

import config

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class MessageLog:
    """Single message in conversation."""
    timestamp: str
    sender: str  # "client" or "manager"
    message_type: str  # "text", "thinking", "tool_call", "tool_result"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCallLog:
    """Single MCP tool call."""
    timestamp: str
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Any] = None
    latency_ms: Optional[float] = None
    success: bool = True
    error: Optional[str] = None


@dataclass
class APICallLog:
    """Single backend API call."""
    timestamp: str
    method: str  # GET, POST, PUT, DELETE
    endpoint: str
    params: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    status_code: Optional[int] = None
    response: Optional[Any] = None
    latency_ms: Optional[float] = None
    success: bool = True
    error: Optional[str] = None


class TestLogger:
    """
    Comprehensive logger for test execution.
    Records messages, tool calls, API calls, and generates reports.
    """

    def __init__(self, test_name: str, scenario_name: str):
        self.test_name = test_name
        self.scenario_name = scenario_name
        self.start_time = datetime.now()

        # Storage for logs
        self.messages: List[MessageLog] = []
        self.tool_calls: List[ToolCallLog] = []
        self.api_calls: List[APICallLog] = []

        # Test metadata
        self.metadata = {
            "test_name": test_name,
            "scenario": scenario_name,
            "start_time": self.start_time.isoformat(),
        }

        # Create report directory
        timestamp = self.start_time.strftime("%Y_%m_%d_%H_%M_%S")
        self.report_dir = config.REPORTS_DIR / timestamp
        self.report_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📊 Test logger initialized: {test_name}")
        logger.info(f"📁 Report directory: {self.report_dir}")

    def log_message(
        self,
        sender: str,
        message_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log a conversation message."""
        msg = MessageLog(
            timestamp=datetime.now().isoformat(),
            sender=sender,
            message_type=message_type,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(msg)

        # Console output
        emoji = "👤" if sender == "client" else "🤖"
        type_emoji = {
            "text": "💬",
            "thinking": "🤔",
            "tool_call": "🔧",
            "tool_result": "📤"
        }.get(message_type, "📝")

        console.print(f"{emoji} {type_emoji} [{sender.upper()}] {message_type}: {content[:100]}...")

    def log_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Optional[Any] = None,
        latency_ms: Optional[float] = None,
        success: bool = True,
        error: Optional[str] = None
    ):
        """Log an MCP tool call."""
        call = ToolCallLog(
            timestamp=datetime.now().isoformat(),
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            latency_ms=latency_ms,
            success=success,
            error=error
        )
        self.tool_calls.append(call)

        # Console output
        status = "✅" if success else "❌"
        console.print(f"🔧 {status} Tool: {tool_name} ({latency_ms:.0f}ms)" if latency_ms else f"🔧 {status} Tool: {tool_name}")

    def log_api_call(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        response: Optional[Any] = None,
        latency_ms: Optional[float] = None,
        success: bool = True,
        error: Optional[str] = None
    ):
        """Log a backend API call."""
        call = APICallLog(
            timestamp=datetime.now().isoformat(),
            method=method,
            endpoint=endpoint,
            params=params,
            body=body,
            status_code=status_code,
            response=response,
            latency_ms=latency_ms,
            success=success,
            error=error
        )
        self.api_calls.append(call)

        # Console output
        status = "✅" if success else "❌"
        console.print(f"🌐 {status} {method} {endpoint} [{status_code}] ({latency_ms:.0f}ms)" if latency_ms else f"🌐 {status} {method} {endpoint}")

    def finalize(self, test_result: str, analysis: Optional[Dict[str, Any]] = None):
        """
        Finalize test and generate all reports.

        Args:
            test_result: "success", "failure", or "timeout"
            analysis: Optional analysis data
        """
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        self.metadata.update({
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "result": test_result,
            "total_messages": len(self.messages),
            "total_tool_calls": len(self.tool_calls),
            "total_api_calls": len(self.api_calls),
        })

        # Generate all report files
        self._generate_markdown_report(analysis)
        self._generate_dialog_txt()
        self._generate_api_calls_json()
        self._generate_analysis_json(analysis)

        # Create latest symlink
        latest_link = config.REPORTS_DIR / "latest"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(self.report_dir.name)

        # Print summary
        self._print_summary()

        logger.info(f"📊 Test completed: {test_result.upper()}")
        logger.info(f"📁 Reports saved to: {self.report_dir}")

    def _generate_markdown_report(self, analysis: Optional[Dict[str, Any]] = None):
        """Generate comprehensive markdown report."""
        report_path = self.report_dir / "full_report.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# Test Report: {self.test_name}\n\n")
            f.write(f"**Scenario**: `{self.scenario_name}`  \n")
            f.write(f"**Date**: {self.metadata['start_time']}  \n")
            f.write(f"**Duration**: {self.metadata['duration_seconds']:.1f} seconds  \n")
            f.write(f"**Result**: {self._result_emoji(self.metadata['result'])} **{self.metadata['result'].upper()}**\n\n")

            # Metrics
            f.write("## 📊 Metrics\n\n")
            f.write(f"- **Total Messages**: {len(self.messages)}\n")
            f.write(f"- **MCP Tool Calls**: {len(self.tool_calls)}\n")
            f.write(f"- **API Requests**: {len(self.api_calls)}\n")

            if self.tool_calls:
                avg_tool_latency = sum(tc.latency_ms for tc in self.tool_calls if tc.latency_ms) / len([tc for tc in self.tool_calls if tc.latency_ms])
                f.write(f"- **Avg Tool Latency**: {avg_tool_latency:.0f}ms\n")

            if self.api_calls:
                avg_api_latency = sum(ac.latency_ms for ac in self.api_calls if ac.latency_ms) / len([ac for ac in self.api_calls if ac.latency_ms])
                f.write(f"- **Avg API Latency**: {avg_api_latency:.0f}ms\n")

            f.write("\n---\n\n")

            # Dialog
            f.write("## 💬 Conversation Dialog\n\n")
            for msg in self.messages:
                timestamp = datetime.fromisoformat(msg.timestamp).strftime("%H:%M:%S.%f")[:-3]
                emoji = self._message_emoji(msg.sender, msg.message_type)
                sender_label = msg.sender.capitalize()

                f.write(f"### [{timestamp}] {emoji} {sender_label}\n")

                if msg.message_type == "thinking":
                    f.write("```\n")
                    f.write(msg.content + "\n")
                    f.write("```\n\n")
                elif msg.message_type == "tool_call":
                    f.write(f"**Tool**: `{msg.metadata.get('tool_name', 'unknown')}`  \n")
                    f.write("**Arguments**:\n```json\n")
                    f.write(json.dumps(msg.metadata.get('arguments', {}), indent=2, ensure_ascii=False) + "\n")
                    f.write("```\n\n")
                elif msg.message_type == "tool_result":
                    f.write("**Result**:\n```json\n")
                    result = msg.metadata.get('result', {})
                    # Truncate long results
                    result_str = json.dumps(result, indent=2, ensure_ascii=False)
                    if len(result_str) > 1000:
                        result_str = result_str[:1000] + "\n... (truncated)"
                    f.write(result_str + "\n")
                    f.write("```\n\n")
                else:
                    f.write(msg.content + "\n\n")

            # Tool Calls Summary
            if self.tool_calls:
                f.write("---\n\n")
                f.write("## 🔧 MCP Tool Calls Summary\n\n")
                f.write("| Tool | Calls | Avg Latency | Success Rate |\n")
                f.write("|------|-------|-------------|-------------|\n")

                tool_stats = {}
                for tc in self.tool_calls:
                    if tc.tool_name not in tool_stats:
                        tool_stats[tc.tool_name] = {
                            'count': 0,
                            'latencies': [],
                            'successes': 0
                        }
                    tool_stats[tc.tool_name]['count'] += 1
                    if tc.latency_ms:
                        tool_stats[tc.tool_name]['latencies'].append(tc.latency_ms)
                    if tc.success:
                        tool_stats[tc.tool_name]['successes'] += 1

                for tool, stats in tool_stats.items():
                    count = stats['count']
                    avg_latency = sum(stats['latencies']) / len(stats['latencies']) if stats['latencies'] else 0
                    success_rate = (stats['successes'] / count) * 100
                    f.write(f"| `{tool}` | {count} | {avg_latency:.0f}ms | {success_rate:.0f}% |\n")

            # Analysis
            if analysis:
                f.write("\n---\n\n")
                f.write("## 🎯 Analysis\n\n")

                if analysis.get("success_criteria"):
                    f.write("### ✅ Success Criteria\n\n")
                    for criterion, passed in analysis["success_criteria"].items():
                        icon = "✅" if passed else "❌"
                        f.write(f"- {icon} {criterion.replace('_', ' ').title()}\n")
                    f.write("\n")

                if analysis.get("recommendations"):
                    f.write("### 💡 Recommendations\n\n")
                    for i, rec in enumerate(analysis["recommendations"], 1):
                        f.write(f"{i}. {rec}\n")

    def _generate_dialog_txt(self):
        """Generate clean dialog text file."""
        dialog_path = self.report_dir / "dialog.txt"

        with open(dialog_path, 'w', encoding='utf-8') as f:
            f.write(f"Test: {self.test_name}\n")
            f.write(f"Scenario: {self.scenario_name}\n")
            f.write(f"{'=' * 60}\n\n")

            for msg in self.messages:
                if msg.message_type == "text":
                    timestamp = datetime.fromisoformat(msg.timestamp).strftime("%H:%M:%S")
                    sender = msg.sender.upper()
                    f.write(f"[{timestamp}] {sender}:\n")
                    f.write(f"{msg.content}\n\n")

    def _generate_api_calls_json(self):
        """Generate structured JSON of all API/tool calls."""
        api_calls_path = self.report_dir / "api_calls.json"

        data = {
            "metadata": self.metadata,
            "tool_calls": [asdict(tc) for tc in self.tool_calls],
            "api_calls": [asdict(ac) for ac in self.api_calls]
        }

        with open(api_calls_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _generate_analysis_json(self, analysis: Optional[Dict[str, Any]] = None):
        """Generate analysis JSON file."""
        analysis_path = self.report_dir / "analysis.json"

        data = {
            "metadata": self.metadata,
            "metrics": {
                "total_messages": len(self.messages),
                "total_tool_calls": len(self.tool_calls),
                "total_api_calls": len(self.api_calls),
                "duration_seconds": self.metadata["duration_seconds"],
            },
            "analysis": analysis or {}
        }

        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _print_summary(self):
        """Print summary table to console."""
        table = Table(title=f"Test Summary: {self.test_name}")

        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Result", self._result_emoji(self.metadata['result']) + " " + self.metadata['result'].upper())
        table.add_row("Duration", f"{self.metadata['duration_seconds']:.1f}s")
        table.add_row("Messages", str(len(self.messages)))
        table.add_row("Tool Calls", str(len(self.tool_calls)))
        table.add_row("API Calls", str(len(self.api_calls)))

        console.print(table)

    @staticmethod
    def _result_emoji(result: str) -> str:
        """Get emoji for test result."""
        return {
            "success": "✅",
            "failure": "❌",
            "timeout": "⏱️"
        }.get(result.lower(), "❓")

    @staticmethod
    def _message_emoji(sender: str, message_type: str) -> str:
        """Get emoji for message."""
        if message_type == "thinking":
            return "🤔"
        elif message_type == "tool_call":
            return "🔧"
        elif message_type == "tool_result":
            return "📤"
        else:
            return "👤" if sender == "client" else "🤖"
