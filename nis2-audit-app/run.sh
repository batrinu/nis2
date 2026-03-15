#!/bin/bash
# NIS2 Field Audit Tool Launcher

cd "$(dirname "$0")"

echo "🛡️  Starting NIS2 Field Audit Tool..."
echo ""

# Check if we're in a virtual environment
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "⚠️  No virtual environment detected."
    echo "   If you have dependency issues, try:"
    echo "   python3 -m venv .venv && source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    echo ""
fi

# Run the app
python3 -m app.textual_app "$@"
