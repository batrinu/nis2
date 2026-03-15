#!/bin/bash
# Run tests for NIS2 Field Audit Tool

cd "$(dirname "$0")"

echo "🧪 NIS2 Field Audit Tool - Test Runner"
echo "======================================"
echo ""

# Check if pytest is installed
if ! python3 -c "import pytest" 2>/dev/null; then
    echo "⚠️  pytest not found. Installing test dependencies..."
    pip install pytest pytest-asyncio
    echo ""
fi

# Parse arguments
MODE=${1:-"all"}

run_tests() {
    case "$MODE" in
        all)
            echo "📋 Running all tests..."
            python3 -m pytest tests/ -v --tb=short
            ;;
        launch)
            echo "🚀 Running app launch tests..."
            python3 -m pytest tests/test_app_launch.py -v --tb=short
            ;;
        nav|navigation)
            echo "🧭 Running navigation tests..."
            python3 -m pytest tests/test_navigation.py -v --tb=short
            ;;
        logs)
            echo "📄 Running tests and showing logs..."
            python3 -m pytest tests/ -v --tb=short --log-cli-level=DEBUG
            ;;
        quick)
            echo "⚡ Running quick tests only..."
            python3 -m pytest tests/ -v --tb=short -x -m "not slow"
            ;;
        *)
            echo "❌ Unknown mode: $MODE"
            show_help
            exit 1
            ;;
    esac
}

show_help() {
    echo ""
    echo "Usage: ./run_tests.sh [MODE]"
    echo ""
    echo "Modes:"
    echo "  all          - Run all tests (default)"
    echo "  launch       - Run app launch tests only"
    echo "  nav          - Run navigation tests only"
    echo "  logs         - Run tests with debug logs"
    echo "  quick        - Run quick tests only (no slow ones)"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh"
    echo "  ./run_tests.sh launch"
    echo "  ./run_tests.sh logs"
}

# Show help if requested
if [[ "$MODE" == "help" || "$MODE" == "-h" || "$MODE" == "--help" ]]; then
    show_help
    exit 0
fi

# Run the tests
run_tests
TEST_RESULT=$?

echo ""
echo "======================================"
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed."
fi

# Show recent log entries
echo ""
echo "📋 Recent log entries:"
echo "----------------------"
LOG_FILE="$HOME/.local/share/nis2-audit/logs/nis2_audit.log"
if [ -f "$LOG_FILE" ]; then
    tail -10 "$LOG_FILE"
else
    echo "(No log file found)"
fi

echo ""
exit $TEST_RESULT
