"""
Global error handling for the NIS2 Field Audit App.

Provides:
- Global exception hook
- Structured error reporting
- Crash recovery
- User-friendly error messages
"""
import sys
import traceback
import logging
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Callable, Any, Type
from dataclasses import dataclass
from enum import Enum, auto

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()
    FATAL = auto()


class ErrorCategory(Enum):
    """Error categories for user-friendly messages."""
    DATABASE = "database"
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class AppError:
    """Structured application error."""
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    traceback: Optional[str] = None
    context: Optional[dict] = None
    timestamp: str = None
    recoverable: bool = False
    suggested_action: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat() + 'Z'
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'message': self.message,
            'category': self.category.value,
            'severity': self.severity.name,
            'exception_type': self.exception_type,
            'exception_message': self.exception_message,
            'context': self.context,
            'timestamp': self.timestamp,
            'recoverable': self.recoverable,
            'suggested_action': self.suggested_action
        }


# Error message templates for users
ERROR_MESSAGES = {
    ErrorCategory.DATABASE: {
        'title': 'Database Error',
        'template': 'A database error occurred: {message}',
        'actions': {
            'sqlite3.OperationalError': 'Check if the database file is accessible and not corrupted.',
            'sqlite3.DatabaseError': 'The database may be corrupted. Try restoring from a backup.',
            'default': 'Please try again or contact support if the issue persists.'
        }
    },
    ErrorCategory.NETWORK: {
        'title': 'Network Error',
        'template': 'Network operation failed: {message}',
        'actions': {
            'TimeoutError': 'The operation timed out. Check your network connection and try again.',
            'ConnectionRefusedError': 'Could not connect to the target. Verify the address is correct.',
            'default': 'Check your network connection and try again.'
        }
    },
    ErrorCategory.FILE_SYSTEM: {
        'title': 'File System Error',
        'template': 'File operation failed: {message}',
        'actions': {
            'PermissionError': 'Insufficient permissions. Run as administrator or check file permissions.',
            'FileNotFoundError': 'Required file not found. Please check the path and try again.',
            'default': 'Check file permissions and available disk space.'
        }
    },
    ErrorCategory.VALIDATION: {
        'title': 'Validation Error',
        'template': 'Invalid input: {message}',
        'actions': {
            'default': 'Please check your input and try again.'
        }
    },
    ErrorCategory.AUTHENTICATION: {
        'title': 'Authentication Error',
        'template': 'Authentication failed: {message}',
        'actions': {
            'default': 'Check your credentials and try again.'
        }
    },
    ErrorCategory.PERMISSION: {
        'title': 'Permission Denied',
        'template': 'Insufficient permissions: {message}',
        'actions': {
            'default': 'Run the application as administrator or check permissions.'
        }
    },
    ErrorCategory.TIMEOUT: {
        'title': 'Operation Timeout',
        'template': 'Operation timed out: {message}',
        'actions': {
            'default': 'Try again with a longer timeout or reduce the scope of the operation.'
        }
    },
    ErrorCategory.UNKNOWN: {
        'title': 'Unexpected Error',
        'template': 'An unexpected error occurred: {message}',
        'actions': {
            'default': 'Please restart the application. If the issue persists, contact support.'
        }
    }
}


def categorize_exception(exc: Exception) -> ErrorCategory:
    """Categorize an exception for user-friendly handling."""
    exc_type = type(exc).__name__
    module = type(exc).__module__
    
    # Database errors
    if module == 'sqlite3' or 'database' in exc_type.lower():
        return ErrorCategory.DATABASE
    
    # Network errors
    if any(name in exc_type.lower() for name in ['connection', 'timeout', 'network', 'socket']):
        if isinstance(exc, TimeoutError):
            return ErrorCategory.TIMEOUT
        return ErrorCategory.NETWORK
    
    # File system errors
    if any(name in exc_type.lower() for name in ['file', 'directory', 'path', 'permission', 'access']):
        if isinstance(exc, PermissionError):
            return ErrorCategory.PERMISSION
        return ErrorCategory.FILE_SYSTEM
    
    # Validation errors
    if any(name in exc_type.lower() for name in ['validation', 'value', 'type', 'key']):
        return ErrorCategory.VALIDATION
    
    # Authentication errors
    if any(name in exc_type.lower() for name in ['auth', 'credential', 'login', 'password']):
        return ErrorCategory.AUTHENTICATION
    
    return ErrorCategory.UNKNOWN


def get_user_friendly_message(error: AppError) -> str:
    """Get a user-friendly error message."""
    category_info = ERROR_MESSAGES.get(error.category, ERROR_MESSAGES[ErrorCategory.UNKNOWN])
    
    # Safely get template with fallback
    template = category_info.get('template', 'An error occurred: {message}')
    message = template.format(message=error.message)
    
    # Get suggested action safely
    actions = category_info.get('actions', {})
    action = actions.get(error.exception_type) if error.exception_type else None
    if action is None:
        action = actions.get('default', 'Please try again or contact support if the issue persists.')
    
    if error.suggested_action:
        action = error.suggested_action
    
    return f"""
{category_info['title']}
{'=' * len(category_info['title'])}

{message}

Suggested action:
{action}
""".strip()


