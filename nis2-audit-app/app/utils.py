"""Utility functions for NIS2 Field Audit Tool."""
import os
import platform
import time
import functools
from pathlib import Path
from typing import Optional, Callable


def get_app_data_dir() -> Path:
    """
    Get the application data directory.
    
    Returns:
        Path to the application data directory
    """
    system = platform.system()
    
    if system == "Windows":
        # Windows: Use LOCALAPPDATA or fallback to AppData/Local
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData/Local")
    elif system == "Darwin":
        # macOS: Use Application Support
        base = Path.home() / "Library/Application Support"
    else:
        # Linux/Unix: Use XDG_DATA_HOME or fallback to .local/share
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
    
    app_dir = base / "nis2-audit"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_db_path() -> str:
    """
    Get the database file path.
    
    Returns:
        Path to the SQLite database file
    """
    return str(get_app_data_dir() / "audit_sessions.db")


def get_config_dir() -> Path:
    """
    Get the configuration directory.
    
    Returns:
        Path to the configuration directory
    """
    system = platform.system()
    
    if system == "Windows":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData/Roaming")
    elif system == "Darwin":
        base = Path.home() / "Library/Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    
    config_dir = base / "nis2-audit"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_log_dir() -> Path:
    """
    Get the log directory.
    
    Returns:
        Path to the log directory
    """
    # Logs go in the app data directory
    log_dir = get_app_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


# Alias for backward compatibility
get_config_path = get_config_dir


def get_css_path() -> str:
    """
    Get the CSS file path.
    Works both when running from source and when installed via pip.
    
    Returns:
        Path to the CSS file
    """
    try:
        # Try to use importlib.resources (Python 3.9+)
        import importlib.resources as pkg_resources
        return str(pkg_resources.files(__package__) / "tui" / "app.css")
    except (ImportError, AttributeError):
        # Fallback for older Python or when running from source
        module_dir = Path(__file__).parent
        css_path = module_dir / "tui" / "app.css"
        if css_path.exists():
            return str(css_path)
        
        # Last resort: return the relative path
        return "tui/app.css"


# ============================================================================
# Rate Limiting (2026 Security Fix)
# ============================================================================

class RateLimiter:
    """
    Simple rate limiter for network operations.
    Prevents flooding attacks and resource exhaustion.
    """
    
    def __init__(self, max_calls: int, per_seconds: int):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed
            per_seconds: Time window in seconds
        """
        self.max_calls = max_calls
        self.per_seconds = per_seconds
        self.calls = []
    
    def is_allowed(self) -> bool:
        """Check if a call is allowed under the rate limit."""
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.per_seconds]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
    
    def time_until_next(self) -> float:
        """Get seconds until next call is allowed."""
        if len(self.calls) < self.max_calls:
            return 0
        now = time.time()
        oldest = min(self.calls)
        return max(0, self.per_seconds - (now - oldest))


# Global rate limiters for different operations
_scan_rate_limiter = RateLimiter(max_calls=10, per_seconds=60)  # 10 scans per minute
_connection_rate_limiter = RateLimiter(max_calls=20, per_seconds=60)  # 20 connections per minute

# Per-IP connection rate limiter (2026: CVE-2026-20080 pattern - SSH flooding)
_ip_connection_limiters: dict[str, RateLimiter] = {}


def get_ip_rate_limiter(ip_address: str) -> RateLimiter:
    """
    Get or create a rate limiter for a specific IP address.
    Prevents per-target SSH connection flooding.
    
    Args:
        ip_address: Target IP address
        
    Returns:
        RateLimiter for that IP
    """
    if ip_address not in _ip_connection_limiters:
        # 5 connections per minute per IP (stricter than global)
        _ip_connection_limiters[ip_address] = RateLimiter(
            max_calls=5, per_seconds=60
        )
    return _ip_connection_limiters[ip_address]


def check_ip_connection_rate_limit(ip_address: str) -> bool:
    """
    Check if a connection to a specific IP is allowed.
    
    Args:
        ip_address: Target IP address
        
    Returns:
        True if allowed, False if rate limited
    """
    limiter = get_ip_rate_limiter(ip_address)
    return limiter.is_allowed()


def rate_limit(max_calls: int = 10, per_seconds: int = 60, limiter_name: str = "default"):
    """
    Decorator to rate limit function calls.
    
    Args:
        max_calls: Maximum calls allowed in time window
        per_seconds: Time window in seconds
        limiter_name: Name for separate rate limiter instances
        
    Raises:
        RuntimeError: If rate limit exceeded
    """
    limiters = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if limiter_name not in limiters:
                limiters[limiter_name] = RateLimiter(max_calls, per_seconds)
            
            limiter = limiters[limiter_name]
            
            if not limiter.is_allowed():
                wait_time = limiter.time_until_next()
                raise RuntimeError(
                    f"Rate limit exceeded for {func.__name__}. "
                    f"Try again in {wait_time:.1f} seconds."
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def check_scan_rate_limit() -> None:
    """
    Check if a scan operation is allowed under rate limit.
    
    Raises:
        RuntimeError: If scan rate limit exceeded
    """
    if not _scan_rate_limiter.is_allowed():
        wait_time = _scan_rate_limiter.time_until_next()
        raise RuntimeError(
            f"Scan rate limit exceeded. Maximum 10 scans per minute. "
            f"Try again in {wait_time:.1f} seconds."
        )


def check_connection_rate_limit() -> None:
    """
    Check if a connection operation is allowed under rate limit.
    
    Raises:
        RuntimeError: If connection rate limit exceeded
    """
    if not _connection_rate_limiter.is_allowed():
        wait_time = _connection_rate_limiter.time_until_next()
        raise RuntimeError(
            f"Connection rate limit exceeded. Maximum 20 connections per minute. "
            f"Try again in {wait_time:.1f} seconds."
        )
