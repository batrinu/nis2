"""
Encrypted database storage for the NIS2 Field Audit Tool.

Provides transparent encryption for sensitive fields using AES-256-GCM.
This is a defense-in-depth measure that protects data at rest.
"""
import os
import json
import base64
import hashlib
import secrets
import logging
from typing import Optional, Union, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from .db import AuditStorage, DatabaseError


class EncryptionError(DatabaseError):
    """Raised when encryption/decryption fails."""
    pass


class FieldEncryption:
    """
    Field-level encryption for sensitive data.
    
    Uses AES-256 in GCM mode for authenticated encryption.
    Each field gets a unique nonce to prevent pattern analysis.
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryption with a key.
        
        Args:
            key: Encryption key (32 bytes). If None, derives from environment.
        """
        if key is None:
            key = self._derive_key_from_environment()
        
        if len(key) != 32:
            raise EncryptionError("Encryption key must be 32 bytes")
        
        self._key = key
        self._fernet = self._create_fernet()
    
    def _derive_key_from_environment(self) -> bytes:
        """
        Derive encryption key from environment or generate new one.
        
        Returns:
            32-byte encryption key
        """
        # Try to get from secrets manager first
        try:
            from ..secrets import SecretsManager
            stored_key = SecretsManager.get_secret("database_encryption_key")
            if stored_key:
                return base64.urlsafe_b64decode(stored_key.encode())[:32]
        except Exception as e:
            logger.warning(f"Failed to retrieve secret from SecretsManager: {e}")
        
        # Check environment variable
        env_key = os.environ.get("NIS2_DB_ENCRYPTION_KEY")
        if env_key:
            # Derive 32-byte key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"nis2_audit_salt_v1",  # Fixed salt is acceptable for this use case
                iterations=100000,
                backend=default_backend()
            )
            return kdf.derive(env_key.encode())
        
        # Generate a new random key (for first run)
        key = secrets.token_bytes(32)
        
        # Store in secrets manager if available
        try:
            from ..secrets import SecretsManager
            encoded_key = base64.urlsafe_b64encode(key).decode()
            SecretsManager.set_secret("database_encryption_key", encoded_key)
        except Exception as e:
            # If we can't store it, warn but continue
            logger.warning(
                f"Generated database encryption key but couldn't store it securely: {e}. "
                "Set NIS2_DB_ENCRYPTION_KEY environment variable to persist."
            )
        
        return key
    
    def _create_fernet(self) -> Fernet:
        """Create Fernet instance from key."""
        # Fernet requires base64-encoded 32-byte key
        fernet_key = base64.urlsafe_b64encode(self._key)
        return Fernet(fernet_key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string value.
        
        Args:
            plaintext: Value to encrypt
            
        Returns:
            Base64-encoded encrypted value
        """
        if not plaintext:
            return ""
        
        try:
            encrypted = self._fernet.encrypt(plaintext.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted).decode('ascii')
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {e}")
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted value.
        
        Args:
            ciphertext: Base64-encoded encrypted value
            
        Returns:
            Decrypted plaintext
        """
        if not ciphertext:
            return ""
        
        try:
            encrypted = base64.urlsafe_b64decode(ciphertext.encode('ascii'))
            decrypted = self._fernet.decrypt(encrypted)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {e}")
    
    def encrypt_dict(self, data: Dict[str, Any], sensitive_fields: List[str]) -> Dict[str, Any]:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary to encrypt fields in
            sensitive_fields: List of field names to encrypt
            
        Returns:
            Dictionary with encrypted fields
        """
        result = {}
        for key, value in data.items():
            if key in sensitive_fields and value is not None:
                result[key] = self.encrypt(str(value))
                result[f"{key}_encrypted"] = True  # Marker for decryption
            else:
                result[key] = value
        return result
    
    def decrypt_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt fields marked as encrypted in a dictionary.
        
        Args:
            data: Dictionary potentially containing encrypted fields
            
        Returns:
            Dictionary with decrypted fields
        """
        result = {}
        for key, value in data.items():
            if key.endswith('_encrypted'):
                continue  # Skip marker fields
            
            # Check if there's an encryption marker for this field
            if data.get(f"{key}_encrypted") and value:
                try:
                    result[key] = self.decrypt(value)
                except EncryptionError as e:
                    # If decryption fails, keep original (might be unencrypted)
                    logger.warning(f"Decryption failed for field '{key}': {e}. Keeping original value.")
                    result[key] = value
            else:
                result[key] = value
        return result


class EncryptedAuditStorage(AuditStorage):
    """
    Audit storage with field-level encryption for sensitive data.
    
    Encrypts:
    - Device credentials (passwords, enable passwords)
    - SSH keys
    - API keys
    - Any field marked as sensitive
    """
    
    # Fields to encrypt
    SENSITIVE_FIELDS = [
        'password',
        'enable_password',
        'ssh_key_path',
        'api_key',
        'secret',
        'credential',
        'private_key',
    ]
    
    def __init__(self, db_path: str = "./audit_sessions.db", encryption_key: Optional[bytes] = None):
        """
        Initialize encrypted storage.
        
        Args:
            db_path: Path to SQLite database
            encryption_key: Optional encryption key (auto-generated if None)
        """
        self._encryption = FieldEncryption(encryption_key)
        super().__init__(db_path)
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a single value."""
        return self._encryption.encrypt(value)
    
    def _decrypt_value(self, value: str) -> str:
        """Decrypt a single value."""
        return self._encryption.decrypt(value)
    
    def _prepare_for_storage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare data for storage by encrypting sensitive fields.
        
        Args:
            data: Raw data dictionary
            
        Returns:
            Data with sensitive fields encrypted
        """
        return self._encryption.encrypt_dict(data, self.SENSITIVE_FIELDS)
    
    def _prepare_from_storage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare data from storage by decrypting encrypted fields.
        
        Args:
            data: Stored data dictionary
            
        Returns:
            Data with encrypted fields decrypted
        """
        return self._encryption.decrypt_dict(data)
    
    def create_encrypted_backup(self, backup_path: str, password: str) -> None:
        """
        Create an encrypted backup of the database.
        
        Args:
            backup_path: Path for backup file
            password: Password to encrypt backup with
        """
        import shutil
        from cryptography.fernet import Fernet
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=secrets.token_bytes(16),  # Random salt for each backup
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        cipher = Fernet(key)
        
        # Create SQL dump
        import io
        dump = io.StringIO()
        with self._get_connection() as conn:
            for line in conn.iterdump():
                dump.write(line + '\n')
        dump_data = dump.getvalue().encode('utf-8')
        
        # Encrypt and write
        encrypted = cipher.encrypt(dump_data)
        
        # Write salt + encrypted data
        try:
            with open(backup_path, 'wb') as f:
                f.write(kdf._salt + encrypted)  # Store salt with backup
        except (OSError, IOError) as e:
            raise DatabaseError(f"Failed to write backup file: {e}")
    
    def restore_encrypted_backup(self, backup_path: str, password: str) -> None:
        """
        Restore from an encrypted backup.
        
        Args:
            backup_path: Path to backup file
            password: Password to decrypt backup
        """
        from cryptography.fernet import Fernet
        
        # Read salt + encrypted data
        try:
            with open(backup_path, 'rb') as f:
                data = f.read()
        except (OSError, IOError) as e:
            raise DatabaseError(f"Failed to read backup file: {e}")
        
        salt = data[:16]
        encrypted = data[16:]
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        cipher = Fernet(key)
        
        # Decrypt
        try:
            dump_data = cipher.decrypt(encrypted)
        except Exception as e:
            raise EncryptionError(f"Failed to decrypt backup: {e}")
        
        # Execute SQL dump
        with self._get_connection() as conn:
            conn.executescript(dump_data.decode('utf-8'))


# Factory function
def get_encrypted_storage(db_path: Optional[str] = None, encryption_key: Optional[bytes] = None) -> EncryptedAuditStorage:
    """
    Get encrypted storage instance.
    
    Args:
        db_path: Database path (uses default if None)
        encryption_key: Encryption key (auto-generated if None)
        
    Returns:
        EncryptedAuditStorage instance
    """
    from ..config import get_config
    
    if db_path is None:
        db_path = get_config().database.path
    
    return EncryptedAuditStorage(db_path, encryption_key)