class ErrorHandler:
    """Global error handler for the application."""
    
    _instance = None
    _error_callbacks: list[Callable[[AppError], None]] = []
    _crash_log_dir: Optional[Path] = None
    _original_excepthook: Optional[Callable] = None
    _gui_mode: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._error_callbacks = []
            cls._instance._original_excepthook = sys.excepthook
        return cls._instance
    
    def initialize(
        self,
        crash_log_dir: Optional[Path] = None,
        gui_mode: bool = False
    ) -> None:
        """
        Initialize the error handler.
        
        Args:
            crash_log_dir: Directory for crash logs
            gui_mode: Whether running in GUI/TUI mode
        """
        self._crash_log_dir = crash_log_dir
        self._gui_mode = gui_mode
        
        # Install global exception hook
        sys.excepthook = self._handle_uncaught_exception
        
        logger.debug("Error handler initialized")
    
    def _handle_uncaught_exception(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_traceback: Any
    ) -> None:
        """Handle uncaught exceptions."""
        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        category = categorize_exception(exc_value)
        severity = ErrorSeverity.CRITICAL if issubclass(exc_type, Exception) else ErrorSeverity.FATAL
        
        error = AppError(
            message=str(exc_value) or f"{exc_type.__name__} occurred",
            category=category,
            severity=severity,
            exception_type=exc_type.__name__,
            exception_message=str(exc_value),
            traceback=tb_str,
            recoverable=False
        )
        
        logger.critical(
            f"Uncaught exception: {exc_type.__name__}: {exc_value}",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        self._save_crash_report(error)
        
        for callback in self._error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error callback failed: {e}", exc_info=True)
        
        if self._original_excepthook:
            self._original_excepthook(exc_type, exc_value, exc_traceback)
    
    def _save_crash_report(self, error: AppError) -> Optional[Path]:
        """Save a crash report to file."""
        if self._crash_log_dir is None:
            return None
        
        try:
            self._crash_log_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            crash_file = self._crash_log_dir / f"crash_{timestamp}.json"
            
            report = {
                'error': error.to_dict(),
                'system_info': {
                    'python_version': sys.version,
                    'platform': sys.platform,
                    'executable': sys.executable,
                }
            }
            
            with open(crash_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Crash report saved to {crash_file}")
            return crash_file
        except Exception as e:
            logger.error(f"Failed to save crash report: {e}", exc_info=True)
            return None
    
    def register_callback(self, callback: Callable[[AppError], None]) -> None:
        """Register a callback for error notifications."""
        self._error_callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable[[AppError], None]) -> None:
        """Unregister an error callback."""
        if callback in self._error_callbacks:
            self._error_callbacks.remove(callback)
    
    def handle_exception(
        self,
        exc: Exception,
        context: Optional[dict] = None,
        recoverable: bool = False,
        user_message: Optional[str] = None
    ) -> AppError:
        """
        Handle an exception programmatically.
        
        Args:
            exc: The exception to handle
            context: Additional context information
            recoverable: Whether the error is recoverable
            user_message: Optional custom user-facing message
            
        Returns:
            Structured AppError
        """
        category = categorize_exception(exc)
        tb = traceback.format_exc()
        
        error = AppError(
            message=user_message or str(exc),
            category=category,
            severity=ErrorSeverity.ERROR,
            exception_type=type(exc).__name__,
            exception_message=str(exc),
            traceback=tb,
            context=context,
            recoverable=recoverable,
            suggested_action=self._get_suggested_action(exc, category)
        )
        
        # Log based on severity
        if category == ErrorCategory.DATABASE and 'corrupt' in str(exc).lower():
            logger.critical(f"Database error: {exc}", exc_info=True)
        else:
            logger.error(f"Handled exception: {exc}", exc_info=True)
        
        # Notify callbacks
        for callback in self._error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error callback failed: {e}", exc_info=True)
        
        return error
    
    def _get_suggested_action(self, exc: Exception, category: ErrorCategory) -> str:
        """Get suggested action for an exception."""
        exc_type = type(exc).__name__
        category_info = ERROR_MESSAGES.get(category, ERROR_MESSAGES[ErrorCategory.UNKNOWN])
        
        actions = category_info.get('actions', {})
        return actions.get(
            exc_type,
            actions.get('default', 'Please try again or contact support if the issue persists.')
        )


def initialize_error_handling(
    crash_log_dir: Optional[Path] = None,
    gui_mode: bool = False
) -> ErrorHandler:
    """Initialize global error handling."""
    handler = ErrorHandler()
    handler.initialize(crash_log_dir=crash_log_dir, gui_mode=gui_mode)
    return handler


def get_error_handler() -> ErrorHandler:
    """Get the error handler instance."""
    return ErrorHandler()


# Decorator for function-level error handling
def handle_errors(
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    recoverable: bool = False,
    default_return: Any = None
):
    """
    Decorator for handling errors in functions.
    
    Args:
        category: Default error category
        recoverable: Whether errors are recoverable
        default_return: Value to return on error
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                handler = get_error_handler()
                ctx = {'function': func.__name__, 'args': str(args), 'kwargs': str(kwargs)}
                error = handler.handle_exception(exc, context=ctx, recoverable=recoverable)
                
                if not recoverable:
                    raise
                
                logger.warning(f"Recoverable error in {func.__name__}: {error.message}")
                return default_return
        return wrapper
    return decorator


# Context manager for operation-level error handling
class ErrorContext:
    """Context manager for handling errors in code blocks."""
    
    def __init__(
        self,
        operation_name: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        recoverable: bool = False,
        on_error: Optional[Callable[[AppError], None]] = None
    ):
        self.operation_name = operation_name
        self.category = category
        self.recoverable = recoverable
        self.on_error = on_error
        self.error: Optional[AppError] = None
    
    def __enter__(self) -> 'ErrorContext':
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            handler = get_error_handler()
            ctx = {'operation': self.operation_name}
            self.error = handler.handle_exception(
                exc_val,
                context=ctx,
                recoverable=self.recoverable
            )
            
            if self.on_error:
                self.on_error(self.error)
            
            return self.recoverable  # Suppress exception if recoverable
        
        return False
