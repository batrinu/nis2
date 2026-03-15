"""
Configuration management for the NIS2 Field Audit App.

Supports:
- Configuration files (JSON, YAML, TOML)
- Environment variable overrides
- Platform-specific defaults
- Runtime configuration updates
"""
import os
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from copy import deepcopy
import logging
from .security_utils import atomic_write, secure_file_permissions

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration."""
    path: Optional[str] = None  # None = use platform default
    backup_on_startup: bool = True
    integrity_check_on_startup: bool = True
    auto_vacuum: bool = True
    wal_mode: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    directory: Optional[str] = None  # None = use platform default
    max_bytes: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5
    json_format: bool = False
    console: bool = True
    modules: Dict[str, str] = field(default_factory=dict)


@dataclass
class SecurityConfig:
    """Security configuration."""
    require_encryption: bool = True
    max_scan_timeout: int = 300  # seconds
    allowed_networks: list = field(default_factory=list)  # CIDR blocks
    block_dangerous_commands: bool = True
    credential_timeout: int = 900  # seconds (reduced from 3600 for security)
    production_mode: bool = False  # Enable for production deployments


@dataclass
class ExportConfig:
    """Export configuration."""
    default_format: str = "docx"
    output_directory: Optional[str] = None
    include_evidence: bool = True
    include_raw_configs: bool = False
    watermark_text: str = "CONFIDENTIAL"


@dataclass
class AppConfig:
    """Application configuration."""
    # App info
    app_name: str = "NIS2 Field Audit Tool"
    version: str = "1.0.0"
    
    # Database
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # Logging
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Security
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Export
    export: ExportConfig = field(default_factory=ExportConfig)
    
    # TUI settings
    theme: str = "amber"  # amber, green, modern
    auto_save_interval: int = 30  # seconds
    max_displayed_devices: int = 100
    idle_timeout: int = 1800  # seconds (30 minutes) - auto-lock after inactivity
    
    # Network scanning
    nmap_timeout: int = 60
    ssh_timeout: int = 30
    concurrent_scans: int = 10
    
    auto_advance: bool = False
    require_notes_for_non_compliant: bool = True
    
    # Performance
    max_memory_cache_mb: int = 100
    
    # SECURITY: Secrets are NOT stored here - use SecretsManager instead
    # All secrets are retrieved via SecretsManager.get_secret(name)


def is_portable_mode() -> bool:
    """Check if the app is running in portable mode."""
    # Check if we are running from a 'python' subdirectory in the app root
    # or if a '.portable' marker file exists.
    try:
        app_root = Path(sys.executable).parent.parent
        return (app_root / "python").exists() or (app_root / ".portable").exists()
    except Exception:
        return False


def get_portable_data_directory() -> Path:
    """Get the data directory for portable mode."""
    app_root = Path(sys.executable).parent.parent
    data_dir = app_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_config_directory() -> Path:
    """Get the platform-appropriate config directory."""
    if is_portable_mode():
        config_dir = get_portable_data_directory() / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    if os.name == 'nt':  # Windows
        base_dir = Path(os.environ.get('APPDATA') or Path.home() / 'AppData/Roaming')
    elif sys.platform == 'darwin':  # macOS
        base_dir = Path.home() / 'Library/Application Support'
    else:  # Linux and others
        base_dir = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config')
    
    config_dir = base_dir / 'nis2-audit'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_data_directory() -> Path:
    """Get the platform-appropriate data directory."""
    if is_portable_mode():
        return get_portable_data_directory()

    if os.name == 'nt':  # Windows
        base_dir = Path(os.environ.get('LOCALAPPDATA') or Path.home() / 'AppData/Local')
    elif sys.platform == 'darwin':  # macOS
        base_dir = Path.home() / 'Library/Application Support'
    else:  # Linux and others
        base_dir = Path(os.environ.get('XDG_DATA_HOME') or Path.home() / '.local/share')
    
    data_dir = base_dir / 'nis2-audit'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_default_config_path() -> Path:
    """Get the default configuration file path."""
    return get_config_directory() / 'config.json'


class ConfigurationManager:
    """
    Manages application configuration.
    
    Configuration priority (highest to lowest):
    1. Environment variables (NIS2_*)
    2. User config file (~/.config/nis2-audit/config.json)
    3. Platform defaults
    """
    
    _instance: Optional['ConfigurationManager'] = None
    _config: AppConfig
    _config_path: Path
    
    def __new__(cls, config_path: Optional[Path] = None) -> 'ConfigurationManager':
        """
        Create or return the singleton ConfigurationManager instance.
        
        Args:
            config_path: Optional path to configuration file
            
        Returns:
            ConfigurationManager singleton instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = AppConfig()
            cls._instance._config_path = config_path or get_default_config_path()
            cls._instance._load()
        return cls._instance
    
    def _load(self) -> None:
        """Load configuration from file and environment."""
        self._config = AppConfig()
        
        if self._config_path.exists():
            try:
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._merge_config(data)
                logger.debug(f"Loaded config from {self._config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        # Apply environment variable overrides
        self._apply_env_overrides()
        
        # Set default paths if not specified
        self._set_default_paths()
    
    def _merge_config(self, data: Dict[str, Any]) -> None:
        """Merge configuration data into current config."""
        # Database
        if 'database' in data:
            db_data = data['database']
            if 'path' in db_data:
                self._config.database.path = db_data['path']
            if 'backup_on_startup' in db_data:
                self._config.database.backup_on_startup = db_data['backup_on_startup']
            if 'integrity_check_on_startup' in db_data:
                self._config.database.integrity_check_on_startup = db_data['integrity_check_on_startup']
        
        # Logging
        if 'logging' in data:
            log_data = data['logging']
            if 'level' in log_data:
                self._config.logging.level = log_data['level']
            if 'directory' in log_data:
                self._config.logging.directory = log_data['directory']
            if 'json_format' in log_data:
                self._config.logging.json_format = log_data['json_format']
        
        # Security
        if 'security' in data:
            sec_data = data['security']
            if 'max_scan_timeout' in sec_data:
                self._config.security.max_scan_timeout = sec_data['max_scan_timeout']
        
        # Export
        if 'export' in data:
            exp_data = data['export']
            if 'default_format' in exp_data:
                self._config.export.default_format = exp_data['default_format']
        
        # TUI
        if 'theme' in data:
            self._config.theme = data['theme']
        if 'auto_save_interval' in data:
            self._config.auto_save_interval = data['auto_save_interval']
        
        # Network
        if 'nmap_timeout' in data:
            self._config.nmap_timeout = data['nmap_timeout']
        if 'concurrent_scans' in data:
            self._config.concurrent_scans = data['concurrent_scans']
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        env_mappings = {
            'NIS2_DB_PATH': ('database', 'path'),
            'NIS2_LOG_LEVEL': ('logging', 'level'),
            'NIS2_LOG_DIR': ('logging', 'directory'),
            'NIS2_THEME': ('theme', None),
            'NIS2_NMAP_TIMEOUT': ('nmap_timeout', None),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                if section == 'database' and key == 'path':
                    self._config.database.path = value
                elif section == 'logging':
                    if key == 'level':
                        self._config.logging.level = value
                    elif key == 'directory':
                        self._config.logging.directory = value
                elif section == 'theme':
                    self._config.theme = value
                elif section == 'nmap_timeout':
                    try:
                        self._config.nmap_timeout = int(value)
                    except ValueError:
                        logger.warning(f"Invalid NIS2_NMAP_TIMEOUT value: {value}")
    
    def _set_default_paths(self) -> None:
        """Set default paths if not specified."""
        data_dir = get_data_directory()
        
        if self._config.database.path is None:
            self._config.database.path = str(data_dir / 'audit_sessions.db')
        
        if self._config.logging.directory is None:
            self._config.logging.directory = str(data_dir / 'logs')
        
        if self._config.export.output_directory is None:
            self._config.export.output_directory = str(data_dir / 'exports')
    
    def get(self) -> AppConfig:
        """Get current configuration."""
        return deepcopy(self._config)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update configuration values."""
        self._merge_config(updates)
        self.save()
    
    def save(self) -> None:
        """Save current configuration to file."""
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            # Pass 10: Use atomic write to prevent corruption
            with atomic_write(self._config_path, mode='w', encoding='utf-8') as f:
                json.dump(asdict(self._config), f, indent=2)
            # Pass 15: Set secure permissions
            secure_file_permissions(self._config_path, 0o600)
            logger.debug(f"Saved config to {self._config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self._config = AppConfig()
        self._set_default_paths()
        self.save()


# Convenience functions
def get_config() -> AppConfig:
    """Get the current configuration."""
    return ConfigurationManager().get()


def update_config(updates: Dict[str, Any]) -> None:
    """Update configuration values."""
    ConfigurationManager().update(updates)


def get_db_path() -> str:
    """Get the configured database path."""
    return get_config().database.path


def get_log_dir() -> str:
    """Get the configured log directory."""
    return get_config().logging.directory


# Create a sample configuration file
def create_sample_config(path: Optional[Path] = None) -> Path:
    """Create a sample configuration file."""
    if path is None:
        path = get_config_directory() / 'config.json.example'
    
    sample = {
        "app_name": "NIS2 Field Audit Tool",
        "theme": "amber",
        "auto_save_interval": 30,
        "database": {
            "backup_on_startup": True,
            "integrity_check_on_startup": True,
            "wal_mode": True
        },
        "logging": {
            "level": "INFO",
            "json_format": False,
            "console": True,
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "security": {
            "require_encryption": True,
            "max_scan_timeout": 300,
            "block_dangerous_commands": True
        },
        "export": {
            "default_format": "docx",
            "include_evidence": True,
            "watermark_text": "CONFIDENTIAL"
        },
        "nmap_timeout": 60,
        "concurrent_scans": 10
    }
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with atomic_write(path, mode='w', encoding='utf-8') as f:
        json.dump(sample, f, indent=2)
    secure_file_permissions(path, 0o600)
    
    return path
