#!/bin/bash
#
# NIS2 Field Audit Tool - Installation Script
#

set -e

echo "🔧 NIS2 Field Audit Tool Installer"
echo "==================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    echo "Please install Python 3.10 or higher: https://python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  ✓ Python $PYTHON_VERSION"

# Check nmap (optional but recommended)
if command -v nmap &> /dev/null; then
    echo "  ✓ nmap $(nmap --version | head -1 | awk '{print $3}')"
else
    echo -e "${YELLOW}⚠ nmap not found. Network scanning will not work.${NC}"
    echo "  Install with: sudo apt install nmap  (Debian/Ubuntu)"
    echo "            or: sudo yum install nmap  (RHEL/CentOS)"
    echo "            or: brew install nmap      (macOS)"
fi

echo ""

# Setup virtual environment if needed
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "📦 Installing Python dependencies..."
source "$VENV_DIR/bin/activate"
pip install -e "$SCRIPT_DIR" -q

cd "$SCRIPT_DIR"

echo "📝 Setting up CLI..."
chmod +x bin/nis2-audit

# Update wrapper script to use venv
sed -i "1a\\
# Use virtual environment if available\nif [ -d \"\\$SCRIPT_DIR/.venv\" ]; then\n    export PATH=\"\\$SCRIPT_DIR/.venv/bin:\$PATH\"\nfi\n" bin/nis2-audit 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "To start the audit tool, run:"
echo "  $SCRIPT_DIR/bin/nis2-audit"
echo ""
