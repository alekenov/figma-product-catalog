"""
Environment Variables Validator

Validates required environment variables at service startup.
Provides clear error messages and prevents runtime crashes due to missing config.
"""
import os
import sys
from typing import Dict, List, Any, Optional


class ConfigValidator:
    """
    Validates environment variables at service startup.

    Features:
    - Required variables validation
    - Type validation (URL, integer, boolean)
    - Default values
    - Clear error messages with actionable advice
    """

    @staticmethod
    def require_env(var_name: str, service_name: str) -> str:
        """
        Require a mandatory environment variable.

        Args:
            var_name: Name of the environment variable
            service_name: Service name for error messages

        Returns:
            Value of the environment variable

        Raises:
            SystemExit: If variable is not set
        """
        value = os.getenv(var_name)
        if not value:
            print(f"❌ ERROR [{service_name}]: Missing required environment variable: {var_name}")
            print(f"\nℹ️  Set it in your .env file or export it:")
            print(f"   export {var_name}=<value>")
            sys.exit(1)
        return value

    @staticmethod
    def validate_url(url: str, var_name: str) -> bool:
        """
        Validate that a string is a valid URL.

        Args:
            url: URL string to validate
            var_name: Variable name for error messages

        Returns:
            True if valid, False otherwise
        """
        if not url:
            return False

        if not url.startswith(("http://", "https://")):
            print(f"❌ ERROR: {var_name} must start with http:// or https://")
            print(f"   Got: {url}")
            return False
        return True

    @staticmethod
    def validate_integer(value: str, var_name: str) -> tuple[bool, Optional[int]]:
        """
        Validate that a string can be converted to integer.

        Args:
            value: String value to validate
            var_name: Variable name for error messages

        Returns:
            Tuple of (is_valid, converted_value or None)
        """
        try:
            return True, int(value)
        except (ValueError, TypeError):
            print(f"❌ ERROR: {var_name} must be a valid integer")
            print(f"   Got: {value}")
            return False, None

    @staticmethod
    def validate_boolean(value: str, var_name: str) -> tuple[bool, Optional[bool]]:
        """
        Validate that a string can be converted to boolean.

        Args:
            value: String value to validate ("true", "false", "1", "0")
            var_name: Variable name for error messages

        Returns:
            Tuple of (is_valid, converted_value or None)
        """
        if not value:
            return False, None

        value_lower = value.lower()
        if value_lower in ("true", "1", "yes"):
            return True, True
        elif value_lower in ("false", "0", "no"):
            return True, False
        else:
            print(f"❌ ERROR: {var_name} must be true/false or 1/0")
            print(f"   Got: {value}")
            return False, None

    @staticmethod
    def validate_all(config: Dict[str, Dict[str, Any]], service_name: str) -> bool:
        """
        Validate all environment variables according to configuration.

        Args:
            config: Configuration dictionary with format:
                {
                    "VAR_NAME": {
                        "required": bool,
                        "type": "url" | "integer" | "boolean" | None,
                        "default": Any (optional)
                    }
                }
            service_name: Service name for logging

        Returns:
            True if all validations passed, exits with code 1 otherwise

        Example:
            config = {
                "CLAUDE_API_KEY": {"required": True},
                "MCP_URL": {"required": True, "type": "url"},
                "DEBUG": {"required": False, "default": "false", "type": "boolean"},
                "PORT": {"required": False, "default": "8000", "type": "integer"}
            }

            ConfigValidator.validate_all(config, "AI Agent Service")
        """
        print(f"🔍 Validating configuration for {service_name}...")

        errors: List[str] = []
        warnings: List[str] = []

        for var_name, rules in config.items():
            value = os.getenv(var_name)

            # Check required
            if rules.get("required") and not value:
                errors.append(f"Missing required variable: {var_name}")
                continue

            # Set default if value not provided
            if not value and "default" in rules:
                default_value = rules["default"]
                os.environ[var_name] = str(default_value)
                print(f"  ℹ️  {var_name}: using default '{default_value}'")
                value = default_value

            # Skip validation if no value and not required
            if not value:
                continue

            # Type validation
            var_type = rules.get("type")

            if var_type == "url":
                if not ConfigValidator.validate_url(value, var_name):
                    errors.append(f"Invalid URL format: {var_name}")

            elif var_type == "integer":
                is_valid, converted = ConfigValidator.validate_integer(value, var_name)
                if not is_valid:
                    errors.append(f"Invalid integer: {var_name}")
                elif converted is not None and converted < 0:
                    warnings.append(f"{var_name} is negative: {converted}")

            elif var_type == "boolean":
                is_valid, converted = ConfigValidator.validate_boolean(value, var_name)
                if not is_valid:
                    errors.append(f"Invalid boolean: {var_name}")

            if not errors:  # Only print success if no errors for this var
                print(f"  ✅ {var_name}: configured")

        # Print warnings
        if warnings:
            print(f"\n⚠️  Warnings:")
            for warning in warnings:
                print(f"   - {warning}")

        # Handle errors
        if errors:
            print(f"\n❌ Configuration errors for {service_name}:")
            for error in errors:
                print(f"   - {error}")
            print(f"\nℹ️  Please check your .env file or environment variables")
            sys.exit(1)

        print(f"✅ Configuration valid for {service_name}\n")
        return True


# Convenience function for quick validation
def validate_config(config: Dict[str, Dict[str, Any]], service_name: str) -> bool:
    """
    Convenience function to validate configuration.
    Alias for ConfigValidator.validate_all()
    """
    return ConfigValidator.validate_all(config, service_name)


# Export for easy import
__all__ = ["ConfigValidator", "validate_config"]
