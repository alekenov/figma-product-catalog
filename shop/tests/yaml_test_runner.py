#!/usr/bin/env python3
"""
YAML Test Runner for Order Lifecycle Tests

Executes test suites defined in YAML format with:
- Variable substitution
- Response assertions
- State management across tests
- Detailed reporting

Usage:
    python yaml_test_runner.py order_lifecycle.yaml
    python yaml_test_runner.py order_lifecycle.yaml --verbose
"""

import yaml
import requests
import sys
import re
from typing import Any, Dict, List, Optional
from pathlib import Path
import json


class TestContext:
    """Stores variables and state across test execution"""

    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.test_results: List[Dict] = []

    def set(self, key: str, value: Any):
        """Set a variable in context"""
        self.variables[key] = value

    def get(self, key: str) -> Any:
        """Get a variable from context"""
        return self.variables.get(key)

    def substitute(self, value: Any) -> Any:
        """Replace {{variable}} placeholders with actual values"""
        if isinstance(value, str):
            # Replace {{var}} with actual value
            for var_name, var_value in self.variables.items():
                pattern = f"{{{{{var_name}}}}}"
                if pattern in value:
                    value = value.replace(pattern, str(var_value))
            return value
        elif isinstance(value, dict):
            return {k: self.substitute(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.substitute(item) for item in value]
        else:
            return value


class YAMLTestRunner:
    """Runs tests from YAML test suite"""

    def __init__(self, yaml_file: str, verbose: bool = False):
        self.yaml_file = yaml_file
        self.verbose = verbose
        self.context = TestContext()
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def load_suite(self) -> Dict:
        """Load YAML test suite"""
        with open(self.yaml_file, 'r') as f:
            return yaml.safe_load(f)

    def log(self, message: str, level: str = "INFO"):
        """Print log message"""
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "SKIP": "⏭️",
            "DEBUG": "🔍"
        }
        icon = icons.get(level, "•")
        print(f"{icon}  {message}")

    def extract_json_path(self, data: Any, path: str) -> Any:
        """Extract value from JSON using simple path notation"""
        # Support $[0].field or $.field.nested
        if path.startswith("$"):
            path = path[1:]

        if not path or path == ".":
            return data

        # Remove leading dot
        if path.startswith("."):
            path = path[1:]

        parts = []
        current = ""
        in_bracket = False

        for char in path:
            if char == '[':
                if current:
                    parts.append(('key', current))
                    current = ""
                in_bracket = True
            elif char == ']':
                if current:
                    parts.append(('index', int(current)))
                    current = ""
                in_bracket = False
            elif char == '.' and not in_bracket:
                if current:
                    parts.append(('key', current))
                    current = ""
            else:
                current += char

        if current:
            parts.append(('key', current))

        # Traverse the data structure
        result = data
        for part_type, part_value in parts:
            if part_type == 'key':
                if isinstance(result, dict):
                    result = result.get(part_value)
                else:
                    return None
            elif part_type == 'index':
                if isinstance(result, list):
                    try:
                        result = result[part_value]
                    except IndexError:
                        return None
                else:
                    return None

        return result

    def save_response_values(self, response_data: Any, save_config: Dict):
        """Extract and save values from response"""
        for var_name, json_path in save_config.items():
            value = self.extract_json_path(response_data, json_path)
            if value is not None:
                self.context.set(var_name, value)
                if self.verbose:
                    self.log(f"Saved {var_name} = {value}", "DEBUG")

    def check_assertion(self, response: requests.Response, response_data: Any, assertion: Dict) -> bool:
        """Check a single assertion"""
        assertion_type = assertion.get('type')

        if assertion_type == 'status_code':
            expected = assertion.get('expected')
            actual = response.status_code
            if actual != expected:
                self.log(f"Status code mismatch: expected {expected}, got {actual}", "ERROR")
                return False
            return True

        elif assertion_type == 'json_path':
            path = assertion.get('path')
            expected = assertion.get('expected')
            operator = assertion.get('operator', '==')

            # Substitute variables in expected value
            expected = self.context.substitute(expected)

            actual = self.extract_json_path(response_data, path)

            if operator == 'exists':
                if actual is None:
                    self.log(f"Path {path} does not exist", "ERROR")
                    return False
                return True
            elif operator == '==':
                if actual != expected:
                    self.log(f"Value mismatch at {path}: expected {expected}, got {actual}", "ERROR")
                    return False
                return True
            elif operator == '!=':
                if actual == expected:
                    self.log(f"Value should not equal {expected} at {path}", "ERROR")
                    return False
                return True
            else:
                self.log(f"Unknown operator: {operator}", "ERROR")
                return False

        elif assertion_type == 'json_length':
            path = assertion.get('path', '$')
            operator = assertion.get('operator', '==')
            expected = assertion.get('expected')

            # Substitute variables in expected value
            expected = self.context.substitute(expected)

            # Convert to int if string
            if isinstance(expected, str):
                try:
                    expected = int(expected)
                except ValueError:
                    self.log(f"Expected length '{expected}' is not a valid integer", "ERROR")
                    return False

            actual_data = self.extract_json_path(response_data, path)
            if not isinstance(actual_data, (list, dict)):
                self.log(f"Path {path} is not a collection", "ERROR")
                return False

            actual_length = len(actual_data)

            if operator == '==':
                return actual_length == expected
            elif operator == '>=':
                return actual_length >= expected
            elif operator == '>':
                return actual_length > expected
            elif operator == '<=':
                return actual_length <= expected
            elif operator == '<':
                return actual_length < expected
            else:
                self.log(f"Unknown operator: {operator}", "ERROR")
                return False

        return True

    def run_test(self, test: Dict, base_url: str) -> bool:
        """Execute a single test"""
        test_name = test.get('name', 'Unnamed test')

        # Check if test should be skipped
        if test.get('skip', False):
            reason = test.get('reason', 'No reason provided')
            self.log(f"{test_name} - SKIPPED: {reason}", "SKIP")
            self.skipped += 1
            return True

        self.log(f"Running: {test_name}", "INFO")

        # Build request
        method = test.get('method', 'GET')
        endpoint = self.context.substitute(test.get('endpoint', ''))
        url = base_url + endpoint

        # Prepare parameters
        params = self.context.substitute(test.get('params', {}))
        headers = self.context.substitute(test.get('headers', {}))
        body = self.context.substitute(test.get('body', None))

        if self.verbose:
            self.log(f"  {method} {url}", "DEBUG")
            if params:
                self.log(f"  Params: {params}", "DEBUG")
            if body:
                self.log(f"  Body: {json.dumps(body, indent=2)}", "DEBUG")

        try:
            # Make request
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=body,
                headers=headers,
                timeout=10
            )

            # Try to parse response as JSON
            try:
                response_data = response.json()
            except:
                response_data = response.text

            if self.verbose:
                self.log(f"  Response: {response.status_code}", "DEBUG")

            # Save response values
            if 'save_response' in test:
                self.save_response_values(response_data, test['save_response'])

            # Check assertions
            assertions = test.get('assertions', [])
            all_passed = True

            for assertion in assertions:
                if not self.check_assertion(response, response_data, assertion):
                    all_passed = False

            if all_passed:
                self.log(f"{test_name} - PASSED", "SUCCESS")
                self.passed += 1
                return True
            else:
                self.log(f"{test_name} - FAILED", "ERROR")
                self.failed += 1
                return False

        except Exception as e:
            self.log(f"{test_name} - ERROR: {str(e)}", "ERROR")
            self.failed += 1
            return False

    def run_suite(self):
        """Execute entire test suite"""
        suite = self.load_suite()

        # Extract suite config
        suite_config = suite.get('test_suite', {})
        suite_name = suite_config.get('name', 'Test Suite')
        base_url = suite_config.get('base_url', 'http://localhost:8014/api/v1')
        shop_id = suite_config.get('shop_id', 8)

        # Set initial variables
        self.context.set('shop_id', shop_id)

        print("\n" + "=" * 60)
        self.log(f"Starting: {suite_name}", "INFO")
        print("=" * 60 + "\n")

        # Run setup
        if 'setup' in suite:
            self.log("Running setup...", "INFO")
            for test in suite['setup']:
                if not self.run_test(test, base_url):
                    self.log("Setup failed, aborting", "ERROR")
                    return
            print()

        # Run tests
        if 'tests' in suite:
            for test in suite['tests']:
                self.run_test(test, base_url)
            print()

        # Run cleanup
        if 'cleanup' in suite:
            self.log("Running cleanup...", "INFO")
            for test in suite['cleanup']:
                self.run_test(test, base_url)
            print()

        # Print summary
        if 'summary' in suite:
            summary = suite['summary']

            # Print variables
            if 'print_variables' in summary:
                print("\n📊 Test Variables:")
                for var in summary['print_variables']:
                    value = self.context.get(var)
                    print(f"   {var}: {value}")

            # Print message
            if 'print_message' in summary:
                message = self.context.substitute(summary['print_message'])
                print(f"\n{message}")

        # Print final results
        print("\n" + "=" * 60)
        total = self.passed + self.failed + self.skipped
        print(f"Test Results: {self.passed}/{total} passed")
        if self.failed > 0:
            print(f"  ❌ Failed: {self.failed}")
        if self.skipped > 0:
            print(f"  ⏭️  Skipped: {self.skipped}")
        print("=" * 60 + "\n")

        return self.failed == 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python yaml_test_runner.py <test_suite.yaml> [--verbose]")
        sys.exit(1)

    yaml_file = sys.argv[1]
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    if not Path(yaml_file).exists():
        print(f"Error: Test file '{yaml_file}' not found")
        sys.exit(1)

    runner = YAMLTestRunner(yaml_file, verbose=verbose)
    success = runner.run_suite()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
