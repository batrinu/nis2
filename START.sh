#!/bin/bash
#
# ==============================================================================
# NIS2 Field Audit Tool - Uncle-Friendly Launcher (Mac/Linux)
# ==============================================================================
# This script automatically:
#   1. Finds Python on your system
#   2. Creates a virtual environment on first run
#   3. Installs required packages
#   4. Launches the application
# ==============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$SCRIPT_DIR/nis2-audit-app"

# Print banner
echo "========================================"
echo "  NIS2 Field Audit Tool"
echo "========================================"
echo ""

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}[ERROR] Application directory not found!${NC}"
    echo "Expected: $APP_DIR"
    echo ""
    echo "Make sure you extracted the entire archive."
    exit 1
fi

# ==============================================================================
# Step 1: Find Python
# ==============================================================================
echo -e "${BLUE}[INFO]${NC} Looking for Python..."

PYTHON_CMD=""

# Try different Python commands (in order of preference)
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

# Check if we found Python
if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo -e "${RED}[ERROR] Python not found!${NC}"
    echo ""
    echo "========================================"
    echo "  Python is Required"
    echo "========================================"
    echo ""
    echo "The NIS2 Audit Tool needs Python 3.10 or newer."
    echo ""
    echo "Please install Python:"
    echo ""
    echo "  macOS:"
    echo "    brew install python3"
    echo "    OR download from https://python.org/downloads"
    echo ""
    echo "  Ubuntu/Debian:"
    echo "    sudo apt update"
    echo "    sudo apt install python3 python3-venv python3-pip"
    echo ""
    echo "  RHEL/CentOS/Fedora:"
    echo "    sudo dnf install python3 python3-venv python3-pip"
    echo ""
    echo "  Other Linux:"
    echo "    https://python.org/downloads"
    echo ""
    echo "========================================"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo -e "${GREEN}[OK]${NC} Found $PYTHON_VERSION"
echo ""

# ==============================================================================
# Step 2: Check/Create Virtual Environment
# ==============================================================================

if [ ! -d "$APP_DIR/.venv" ]; then
    echo "========================================"
    echo "  First Run Setup"
    echo "========================================"
    echo ""
    echo -e "${BLUE}[INFO]${NC} Setting up the application..."
    echo -e "${BLUE}[INFO]${NC} This will take 1-2 minutes (one-time only)"
    echo ""
    
    cd "$APP_DIR"
    
    # Create virtual environment
    echo "[1/3] Creating virtual environment..."
    if ! $PYTHON_CMD -m venv .venv; then
        echo ""
        echo -e "${RED}[ERROR] Failed to create virtual environment${NC}"
        echo ""
        echo "Possible solutions:"
        echo "  - Install python3-venv: sudo apt install python3-venv"
        echo "  - Check disk space"
        echo "  - Run with sudo (not recommended)"
        exit 1
    fi
    
    # Activate and install
    echo "[2/3] Activating environment..."
    source .venv/bin/activate
    
    echo "[3/3] Installing packages..."
    if ! pip install -q --upgrade pip; then
        echo -e "${YELLOW}[WARNING]${NC} Could not upgrade pip, continuing..."
    fi
    
    if ! pip install -q -e .; then
        echo ""
        echo -e "${RED}[ERROR] Package installation failed${NC}"
        echo ""
        echo "Possible solutions:"
        echo "  1. Check your internet connection"
        echo "  2. Update pip: python -m pip install --upgrade pip"
        echo "  3. Try with sudo (not recommended): sudo ./START.sh"
        echo ""
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}[OK]${NC} Setup complete!"
    echo ""
    sleep 2
fi

# ==============================================================================
# Step 3: Check Terminal Size
# ==============================================================================

# Get terminal size
if command -v stty &> /dev/null; then
    TERM_SIZE=$(stty size 2>/dev/null || echo "24 80")
    TERM_HEIGHT=$(echo $TERM_SIZE | cut -d' ' -f1)
    TERM_WIDTH=$(echo $TERM_SIZE | cut -d' ' -f2)
    
    # Check minimum size (80x24)
    if [ "$TERM_WIDTH" -lt 80 ]; then
        echo -e "${YELLOW}[WARNING]${NC} Terminal window is too narrow"
        echo "Current: $TERM_WIDTH columns"
        echo "Required: at least 80 columns"
        echo ""
        echo "Please resize your terminal window wider and run again."
        exit 1
    fi
    
    if [ "$TERM_HEIGHT" -lt 24 ]; then
        echo -e "${YELLOW}[WARNING]${NC} Terminal window is too short"
        echo "Current: $TERM_HEIGHT rows"
        echo "Required: at least 24 rows"
        echo ""
        echo "Please resize your terminal window taller and run again."
        exit 1
    fi
fi

# ==============================================================================
# Step 4: Launch Application
# ==============================================================================

echo -e "${BLUE}[INFO]${NC} Starting NIS2 Field Audit Tool..."
echo ""

cd "$APP_DIR"
source .venv/bin/activate

# Run the app
if ! python -m app.textual_app; then
    EXIT_CODE=$?
    echo ""
    echo "========================================"
    echo "  Application Exited with Error"
    echo "========================================"
    echo ""
    echo "Exit code: $EXIT_CODE"
    echo ""
    echo "Check the log file for details:"
    echo "  ~/.nis2-audit/logs/nis2-audit.log"
    echo ""
    echo "Try these solutions:"
    echo "  1. Delete the .venv folder and run START.sh again"
    echo "  2. Check that your antivirus isn't blocking the app"
    echo "  3. Run with sudo (not recommended)"
    echo ""
    exit $EXIT_CODE
fi
