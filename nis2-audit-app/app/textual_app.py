"""Main Textual application for NIS2 Field Audit Tool.
RomEnglish localization: Technical terms in English, actions in Romanian.
"""
import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional
from textual.app import App
from textual.reactive import reactive
from textual.timer import Timer

from .utils import get_db_path, get_css_path, get_log_dir
from .config import get_config, ConfigurationManager
from .logging_config import setup_logging, log_audit_event
from .error_handling import initialize_error_handling, get_error_handler, ErrorCategory
from .storage.db import AuditStorage, DatabaseError
from .user_experience import PreferenceManager
from .startup_checks import is_first_run
from .tui.screens.splash import SplashScreen
from .tui.screens.dashboard import Dashboard
from .tui.screens.new_session import NewSessionWizard
from .tui.screens.scan import ScanScreen
from .tui.screens.connect import ConnectScreen
from .tui.screens.checklist import ChecklistScreen
from .tui.screens.findings import FindingsScreen
from .tui.screens.report import ReportScreen
from .tui.screens.onboarding import OnboardingScreen
from .tui.components.shortcut_help import ShortcutHelpScreen
from .tui.components.help_system import HelpModal, GlossaryModal, WalkthroughOverlay
from .i18n import get_text as _

# Module logger
logger = logging.getLogger(__name__)


class NIS2AuditApp(App):
    """Main Textual application for NIS2 compliance audits."""
    
    CSS_PATH = get_css_path()
    
    # Global bindings available everywhere
    BINDINGS = [
        ("?", "show_shortcuts", "Scurtături Tastatură"),
        ("f1", "show_help", "Ajutor"),
    ]
    
    # Global app state
    session_id: reactive[Optional[str]] = reactive(None)
    db_path = get_db_path()
    
    def __init__(self, *args, **kwargs):
        """Initialize the app."""
        super().__init__(*args, **kwargs)
        self.storage = None
        self._last_activity = time.time()
        self._idle_timeout = 1800  # 30 minutes default
        self._idle_timer: Optional[Timer] = None
    
    def on_mount(self) -> None:
        """Register screens and handle first-run experience."""
        try:
            self.storage = AuditStorage(self.db_path)
            logger.info(f"Database initialized at {self.db_path}")
        except DatabaseError as e:
            logger.error(f"Failed to initialize database: {e}")
            # Show error notification (Textual notification)
            self.notify(
                f"Eroare bază de date: {e}\nVerifică log-urile pentru detalii.",
                severity="error",
                timeout=10
            )
            raise
        
        config_dir = os.path.expanduser("~/.nis2-audit")
        first_run = is_first_run(config_dir)
        
        if first_run:
            logger.info("First run detected - showing onboarding wizard")
        else:
            logger.info("Returning user - skipping onboarding")
        
        # Register screens
        self.install_screen(SplashScreen(), name="splash")
        self.install_screen(Dashboard(self.db_path), name="dashboard")
        self.install_screen(NewSessionWizard(self.db_path), name="new_session")
        self.install_screen(ScanScreen(self.db_path), name="scan")
        self.install_screen(ConnectScreen(self.db_path), name="connect")
        self.install_screen(ChecklistScreen(self.db_path), name="checklist")
        self.install_screen(FindingsScreen(self.db_path), name="findings")
        self.install_screen(ReportScreen(self.db_path), name="report")
        
        # Register onboarding screen only for first run
        if first_run:
            self.install_screen(OnboardingScreen(), name="onboarding")
        
        self.push_screen("splash")
        
        config = get_config()
        self._idle_timeout = config.idle_timeout
        if self._idle_timeout > 0:
            self._start_idle_timer()
        
        # Log app start
        log_audit_event(
            event_type="app_started",
            user="system",
            details={"version": "1.0.0", "theme": "amber", "first_run": first_run}
        )
    
    def _start_idle_timer(self) -> None:
        """Start the idle timeout timer."""
        self._idle_timer = self.set_interval(60, self._check_idle_timeout)
    
    def _check_idle_timeout(self) -> None:
        """Check if user has been idle too long."""
        idle_time = time.time() - self._last_activity
        if idle_time > float(self._idle_timeout):
            # Lock the application
            self._lock_application()
    
    def _lock_application(self) -> None:
        """Lock the application due to inactivity."""
        logger.warning("Application locked due to inactivity")
        self.notify(
            "Sesiune blocată din cauza inactivității. Apasă orice tastă pentru deblocare.",
            severity="warning",
            timeout=10
        )
        # In a real implementation, this would show a lock screen
        # For now, we just log and notify
    
    def _update_activity(self) -> None:
        """Update last activity timestamp."""
        self._last_activity = time.time()
    
    def on_key(self, event) -> None:
        """Handle key events - update activity."""
        self._update_activity()
    
    def on_click(self, event) -> None:
        """Handle click events - update activity."""
        self._update_activity()
    
    def action_show_shortcuts(self) -> None:
        """Show keyboard shortcuts overlay."""
        context = 'global'
        if self.screen:
            screen_name = self.screen.__class__.__name__.lower()
            if 'dashboard' in screen_name:
                context = 'dashboard'
            elif 'scan' in screen_name:
                context = 'scan'
            elif 'checklist' in screen_name:
                context = 'checklist'
        
        self.push_screen(ShortcutHelpScreen(context))
    
    def action_show_help(self) -> None:
        """Show help for current screen."""
        screen_name = 'dashboard'
        if self.screen:
            name = self.screen.__class__.__name__.lower()
            if 'dashboard' in name:
                screen_name = 'dashboard'
            elif 'newsession' in name or 'new_session' in name:
                screen_name = 'new_session'
            elif 'scan' in name:
                screen_name = 'scan'
            elif 'checklist' in name:
                screen_name = 'checklist'
            elif 'finding' in name:
                screen_name = 'findings'
            elif 'report' in name:
                screen_name = 'report'
        
        def on_help_close(result):
            if result == "glossary":
                self.push_screen(GlossaryModal())
            elif result == "tutorial":
                self.push_screen(WalkthroughOverlay())
        
        self.push_screen(HelpModal(screen_name), on_help_close)
    
    def on_exit(self) -> None:
        """Clean up on exit."""
        log_audit_event(
            event_type="app_exited",
            user="system",
            details={"session_id": self.session_id}
        )
        logger.info("Application exiting")
    
    def get_session_id(self) -> Optional[str]:
        """Get current session ID."""
        return self.session_id
    
    def set_session_id(self, session_id):
        """Set current session ID and update screens."""
        self.session_id = session_id
        
        for screen_name in ["scan", "connect", "checklist", "findings", "report"]:
            screen = self.get_screen(screen_name)
            if hasattr(screen, 'session_id'):
                screen.session_id = session_id


