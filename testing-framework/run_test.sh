#!/bin/bash
#
# Wrapper script for running AI tests with proper environment setup
#

set -e

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Run test
if [ -z "$1" ]; then
    echo "Usage: ./run_test.sh <scenario.yaml>"
    echo ""
    echo "Available scenarios:"
    ls -1 scenarios/*.yaml | xargs -n1 basename
    exit 1
fi

python3 test_orchestrator.py "$@"
