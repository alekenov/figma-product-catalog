#!/usr/bin/env python3
"""
Production Test Runner
Запускает YAML-сценарии для тестирования CRM на продакшене
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
import yaml
from config_production import *


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color
    BOLD = '\033[1m'


class ProductionTestRunner:
    """Executes YAML test scenarios against production API"""

    def __init__(self, base_url: str = BASE_URL, verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.results = []
        self.context = {}  # Shared context for variables between steps

    def log(self, message: str, color: str = Colors.NC):
        """Print colored log message"""
        print(f"{color}{message}{Colors.NC}")

    def load_scenario(self, yaml_path: Path) -> Dict[str, Any]:
        """Load YAML test scenario"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def interpolate_variables(self, value: Any, context: Dict[str, Any]) -> Any:
        """Replace {{variable}} placeholders with context values"""
        if isinstance(value, str):
            # Handle simple variable replacement
            for key, val in context.items():
                placeholder = f"{{{{{key}}}}}"
                if placeholder in value:
                    value = value.replace(placeholder, str(val))

            # Handle timestamp
            if "{{timestamp}}" in value:
                value = value.replace("{{timestamp}}", datetime.now().isoformat())

            return value

        elif isinstance(value, dict):
            return {k: self.interpolate_variables(v, context) for k, v in value.items()}

        elif isinstance(value, list):
            return [self.interpolate_variables(item, context) for item in value]

        return value

    def execute_request(self, step: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a single HTTP request step"""
        endpoint = self.interpolate_variables(step['endpoint'], context)
        method = step.get('method', 'GET').upper()

        # Build full URL
        url = f"{self.base_url}{endpoint}"

        # Prepare headers
        headers = self.interpolate_variables(step.get('headers', {}), context)

        # Prepare query params
        params = self.interpolate_variables(step.get('query_params', {}), context)

        # Prepare body
        body = self.interpolate_variables(step.get('body', {}), context)

        if self.verbose:
            self.log(f"  → {method} {url}", Colors.BLUE)
            if params:
                self.log(f"    Params: {json.dumps(params, indent=2)}", Colors.BLUE)
            if body:
                self.log(f"    Body: {json.dumps(body, indent=2)}", Colors.BLUE)

        try:
            # Execute request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=body if body else None,
                timeout=REQUEST_TIMEOUT
            )

            if self.verbose:
                self.log(f"  ← Status: {response.status_code}", Colors.BLUE)
                try:
                    self.log(f"    Response: {json.dumps(response.json(), indent=2)}", Colors.BLUE)
                except:
                    pass

            return {
                'status_code': response.status_code,
                'response': response.json() if response.text else {},
                'headers': dict(response.headers)
            }

        except requests.exceptions.Timeout:
            self.log(f"  ✗ Timeout after {REQUEST_TIMEOUT}s", Colors.RED)
            return None

        except Exception as e:
            self.log(f"  ✗ Error: {str(e)}", Colors.RED)
            return None

    def check_assertions(self, result: Dict[str, Any], assertions: List[Dict[str, Any]]) -> bool:
        """Verify response matches assertions"""
        if not assertions:
            return True

        for assertion in assertions:
            # Status code assertion
            if 'status_code' in assertion:
                expected = assertion['status_code']
                actual = result.get('status_code')

                # Support list of acceptable status codes
                if isinstance(expected, list):
                    if actual not in expected:
                        self.log(f"    ✗ Expected status {expected}, got {actual}", Colors.RED)
                        return False
                else:
                    if actual != expected:
                        self.log(f"    ✗ Expected status {expected}, got {actual}", Colors.RED)
                        return False

            # Response field existence
            for key, value in assertion.items():
                if key == 'status_code':
                    continue

                if value == 'exists':
                    # Check if field exists in response
                    # Try both with and without "response." prefix
                    parts = key.split('.')

                    # First try: look for the field in result['response']
                    found = False
                    response_data = result.get('response', {})

                    if parts[0] == 'response' and len(parts) > 1:
                        # Path like "response.access_token" - check if "access_token" exists
                        field_path = parts[1:]
                        current = response_data
                        for part in field_path:
                            if isinstance(current, dict) and part in current:
                                current = current[part]
                                found = True
                            else:
                                found = False
                                break
                    else:
                        # Path without "response." prefix - check directly
                        if key in response_data:
                            found = True

                    if not found:
                        self.log(f"    ✗ Field '{key}' not found in response", Colors.RED)
                        return False

                elif value == 'is_array':
                    # Check if response is array
                    if not isinstance(result.get('response'), list):
                        self.log(f"    ✗ Response is not an array", Colors.RED)
                        return False

        return True

    def save_variables(self, result: Dict[str, Any], save_config: Dict[str, str], context: Dict[str, Any]):
        """Extract values from response and save to context"""
        if not save_config:
            return

        for var_name, path in save_config.items():
            # Handle paths like "response[0].id" or "response.user.id"
            import re

            # Start with result dict
            value = result

            # Split path by dots but keep array indices together
            # Example: "response[0].id" -> ["response[0]", "id"]
            parts = re.split(r'\.(?![^\[]*\])', path)

            for part in parts:
                if value is None:
                    break

                # Handle array access like "response[0]"
                if '[' in part:
                    match = re.match(r'([^\[]+)\[(\d+)\]', part)
                    if match:
                        key = match.group(1)
                        index = int(match.group(2))

                        # Get the key first (e.g., "response")
                        if isinstance(value, dict):
                            value = value.get(key)

                        # Then access array element
                        if isinstance(value, list) and len(value) > index:
                            value = value[index]
                        else:
                            value = None
                    else:
                        value = None
                elif isinstance(value, dict):
                    value = value.get(part)
                else:
                    value = None

            if value is not None:
                context[var_name] = value
                if self.verbose:
                    self.log(f"    💾 Saved {var_name} = {value}", Colors.BLUE)

    def run_scenario(self, scenario_path: Path) -> Dict[str, Any]:
        """Run a single test scenario"""
        scenario = self.load_scenario(scenario_path)

        self.log(f"\n{Colors.BOLD}{'='*70}{Colors.NC}")
        self.log(f"{Colors.BOLD}Scenario: {scenario['name']}{Colors.NC}")
        self.log(f"{scenario.get('description', '')}")
        self.log(f"{Colors.BOLD}{'='*70}{Colors.NC}\n")

        # Initialize context with environment variables
        context = {**scenario.get('environment', {})}

        passed_steps = 0
        failed_steps = 0
        skipped_steps = 0

        start_time = time.time()

        for idx, step in enumerate(scenario.get('test_steps', []), 1):
            step_name = step.get('name', f'Step {idx}')
            is_optional = step.get('optional', False)

            self.log(f"{idx}. {step_name}...", Colors.YELLOW)

            # Execute request
            result = self.execute_request(step, context)

            if result is None:
                if is_optional:
                    self.log(f"  ⊘ Skipped (optional)", Colors.YELLOW)
                    skipped_steps += 1
                else:
                    self.log(f"  ✗ Failed", Colors.RED)
                    failed_steps += 1
                continue

            # Check assertions
            assertions = step.get('assertions', [])
            if self.check_assertions(result, assertions):
                self.log(f"  ✓ Passed", Colors.GREEN)
                passed_steps += 1

                # Save variables for next steps
                self.save_variables(result, step.get('save', {}), context)
            else:
                if is_optional:
                    self.log(f"  ⊘ Skipped (optional, failed assertion)", Colors.YELLOW)
                    skipped_steps += 1
                else:
                    self.log(f"  ✗ Failed", Colors.RED)
                    failed_steps += 1

        duration = time.time() - start_time

        # Summary
        total_steps = passed_steps + failed_steps + skipped_steps
        self.log(f"\n{Colors.BOLD}Summary:{Colors.NC}")
        self.log(f"  ✓ Passed: {passed_steps}/{total_steps}", Colors.GREEN)
        if failed_steps > 0:
            self.log(f"  ✗ Failed: {failed_steps}/{total_steps}", Colors.RED)
        if skipped_steps > 0:
            self.log(f"  ⊘ Skipped: {skipped_steps}/{total_steps}", Colors.YELLOW)
        self.log(f"  Duration: {duration:.2f}s")

        return {
            'scenario': scenario['name'],
            'file': str(scenario_path),
            'passed': passed_steps,
            'failed': failed_steps,
            'skipped': skipped_steps,
            'total': total_steps,
            'duration': duration,
            'success': failed_steps == 0
        }

    def run_all_scenarios(self, scenarios_dir: Path) -> List[Dict[str, Any]]:
        """Run all YAML scenarios in directory"""
        yaml_files = sorted(scenarios_dir.glob('*.yaml'))

        if not yaml_files:
            self.log(f"No YAML files found in {scenarios_dir}", Colors.RED)
            return []

        self.log(f"{Colors.BOLD}Running {len(yaml_files)} test scenarios...{Colors.NC}\n")

        results = []
        for yaml_file in yaml_files:
            if yaml_file.name in SKIP_TESTS:
                self.log(f"Skipping {yaml_file.name} (configured to skip)", Colors.YELLOW)
                continue

            result = self.run_scenario(yaml_file)
            results.append(result)

        return results

    def print_final_report(self, results: List[Dict[str, Any]]):
        """Print final test report"""
        self.log(f"\n{Colors.BOLD}{'='*70}{Colors.NC}")
        self.log(f"{Colors.BOLD}FINAL REPORT{Colors.NC}")
        self.log(f"{Colors.BOLD}{'='*70}{Colors.NC}\n")

        total_scenarios = len(results)
        passed_scenarios = sum(1 for r in results if r['success'])
        failed_scenarios = total_scenarios - passed_scenarios

        total_steps = sum(r['total'] for r in results)
        passed_steps = sum(r['passed'] for r in results)
        failed_steps = sum(r['failed'] for r in results)
        skipped_steps = sum(r['skipped'] for r in results)

        total_duration = sum(r['duration'] for r in results)

        self.log(f"Scenarios: {passed_scenarios}/{total_scenarios} passed",
                 Colors.GREEN if failed_scenarios == 0 else Colors.RED)
        self.log(f"Steps: {passed_steps}/{total_steps} passed",
                 Colors.GREEN if failed_steps == 0 else Colors.RED)
        if skipped_steps > 0:
            self.log(f"Skipped: {skipped_steps} steps", Colors.YELLOW)
        self.log(f"Total duration: {total_duration:.2f}s")

        if failed_scenarios > 0:
            self.log(f"\n{Colors.BOLD}Failed scenarios:{Colors.NC}", Colors.RED)
            for result in results:
                if not result['success']:
                    self.log(f"  ✗ {result['scenario']} ({result['failed']} failed steps)", Colors.RED)

        # Save JSON report
        report_path = Path(REPORT_DIR) / f"production_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_scenarios': total_scenarios,
                    'passed_scenarios': passed_scenarios,
                    'failed_scenarios': failed_scenarios,
                    'total_steps': total_steps,
                    'passed_steps': passed_steps,
                    'failed_steps': failed_steps,
                    'skipped_steps': skipped_steps,
                    'duration': total_duration
                },
                'results': results
            }, f, indent=2)

        self.log(f"\nReport saved: {report_path}", Colors.BLUE)


def main():
    parser = argparse.ArgumentParser(description='Run production CRM tests')
    parser.add_argument('--scenario', '-s', help='Run specific scenario file')
    parser.add_argument('--all', '-a', action='store_true', help='Run all scenarios')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--url', default=BASE_URL, help='Override base URL')

    args = parser.parse_args()

    runner = ProductionTestRunner(base_url=args.url, verbose=args.verbose)

    scenarios_dir = Path(__file__).parent / SCENARIOS_DIR

    if args.scenario:
        # Run single scenario
        scenario_path = scenarios_dir / args.scenario
        if not scenario_path.exists():
            print(f"Scenario not found: {scenario_path}")
            sys.exit(1)

        result = runner.run_scenario(scenario_path)
        runner.print_final_report([result])

        sys.exit(0 if result['success'] else 1)

    elif args.all:
        # Run all scenarios
        results = runner.run_all_scenarios(scenarios_dir)
        runner.print_final_report(results)

        sys.exit(0 if all(r['success'] for r in results) else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
