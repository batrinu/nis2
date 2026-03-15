"""
Secure secrets management for the NIS2 Field Audit Tool.

Uses the system keyring for secure credential storage with fallback
to environment variables for containerized deployments.
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    Secure secrets storage using system keyring.
    
    SECURITY: This class provides a centralized way to store and retrieve
    sensitive information like API keys, passwords, and tokens. Secrets are
    stored in the OS keyring (Keychain on macOS, Credential Manager on Windows,
    Secret Service on Linux) which provides hardware-backed encryption where
    available.
    
    For environments without a keyring (containers, CI/CD), falls back to
    environment variables with appropriate warnings.
    """
    
    SERVICE_NAME = "nis2-field-audit"
    ENV_PREFIX = "NIS2_SECRET_"
    
    _keyring_available: Optional[bool] = None
    _keyring_module = None
    
    @classmethod
    def _check_keyring(cls) -> bool:
        """Check if keyring is available."""
        if cls._keyring_available is not None:
            return cls._keyring_available
        
        try:
            import keyring
            cls._keyring_module = keyring
            # Test if keyring is actually functional
            cls._keyring_available = keyring.get_keyring().is_available()
            if cls._keyring_available:
                logger.debug("Keyring is available and functional")
            else:
                logger.warning("Keyring module installed but not functional")
        except ImportError:
            cls._keyring_available = False
            logger.warning("Keyring module not installed. Secrets will use environment variables only.")
        
        return cls._keyring_available
    
    @classmethod
    def get_secret(cls, name: str) -> Optional[str]:
        """
        Retrieve a secret by name.
        
        Resolution order:
        1. System keyring (most secure)
        2. Environment variable (for containers/CI)
        3. None (not found)
        
        Args:
            name: Secret name/key
            
        Returns:
            Secret value or None if not found
        """
        if not name:
            return None
        
        # Normalize name
        name = name.lower().strip()
        
        # Try keyring first (most secure)
        if cls._check_keyring():
            try:
                value = cls._keyring_module.get_password(cls.SERVICE_NAME, name)
                if value is not None:
                    logger.debug(f"Retrieved secret '{name}' from keyring")
                    return value
            except Exception as e:
                logger.warning(f"Failed to retrieve secret from keyring: {e}")
        
        # Fall back to environment variable
        env_var_name = f"{cls.ENV_PREFIX}{name.upper()}"
        env_value = os.environ.get(env_var_name)
        if env_value is not None:
            logger.debug(f"Retrieved secret '{name}' from environment variable {env_var_name}")
            return env_value
        
        # Also try without prefix for common secrets
        env_value = os.environ.get(name.upper())
        if env_value is not None:
            logger.debug(f"Retrieved secret '{name}' from environment variable {name.upper()}")
            return env_value
        
        return None
    
    @classmethod
    def set_secret(cls, name: str, value: str) -> bool:
        """
        Store a secret securely.
        
        Args:
            name: Secret name/key
            value: Secret value
            
        Returns:
            True if stored successfully, False otherwise
        """
        if not name or not value:
            return False
        
        name = name.lower().strip()
        
        if cls._check_keyring():
            try:
                cls._keyring_module.set_password(cls.SERVICE_NAME, name, value)
                logger.info(f"Stored secret '{name}' in keyring")
                return True
            except Exception as e:
                logger.error(f"Failed to store secret in keyring: {e}")
                return False
        else:
            logger.warning(
                f"Cannot store secret '{name}': keyring not available. "
                f"Set environment variable {cls.ENV_PREFIX}{name.upper()} instead."
            )
            return False
    
    @classmethod
    def delete_secret(cls, name: str) -> bool:
        """
        Delete a secret from storage.
        
        Args:
            name: Secret name/key
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if not name:
            return False
        
        name = name.lower().strip()
        success = False
        
        # Delete from keyring
        if cls._check_keyring():
            try:
                cls._keyring_module.delete_password(cls.SERVICE_NAME, name)
                logger.info(f"Deleted secret '{name}' from keyring")
                success = True
            except Exception as e:
                logger.warning(f"Failed to delete secret from keyring: {e}")
        
        # Note: We don't delete environment variables as they're session-only
        
        return success
    
    @classmethod
    def list_secrets(cls) -> list[str]:
        """
        List available secret names (keyring only).
        
        Returns:
            List of secret names
        """
        if not cls._check_keyring():
            return []
        
        try:
            # keyring doesn't provide a direct list method
            # This is a best-effort approach
            return []
        except Exception as e:
            logger.warning(f"Failed to list secrets: {e}")
            return []
    
    @classmethod
    def migrate_to_keyring(cls, name: str) -> bool:
        """
        Migrate a secret from environment variable to keyring.
        
        Args:
            name: Secret name to migrate
            
        Returns:
            True if migrated successfully
        """
        env_var_name = f"{cls.ENV_PREFIX}{name.upper()}"
        env_value = os.environ.get(env_var_name)
        
        if env_value is None:
            logger.warning(f"No environment variable {env_var_name} found to migrate")
            return False
        
        if cls.set_secret(name, env_value):
            logger.info(
                f"Migrated secret '{name}' from environment to keyring. "
                f"You can now unset {env_var_name}."
            )
            return True
        
        return False


# Convenience functions for common secrets

def get_api_key(provider: str = "default") -> Optional[str]:
    """Get API key for external service."""
    return SecretsManager.get_secret(f"api_key_{provider}")


def get_ssh_key_password(key_name: str = "default") -> Optional[str]:
    """Get password for encrypted SSH key."""
    return SecretsManager.get_secret(f"ssh_key_{key_name}")


def get_database_password() -> Optional[str]:
    """Get database password (if using external DB)."""
    return SecretsManager.get_secret("database_password")


def get_encryption_key() -> Optional[str]:
    """Get master encryption key."""
    return SecretsManager.get_secret("master_encryption_key")
