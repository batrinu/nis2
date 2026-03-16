#!/bin/bash
#
# =============================================================================
# NIS2 Field Audit Tool - Simple Launcher (Mac/Linux)
# =============================================================================
# This script:
#   1. Checks for Python
#   2. Creates virtual environment on first run
#   3. Installs dependencies
#   4. Launches the application
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  NIS2 Field Audit Tool"
echo "========================================"
echo ""

# Check for Python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}[ERROR] Python not found!${NC}"
    echo ""
    echo "Please install Python 3.10 or newer:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  Other: https://python.org/downloads"
    echo ""
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo -e "${GREEN}[OK]${NC} Found $PYTHON_VERSION"

# Create virtual environment if needed
if [ ! -f ".venv/bin/python" ]; then
    echo ""
    echo "========================================"
    echo "  First Run Setup"
    echo "========================================"
    echo ""
    echo -e "${BLUE}Setting up virtual environment...${NC}"
    echo "This will take 1-2 minutes (one-time only)"
    echo ""
    
    if ! $PYTHON_CMD -m venv .venv; then
        echo -e "${RED}[ERROR] Failed to create virtual environment${NC}"
        echo "You may need to install python3-venv"
        exit 1
    fi
    
    echo "Installing dependencies..."
    source .venv/bin/activate
    pip install -q --upgrade pip
    if ! pip install -q -r requirements.txt; then
        echo -e "${RED}[ERROR] Failed to install dependencies${NC}"
        echo "Check your internet connection"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}[OK] Setup complete!${NC}"
    echo ""
    sleep 2
fi

# Activate and run
source .venv/bin/activate

echo ""
echo -e "${BLUE}Starting NIS2 Field Audit Tool...${NC}"
echo ""

if ! python -m app.main; then
    EXIT_CODE=$?
    echo ""
    echo "========================================"
    echo "  Application exited with error $EXIT_CODE"
    echo "========================================"
    echo ""
    echo "Try deleting the .venv folder and running again."
    exit $EXIT_CODE
fi
