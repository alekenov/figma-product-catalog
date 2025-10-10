"""
Configuration for AI Testing Framework.
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
SCENARIOS_DIR = BASE_DIR / "scenarios"
PERSONAS_DIR = BASE_DIR / "personas"
MEMORIES_DIR = BASE_DIR / "memories"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
SCENARIOS_DIR.mkdir(exist_ok=True)
PERSONAS_DIR.mkdir(exist_ok=True)
MEMORIES_DIR.mkdir(exist_ok=True)
(MEMORIES_DIR / "manager").mkdir(exist_ok=True)
(MEMORIES_DIR / "clients").mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# API Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8014/api/v1")
SHOP_ID = int(os.getenv("SHOP_ID", "8"))

# Claude API Configuration
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY environment variable is required")

# Model configuration with Claude 4.5
CLAUDE_MODEL_MANAGER = os.getenv("CLAUDE_MODEL_MANAGER", "claude-sonnet-4-5-20250929")
CLAUDE_MODEL_CLIENT = os.getenv("CLAUDE_MODEL_CLIENT", "claude-sonnet-4-5-20250929")

# Beta features for new Claude 4.5 features
# Pass as extra_headers parameter
CLAUDE_EXTRA_HEADERS = {
    "anthropic-beta": "context-management-2025-06-27,interleaved-thinking-2025-05-14"
}

# Test configuration
DEFAULT_MAX_TURNS = 20
DEFAULT_TIMEOUT_SECONDS = 180
MAX_TOKENS = 4096

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Report configuration
REPORT_TEMPLATE_DIR = BASE_DIR / "templates"
REPORT_TEMPLATE_DIR.mkdir(exist_ok=True)
