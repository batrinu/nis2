"""
Production logging configuration for the NIS2 Field Audit App.

Provides:
- Rotating file handlers with compression
- Structured logging support
- Per-module log level control
- Audit trail logging
"""
import json
import logging
import logging.handlers
import gzip
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, Union
from contextvars import ContextVar
import sys
from .security_utils import sanitize_for_logging, sanitize_dict_for_logging

# Context variable for request/session correlation
session_context: ContextVar[Dict[str, Any]] = ContextVar('session_context', default={})


class SessionFilter(logging.Filter):
    """Add session context to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        ctx = session_context.get()
        record.session_id = ctx.get('session_id', '-')
        record.user = ctx.get('user', '-')
        record.ip = ctx.get('ip', '-')
        return True


class SensitiveDataFilter(logging.Filter):
    """
    Filter sensitive data from log records.
    
    SECURITY: Prevents credentials, tokens, and secrets from appearing in logs.
    This is a defense-in-depth measure - sensitive data should never be logged,
    but this filter provides a safety net in case it accidentally is.
    """
    
    # Patterns to match sensitive data (key=value or key: value formats)
    SENSITIVE_PATTERNS = [
        # Password patterns
        (r'password\s*[=:]\s*\S+', 'password=***'),
        (r'passwd\s*[=:]\s*\S+', 'passwd=***'),
        (r'pwd\s*[=:]\s*\S+', 'pwd=***'),
        # Secret patterns
        (r'secret\s*[=:]\s*\S+', 'secret=***'),
        (r'api[_-]?key\s*[=:]\s*\S+', 'api_key=***'),
        (r'auth[_-]?token\s*[=:]\s*\S+', 'auth_token=***'),
        (r'access[_-]?token\s*[=:]\s*\S+', 'access_token=***'),
        (r'bearer\s+\S+', 'bearer ***'),
        # SSH/Key patterns
        (r'private[_-]?key\s*[=:]\s*\S+', 'private_key=***'),
        (r'ssh[_-]?key\s*[=:]\s*\S+', 'ssh_key=***'),
        # Credential patterns
        (r'credential\s*[=:]\s*\S+', 'credential=***'),
        (r'enable[_-]?password\s*[=:]\s*\S+', 'enable_password=***'),
        (r'secret\s+5\s+\S+', 'secret 5 ***'),  # Cisco enable secret
        # Token patterns (generic)
        (r'token\s*[=:]\s*[a-zA-Z0-9_-]{20,}', 'token=***'),
        # Session patterns
        (r'session[_-]?id\s*[=:]\s*[a-zA-Z0-9_-]{20,}', 'session_id=***'),
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter sensitive data from the log message."""
        original_msg = record.getMessage()
        sanitized_msg = original_msg
        
        import re
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            try:
                sanitized_msg = re.sub(pattern, replacement, sanitized_msg, flags=re.IGNORECASE)
            except re.error:
                # If regex fails, skip this pattern
                continue
        
        # Also check the formatted message args
        if record.args:
            sanitized_args = []
            for arg in record.args:
                arg_str = str(arg)
                for pattern, replacement in self.SENSITIVE_PATTERNS:
                    try:
                        arg_str = re.sub(pattern, replacement, arg_str, flags=re.IGNORECASE)
                    except re.error:
                        continue
                sanitized_args.append(arg_str)
            record.args = tuple(sanitized_args)
        
        if sanitized_msg != original_msg:
            record.msg = sanitized_msg
            record.args = ()
        
        return True


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Pass 13: Sanitize message to prevent log injection
        safe_message = sanitize_for_logging(record.getMessage())
        
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': safe_message,
            'source': {
                'file': record.filename,
                'line': record.lineno,
                'function': record.funcName,
            },
            'session_id': sanitize_for_logging(getattr(record, 'session_id', '-')),
            'user': sanitize_for_logging(getattr(record, 'user', '-')),
            'ip': sanitize_for_logging(getattr(record, 'ip', '-')),
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        for key, value in record.__dict__.items():
            if key not in log_data and not key.startswith('_'):
                try:
                    # Ensure JSON serializable
                    json.dumps({key: value})
                    log_data[key] = value
                except (TypeError, ValueError):
                    log_data[key] = str(value)
        
        return json.dumps(log_data, default=str)


class CompressedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Rotating file handler that compresses old log files."""
    
    def doRollover(self) -> None:
        """Override to compress the old log file."""
        if self.stream:
            self.stream.close()
            self.stream = None
        
        if os.path.exists(self.baseFilename):
            # Rotate existing backups
            for i in range(self.backupCount - 1, 0, -1):
                src = f"{self.baseFilename}.{i}.gz"
                dst = f"{self.baseFilename}.{i + 1}.gz"
                if os.path.exists(src):
                    try:
                        if os.path.exists(dst):
                            os.remove(dst)
                        shutil.move(src, dst)
                    except (OSError, IOError) as e:
                        # Log rotation error shouldn't stop logging
                        pass
            
            # Compress the current log file
            compressed = f"{self.baseFilename}.1.gz"
            try:
                with open(self.baseFilename, 'rb') as f_in:
                    with gzip.open(compressed, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(self.baseFilename)
            except (OSError, IOError) as e:
                # Log rotation error shouldn't stop logging
                pass
        
        self.stream = self._open()


def get_log_directory() -> Path:
    """
    Get the appropriate log directory for the platform.
    
    Returns:
        Path to log directory
    """
    if os.name == 'nt':  # Windows
        base_dir = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local'))
    elif sys.platform == 'darwin':  # macOS
        base_dir = Path.home() / 'Library/Logs'
    else:  # Linux and others
        base_dir = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
    
    log_dir = base_dir / 'nis2-audit' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(
    log_level: Union[int, str] = logging.INFO,
    log_dir: Optional[Path] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    json_format: bool = False,
    console_output: bool = True,
) -> logging.Logger:
    """
    Configure production logging for the application.
    
    Args:
        log_level: Minimum log level (default: INFO)
        log_dir: Directory for log files. If None, uses platform default.
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        json_format: Use JSON formatting for structured logging
        console_output: Also log to console
        
    Returns:
        Configured root logger for the application
    """
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)
    
    if log_dir is None:
        log_dir = get_log_directory()
    else:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger('nis2_audit')
    logger.setLevel(log_level)
    logger.handlers = []  # Clear existing handlers
    
    session_filter = SessionFilter()
    logger.addFilter(session_filter)
    
    # Prevent credential leakage in logs
    sensitive_filter = SensitiveDataFilter()
    logger.addFilter(sensitive_filter)
    
    if json_format:
        file_formatter = JSONFormatter()
        console_formatter = JSONFormatter()
    else:
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - '
            '[%(session_id)s] [%(user)s] - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
    
    # Rotating file handler with compression
    log_file = log_dir / 'nis2_audit.log'
    file_handler = CompressedRotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(session_filter)
    file_handler.addFilter(sensitive_filter)
    logger.addHandler(file_handler)
    
    # Separate error log
    error_file = log_dir / 'nis2_audit_errors.log'
    error_handler = CompressedRotatingFileHandler(
        error_file,
        maxBytes=max_bytes // 2,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    error_handler.addFilter(session_filter)
    error_handler.addFilter(sensitive_filter)
    logger.addHandler(error_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(max(log_level, logging.INFO))  # Don't spam console with debug
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(session_filter)
        console_handler.addFilter(sensitive_filter)
        logger.addHandler(console_handler)
    
    # Audit trail logger (separate file for compliance)
    audit_logger = logging.getLogger('nis2_audit.audit')
    audit_logger.setLevel(logging.INFO)
    audit_logger.handlers = []
    audit_logger.propagate = False  # Don't duplicate to parent
    
    audit_file = log_dir / 'audit_trail.log'
    audit_handler = CompressedRotatingFileHandler(
        audit_file,
        maxBytes=max_bytes,
        backupCount=10,  # Keep more audit logs
        encoding='utf-8'
    )
    audit_handler.setLevel(logging.INFO)
    audit_formatter = JSONFormatter() if json_format else logging.Formatter(
        '%(asctime)s - AUDIT - %(message)s'
    )
    audit_handler.setFormatter(audit_formatter)
    audit_logger.addHandler(audit_handler)
    
    logger.info(f"Logging initialized — level={logging.getLevelName(log_level)}, dir={log_dir}")
    
    return logger


def get_audit_logger() -> logging.Logger:
    """Get the audit trail logger."""
    return logging.getLogger('nis2_audit.audit')


def log_audit_event(
    event_type: str,
    session_id: Optional[str] = None,
    user: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an audit event for compliance trail.
    
    Args:
        event_type: Type of event (e.g., 'session_created', 'finding_added')
        session_id: Associated session ID
        user: User who performed the action
        details: Additional event details
    """
    logger = get_audit_logger()
    
    token = session_context.set({
        'session_id': session_id or '-',
        'user': user or '-',
    })
    
    try:
        log_data = {
            'event_type': event_type,
            'timestamp': datetime.now(timezone.utc).isoformat() + 'Z',
            'session_id': session_id,
            'user': user,
            'details': details or {}
        }
        logger.info(json.dumps(log_data, default=str))
    finally:
        session_context.reset(token)


def set_session_context(
    session_id: Optional[str] = None,
    user: Optional[str] = None,
    ip: Optional[str] = None
) -> Any:
    """
    Set context for the current session/scope.
    
    Returns a token that should be used with reset_session_context.
    
    Example:
        token = set_session_context(session_id='abc123', user='john.doe')
        try:
            # Do work
            logger.info("Processing...")  # Will include session context
        finally:
            reset_session_context(token)
    """
    return session_context.set({
        'session_id': session_id,
        'user': user,
        'ip': ip
    })


def reset_session_context(token: Any) -> None:
    """Reset the session context."""
    session_context.reset(token)


# Convenience function to configure logging from config
def configure_logging_from_config(config: Dict[str, Any]) -> logging.Logger:
    """
    Configure logging from a configuration dictionary.
    
    Config format:
        {
            'level': 'INFO',
            'directory': '/var/log/nis2-audit',
            'max_bytes': 10485760,
            'backup_count': 5,
            'json_format': False,
            'console': True,
            'modules': {
                'app.storage.db': 'DEBUG',
                'app.tui': 'WARNING'
            }
        }
    """
    logger = setup_logging(
        log_level=config.get('level', 'INFO'),
        log_dir=config.get('directory'),
        max_bytes=config.get('max_bytes', 10 * 1024 * 1024),
        backup_count=config.get('backup_count', 5),
        json_format=config.get('json_format', False),
        console_output=config.get('console', True),
    )
    
    for module, level in config.get('modules', {}).items():
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger(module).setLevel(level)
    
    return logger
