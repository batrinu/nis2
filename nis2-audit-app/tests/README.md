# Testing Guide for NIS2 Field Audit Tool

## 🚀 Quick Start

Run all tests with one command:
```bash
./run_tests.sh
```

Or use pytest directly:
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_app_launch.py

# Run with logs visible
pytest -v --log-cli-level=INFO
```

## 📁 Test Files

- `test_app_launch.py` - Tests for app startup, imports, and basic functionality
- `test_navigation.py` - Tests for screen navigation and user interactions
- `conftest.py` - Shared fixtures and configuration

## 🔧 Test Modes

The `run_tests.sh` script supports different modes:

| Mode | Command | Description |
|------|---------|-------------|
| all | `./run_tests.sh` | Run all tests |
| launch | `./run_tests.sh launch` | Test app startup only |
| nav | `./run_tests.sh nav` | Test navigation only |
| logs | `./run_tests.sh logs` | Show debug logs during tests |
| quick | `./run_tests.sh quick` | Skip slow tests |

## 🧪 Writing New Tests

### Basic Test Template

```python
async def test_my_feature():
    """Description of what this test checks."""
    from app.textual_app import NIS2AuditApp
    
    app = NIS2AuditApp()
    async with app.run_test() as pilot:
        # Your test code here
        await pilot.pause()
        
        # Make assertions
        assert app.screen is not None
```

### Testing Key Presses

```python
async def test_key_press():
    """Test that pressing a key works."""
    from app.textual_app import NIS2AuditApp
    
    app = NIS2AuditApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        
        # Press a key
        await pilot.press("right")
        await pilot.pause()
        
        # Check result
        assert isinstance(app.screen, ExpectedScreen)
```

### Testing Button Clicks

```python
async def test_button_click():
    """Test clicking a button."""
    from app.textual_app import NIS2AuditApp
    
    app = NIS2AuditApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        
        # Click a button by ID
        await pilot.click("#button-id")
        await pilot.pause()
```

### Checking Logs

Tests automatically capture logs. You can check them:

```python
import logging

async def test_with_logging(caplog):
    """Test that checks log output."""
    with caplog.at_level(logging.INFO):
        # Run your test
        pass
    
    # Check logs
    assert "Expected log message" in caplog.text
```

## 📋 Common Assertions

```python
# Check current screen type
assert isinstance(app.screen, Dashboard)

# Check widget exists
widget = app.screen.query_one("#widget-id")
assert widget is not None

# Check widget text
assert widget.render() == "Expected text"

# Check app state
assert app._running
```

## 🐛 Debugging Failed Tests

### See Full Traceback
```bash
pytest -v --tb=long
```

### Stop on First Failure
```bash
pytest -x
```

### Run Single Test
```bash
pytest tests/test_app_launch.py::test_app_creation -v
```

### Check Logs After Test
```bash
# Run test then check logs
./run_tests.sh
cat ~/.local/share/nis2-audit/logs/nis2_audit.log
```

## 📝 Test Configuration

The `pytest.ini` file contains:
- Auto asyncio mode (no decorators needed)
- Log capture settings
- Test discovery patterns

You can override settings on the command line:
```bash
# Change log level
pytest --log-cli-level=DEBUG

# Disable log capture
pytest --no-log-cli
```

## 🎯 Test Coverage Areas

1. **App Launch**
   - Imports work
   - App starts without errors
   - Initial screen displays

2. **Navigation**
   - Screen transitions work
   - Key presses handled
   - Buttons clickable

3. **Error Handling**
   - Graceful error recovery
   - No crashes on bad input
   - Help system works

4. **User Flows**
   - Complete user journeys
   - First-run experience
   - Returning user experience
