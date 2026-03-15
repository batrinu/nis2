"""
Tests for app startup and basic functionality.

Run with: pytest tests/test_app_launch.py -v
"""
import pytest
from pathlib import Path


@pytest.mark.anyio
async def test_app_imports() -> None:
    """Test that app modules import without errors."""
    from app.textual_app import NIS2AuditApp
    from app.tui.screens.splash import SplashScreen
    from app.tui.screens.dashboard import Dashboard
    from app.tui.screens.onboarding import OnboardingScreen
    assert True  # If we get here, imports worked


@pytest.mark.anyio
async def test_app_creation() -> None:
    """Test that the NIS2AuditApp can be created and has required attributes."""
    from app.textual_app import NIS2AuditApp
    app = NIS2AuditApp()
    assert app is not None
    assert app.CSS_PATH is not None


@pytest.mark.anyio
async def test_app_starts_and_shows_splash() -> None:
    """Test that app starts and displays the splash screen."""
    from app.textual_app import NIS2AuditApp
    from app.tui.screens.splash import SplashScreen
    
    app = NIS2AuditApp()
    async with app.run_test() as pilot:
        # App should start
        assert app.screen is not None
        # Should be on splash screen
        assert isinstance(app.screen, SplashScreen)
        # Let it settle
        await pilot.pause()


@pytest.mark.anyio
async def test_key_presses_dont_crash() -> None:
    """Test that pressing various keys doesn't crash the app."""
    from app.textual_app import NIS2AuditApp
    
    app = NIS2AuditApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        
        # Press various keys
        keys = ["right", "left", "up", "down", "space", "enter", "q", "?"]
        for key in keys:
            await pilot.press(key)
            await pilot.pause()
            # If we get here without exception, test passed
            assert True


@pytest.mark.anyio
async def test_app_logs_work() -> None:
    """Test that the logging system works without errors."""
    from app.textual_app import NIS2AuditApp
    import logging
    
    app = NIS2AuditApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        
        # Just verify we can log without errors
        logging.info("Test log message")
        assert True  # If we get here, logging works


@pytest.mark.anyio
async def test_all_screens_instantiate() -> None:
    """Test that all screen classes can be instantiated without errors."""
    from app.tui.screens.splash import SplashScreen
    from app.tui.screens.dashboard import Dashboard
    from app.tui.screens.onboarding import OnboardingScreen
    from app.tui.screens.new_session import NewSessionWizard
    from app.tui.screens.scan import ScanScreen
    from app.tui.screens.connect import ConnectScreen
    from app.tui.screens.checklist import ChecklistScreen
    from app.tui.screens.findings import FindingsScreen
    from app.tui.screens.report import ReportScreen
    
    # These should all create without errors
    SplashScreen()
    Dashboard("./test.db")
    OnboardingScreen()
    NewSessionWizard("./test.db")
    ScanScreen("./test.db")
    ConnectScreen("./test.db")
    ChecklistScreen("./test.db")
    FindingsScreen("./test.db")
    ReportScreen("./test.db")
    # If we get here, all screens instantiated successfully
    assert True
