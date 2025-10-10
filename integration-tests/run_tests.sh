#!/bin/bash
# Integration Test Runner
# Checks service health and runs appropriate test suites

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service URLs (support both standalone and Docker ports)
export BACKEND_URL=${BACKEND_URL:-http://localhost:8014}
export MCP_SERVER_URL=${MCP_SERVER_URL:-http://localhost:8001}
# Docker Compose default: port 8000, Standalone: port 8015
export AI_AGENT_URL=${AI_AGENT_URL:-http://localhost:8000}

echo -e "${BLUE}🔬 Integration Test Runner${NC}"
echo -e "${BLUE}======================================${NC}\n"

# Function to check service health
check_service() {
    local url=$1
    local name=$2

    if curl -s -f "${url}/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ ${name} is running${NC}"
        return 0
    else
        echo -e "${RED}❌ ${name} is not running${NC}"
        return 1
    fi
}

# Check which services are available
echo -e "${YELLOW}📡 Checking service health...${NC}\n"

BACKEND_OK=0
MCP_OK=0
AI_AGENT_OK=0

check_service "$BACKEND_URL" "Backend API (port 8014)" && BACKEND_OK=1 || true
check_service "$MCP_SERVER_URL" "MCP Server (port 8001)" && MCP_OK=1 || true
check_service "$AI_AGENT_URL" "AI Agent (port 8000)" && AI_AGENT_OK=1 || true

echo ""

# Determine which tests to run
if [ $BACKEND_OK -eq 0 ]; then
    echo -e "${RED}❌ Backend API is not running. Cannot run tests.${NC}"
    echo -e "${YELLOW}💡 Start backend with: cd backend && python3 main.py${NC}"
    exit 1
fi

if [ $MCP_OK -eq 0 ]; then
    echo -e "${RED}❌ MCP Server is not running. Cannot run tests.${NC}"
    echo -e "${YELLOW}💡 Start MCP server with: cd mcp-server && ./start.sh${NC}"
    exit 1
fi

# Build test command
TEST_CMD="python3 -m pytest"
TEST_ARGS="-v --tb=short"
TEST_SCOPE=""

if [ $AI_AGENT_OK -eq 1 ]; then
    echo -e "${GREEN}🚀 All services running. Running FULL test suite (including AI conversation tests)${NC}\n"
    TEST_SCOPE="test_conversation_flows.py"
else
    echo -e "${YELLOW}⚠️  AI Agent not running. Running DIRECT MCP tests only${NC}"
    echo -e "${YELLOW}💡 For full tests, start AI agent with: cd ai-agent-service && python3 main.py${NC}\n"
    TEST_SCOPE="test_conversation_flows.py::TestDirectMCPCalls"
fi

# Run tests
echo -e "${BLUE}🧪 Running tests...${NC}\n"
$TEST_CMD $TEST_ARGS $TEST_SCOPE

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed${NC}"
    exit 1
fi
