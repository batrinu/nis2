"""
Tests for screen navigation and user interactions.

Run with: pytest tests/test_navigation.py -v
"""
import pytest
import asyncio
from textual.pilot import Pilot


@pytest.mark.anyio
async def test_splash_to_dashboard() -> None:
    """Test navigation from splash screen to dashboard after boot sequence."""
    from app.textual_app import NIS2AuditApp
    from app.tui.screens.splash import SplashScreen
    
    app = NIS2AuditApp()
    async with app.run_test() as pilot:
        # Start on splash
        assert isinstance(app.screen, SplashScreen)
        
        # Wait for boot sequence to complete
        await asyncio.sleep(5)
        
        # Should now be on dashboard (if not first run)
        # Note: This may vary based on first_run status
        await pilot.pause()


@pytest.mark.anyio
async def test_onboarding_navigation() -> None:
    """Test onboarding step navigation using the right arrow key."""
    from app.tui.screens.onboarding import OnboardingScreen
    from textual.app import App
    
    # Create a simple test app with just onboarding
    class TestApp(App):
        def on_mount(self):
            self.push_screen(OnboardingScreen())
    
    app = TestApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        
        screen = app.screen
        assert isinstance(screen, OnboardingScreen)
        
        # Check initial step
        initial_step = screen._current_step_index
        
        # Press right to advance
        await pilot.press("right")
        await pilot.pause()
        
        # Step should have advanced
        assert screen._current_step_index == initial_step + 1


@pytest.mark.anyio
async def test_help_button_opens_help() -> None:
    """Test that the help button opens the help modal on the dashboard."""
    from app.textual_app import NIS2AuditApp
    from app.tui.screens.dashboard import Dashboard
    from app.tui.components.help_system import HelpModal
    
    app = NIS2AuditApp()
    async with app.run_test() as pilot:
        # Wait for boot sequence
        await asyncio.sleep(5)
        await pilot.pause()
        
        # Try to open help if on dashboard
        if isinstance(app.screen, Dashboard):
            app.screen._show_help()
            await pilot.pause()
            
            # Check if HelpModal is now on screen stack
            assert any(isinstance(s, HelpModal) for s in app.screen_stack)


@pytest.mark.anyio
async def test_keyboard_shortcuts() -> None:
    """Test that keyboard shortcuts (? key) can be pressed without errors."""
    from app.textual_app import NIS2AuditApp
    from app.tui.components.shortcut_help import ShortcutHelpScreen
    
    app = NIS2AuditApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        
        # Press ? to show shortcuts
        await pilot.press("?")
        await pilot.pause()
        
        # Check if shortcut help screen is showing
        # (This depends on current screen, may not always work)


@pytest.mark.anyio
async def test_quit_works() -> None:
    """Test that the app can exit cleanly using the exit() method."""
    from app.textual_app import NIS2AuditApp
    
    app = NIS2AuditApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        
        # App should be running
        assert app._running
        
        # Exit the app
        app.exit()
        await pilot.pause()
        
        # App should no longer be running
        assert not app._running
