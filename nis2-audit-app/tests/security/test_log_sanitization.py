"""
Security tests for log sanitization.
Tests that sensitive data is redacted from logs.
"""
import pytest
import logging
from io import StringIO

from app.logging_config import SensitiveDataFilter


class TestLogSanitization:
    """Test log sanitization filter."""
    
    @pytest.fixture
    def logger_with_filter(self):
        """Create a logger with the sensitive data filter."""
        logger = logging.getLogger("test_sensitive")
        logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        logger.handlers = []
        
        # Create handler with filter
        handler = logging.StreamHandler(StringIO())
        handler.addFilter(SensitiveDataFilter())
        logger.addHandler(handler)
        
        return logger, handler
    
    def test_password_redacted(self, logger_with_filter):
        """Test that passwords are redacted from logs."""
        logger, handler = logger_with_filter
        
        # Log a message with password
        logger.info("Connecting with password=secret123")
        
        # Check output
        output = handler.stream.getvalue()
        assert "secret123" not in output
        assert "password=***" in output
    
    def test_api_key_redacted(self, logger_with_filter):
        """Test that API keys are redacted from logs."""
        logger, handler = logger_with_filter
        
        logger.info("Using api_key=AKIAIOSFODNN7EXAMPLE")
        
        output = handler.stream.getvalue()
        assert "AKIAIOSFODNN7EXAMPLE" not in output
        assert "api_key=***" in output
    
    def test_bearer_token_redacted(self, logger_with_filter):
        """Test that bearer tokens are redacted from logs."""
        logger, handler = logger_with_filter
        
        logger.info("Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
        
        output = handler.stream.getvalue()
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in output
        assert "bearer ***" in output.lower()
    
    def test_private_key_redacted(self, logger_with_filter):
        """Test that private key references are redacted."""
        logger, handler = logger_with_filter
        
        logger.info("Loading private_key=/home/user/.ssh/id_rsa")
        
        output = handler.stream.getvalue()
        assert "/home/user/.ssh/id_rsa" not in output
        assert "private_key=***" in output
    
    def test_credential_redacted(self, logger_with_filter):
        """Test that credentials are redacted."""
        logger, handler = logger_with_filter
        
        logger.info("Failed login with credential=admin:password123")
        
        output = handler.stream.getvalue()
        assert "admin:password123" not in output
        assert "credential=***" in output
    
    def test_normal_message_unchanged(self, logger_with_filter):
        """Test that normal messages are not modified."""
        logger, handler = logger_with_filter
        
        normal_message = "User logged in successfully"
        logger.info(normal_message)
        
        output = handler.stream.getvalue()
        assert normal_message in output
    
    def test_case_insensitive_matching(self, logger_with_filter):
        """Test that matching is case-insensitive."""
        logger, handler = logger_with_filter
        
        variations = [
            "PASSWORD=secret",
            "password=secret",
            "Password=secret",
            "Api_Key=secret",
            "API_KEY=secret",
        ]
        
        for msg in variations:
            # Clear the stream
            handler.stream.truncate(0)
            handler.stream.seek(0)
            
            logger.info(msg)
            output = handler.stream.getvalue()
            assert "secret" not in output, f"Failed for: {msg}"


class TestSecretsManager:
    """Test secrets manager (if keyring is available)."""
    
    def test_get_secret_returns_none_for_missing(self):
        """Test that missing secrets return None."""
        from app.secrets import SecretsManager
        
        # Use a random name that shouldn't exist
        result = SecretsManager.get_secret("test_nonexistent_secret_12345")
        assert result is None
    
    def test_environment_variable_fallback(self):
        """Test fallback to environment variables."""
        import os
        from app.secrets import SecretsManager
        
        # Set an environment variable
        os.environ["NIS2_SECRET_TEST_KEY"] = "test_value"
        
        try:
            result = SecretsManager.get_secret("test_key")
            assert result == "test_value"
        finally:
            # Clean up
            del os.environ["NIS2_SECRET_TEST_KEY"]
    
    def test_service_name_constant(self):
        """Test that service name is consistent."""
        from app.secrets import SecretsManager
        
        assert SecretsManager.SERVICE_NAME == "nis2-field-audit"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
