"""
Production Testing Configuration
Настройки для тестирования на продакшене
"""

# Production API URL
BASE_URL = "https://figma-product-catalog-production.up.railway.app/api/v1"

# Test credentials (working production user)
TEST_USER_PHONE = "+77777777777"  # Must include + prefix
TEST_USER_PASSWORD = "test123"
TEST_USER_NAME = "API Test User"

# Default shop ID for testing (user's actual shop)
SHOP_ID = 2

# Timeout settings (seconds)
REQUEST_TIMEOUT = 30
TEST_TIMEOUT = 180

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "production_test_results.log"

# Report settings
REPORT_DIR = "reports"
REPORT_FORMAT = "json"  # json, html, markdown

# Test scenarios directory
SCENARIOS_DIR = "scenarios"

# Optional: Skip certain tests
SKIP_TESTS = []  # e.g., ["06_profile_updates.yaml"] if profile API not ready

# Cleanup after tests
CLEANUP_TEST_DATA = True  # Delete created test products/orders after tests

# Alert settings
ALERT_ON_FAILURE = False  # Send alert if tests fail (future feature)
SLACK_WEBHOOK = None  # For notifications
