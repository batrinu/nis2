"""NIS2 Field Audit Tool - Main application package."""
from .config import get_config, ConfigurationManager
from .logging_config import setup_logging, log_audit_event, get_audit_logger
from .error_handling import (
    initialize_error_handling,
    get_error_handler,
    ErrorHandler,
    AppError,
    ErrorCategory,
    ErrorSeverity,
)
from .utils import get_db_path, get_css_path, get_log_dir, get_config_dir

__version__ = "1.0.0"
__all__ = [
    'get_config',
    'ConfigurationManager',
    'setup_logging',
    'log_audit_event',
    'get_audit_logger',
    'initialize_error_handling',
    'get_error_handler',
    'ErrorHandler',
    'AppError',
    'ErrorCategory',
    'ErrorSeverity',
    'get_db_path',
    'get_css_path',
    'get_log_dir',
    'get_config_dir',
]