def initialize_app():
    """
    Initialize all application components.
    
    This function sets up:
    - Configuration management
    - Logging system
    - Error handling
    - Database connections
    """
    config = get_config()
    
    log_dir = Path(config.logging.directory) if config.logging.directory else None
    setup_logging(
        log_level=config.logging.level,
        log_dir=log_dir,
        max_bytes=config.logging.max_bytes,
        backup_count=config.logging.backup_count,
        json_format=config.logging.json_format,
        console_output=config.logging.console
    )
    
    crash_dir = log_dir / "crashes" if log_dir else None
    handler = initialize_error_handling(
        crash_log_dir=crash_dir,
        gui_mode=True
    )
    
    # Register error callback for notifications
    def on_error(error):
        logger.error(f"Error reported: {error.message}")
    
    handler.register_callback(on_error)
    
    logger.info("=" * 60)
    logger.info("NIS2 Field Audit Tool Starting")
    logger.info(f"Config directory: {ConfigurationManager()._config_path}")
    logger.info(f"Database path: {config.database.path}")
    logger.info(f"Log directory: {config.logging.directory}")
    logger.info("=" * 60)
    
    return config


def main():
    """Entry point for the Textual app."""
    try:
        config = initialize_app()
        
        app = NIS2AuditApp()
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        # This shouldn't happen if error handling is working,
        # but just in case...
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"Fatal error: {e}", file=sys.stderr)
        print("Check the log files for details.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
