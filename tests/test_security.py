"""
Tests for security utilities (Passes 33-45).

This file tests the 2026 CVE-based security passes:
- Pass 33: JWT Authentication Bypass Prevention
- Pass 34: SQL Injection Prevention
- Pass 35: Advanced XXE Prevention
- Pass 36: Secure File Upload
- Pass 37: Open Redirect Prevention
- Pass 38: Secure Deserialization
- Pass 39: Session Fixation Prevention
- Pass 40: Clickjacking Prevention
- Pass 41: LDAP Injection Prevention
- Pass 42: NoSQL Injection Prevention
- Pass 43: HTTP Header Injection Prevention
- Pass 44: Information Disclosure Prevention
- Pass 45: Secure Configuration Management
"""
import pytest
import json
import os
import tempfile
from pathlib import Path
from io import BytesIO

# Import security utilities
from app.security_utils import (
    # Pass 33: JWT
    validate_jwt_algorithm,
    validate_jwt_header,
    sanitize_jwt_token,
    JWTValidationError,
    FORBIDDEN_JWT_ALGORITHMS,
    ALLOWED_JWT_ALGORITHMS,
    
    # Pass 34: SQL
    validate_sql_column_alias,
    validate_sql_order_by,
    SQLInjectionError,
    
    # Pass 35: XXE
    parse_xml_securely,
    XXEError,
    
    # Pass 36: File Upload
    validate_file_extension,
    validate_file_content_type,
    sanitize_upload_filename,
    validate_upload_path,
    FileUploadError,
    DANGEROUS_EXTENSIONS,
    
    # Pass 37: Open Redirect
    validate_redirect_url,
    add_allowed_redirect_domain,
    OpenRedirectError,
    
    # Pass 38: Deserialization
    validate_pickle_data,
    safe_json_deserialize,
    DeserializationError,
    
    # Pass 39: Session
    generate_secure_session_id,
    regenerate_session_id,
    get_secure_cookie_flags,
    
    # Pass 40: Clickjacking
    get_clickjacking_protection_headers,
    validate_frame_options_header,
    
    # Pass 41: LDAP
    escape_ldap_filter_value,
    escape_ldap_dn_value,
    validate_ldap_filter,
    LDAPInjectionError,
    
    # Pass 42: NoSQL
    sanitize_mongodb_query,
    validate_mongodb_field_name,
    sanitize_redis_command,
    NoSQLInjectionError,
    
    # Pass 43: HTTP Headers
    sanitize_http_header_name,
    sanitize_http_header_value,
    HeaderInjectionError,
    
    # Pass 44: Info Disclosure
    sanitize_error_message,
    mask_sensitive_data,
    
    # Pass 45: Configuration
    validate_config_file_permissions,
    set_secure_file_permissions,
    validate_config_schema,
    ConfigurationSecurityError,
    SECURE_FILE_PERMISSIONS,
)


# =============================================================================
# Pass 33: JWT Authentication Bypass Prevention
# =============================================================================

class TestJWTValidation:
    """Test JWT authentication bypass prevention (CVE-2026-29000, CVE-2026-28802)."""
    
    def test_validate_jwt_algorithm_none_rejected(self):
        """Reject alg:none algorithm."""
        with pytest.raises(JWTValidationError, match="forbidden"):
            validate_jwt_algorithm('none')
        with pytest.raises(JWTValidationError, match="forbidden"):
            validate_jwt_algorithm('None')
        with pytest.raises(JWTValidationError, match="forbidden"):
            validate_jwt_algorithm('NONE')
    
    def test_validate_jwt_algorithm_empty_rejected(self):
        """Reject empty algorithm."""
        with pytest.raises(JWTValidationError):
            validate_jwt_algorithm('')
    
    def test_validate_jwt_algorithm_allowed(self):
        """Accept allowed algorithms."""
        for alg in ['HS256', 'RS256', 'ES256', 'EdDSA']:
            validate_jwt_algorithm(alg)  # Should not raise
    
    def test_validate_jwt_algorithm_unknown_rejected(self):
        """Reject unknown algorithms."""
        with pytest.raises(JWTValidationError):
            validate_jwt_algorithm('UNKNOWN')
    
    def test_validate_jwt_header_jwk_rejected(self):
        """Reject JWK in header (key confusion prevention)."""
        with pytest.raises(JWTValidationError, match="JWK"):
            validate_jwt_header({'alg': 'HS256', 'jwk': {'k': 'value'}})
    
    def test_sanitize_jwt_token_valid(self):
        """Sanitize valid JWT token."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        result = sanitize_jwt_token(token)
        assert result == token
    
    def test_sanitize_jwt_token_invalid_format(self):
        """Reject invalid JWT format."""
        # 5 parts should be rejected
        with pytest.raises(JWTValidationError):
            sanitize_jwt_token("not.a.valid.jwt.extra")
        # 1 part should be rejected
        with pytest.raises(JWTValidationError):
            sanitize_jwt_token("onlyonepart")
    
    def test_sanitize_jwt_token_suspicious_chars(self):
        """Reject JWT with suspicious characters."""
        with pytest.raises(JWTValidationError):
            sanitize_jwt_token("eyJhbGc<script>alert(1)</script>iOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.signature")


# =============================================================================
# Pass 34: SQL Injection Prevention
# =============================================================================

class TestSQLInjectionPrevention:
    """Test SQL injection prevention (CVE-2026-1312, CVE-2026-3057)."""
    
    def test_validate_sql_column_alias_valid(self):
        """Accept valid column aliases."""
        validate_sql_column_alias("username")  # Should not raise
        validate_sql_column_alias("user_name")  # Should not raise
        validate_sql_column_alias("col123")  # Should not raise
    
    def test_validate_sql_column_alias_dangerous_chars(self):
        """Reject aliases with dangerous characters."""
        with pytest.raises(SQLInjectionError):
            validate_sql_column_alias("name'; DROP TABLE users;--")
        with pytest.raises(SQLInjectionError):
            validate_sql_column_alias('name"')
    
    def test_validate_sql_column_alias_sql_keywords(self):
        """Reject aliases with SQL keywords."""
        with pytest.raises(SQLInjectionError):
            validate_sql_column_alias("col UNION SELECT")
    
    def test_validate_sql_order_by_valid(self):
        """Accept valid ORDER BY fields."""
        validate_sql_order_by("username")
        validate_sql_order_by("-created_at")  # Descending
    
    def test_validate_sql_order_by_allowlist(self):
        """Enforce allowlist for ORDER BY fields."""
        allowed = {"username", "email", "created_at"}
        validate_sql_order_by("username", allowed)
        
        with pytest.raises(SQLInjectionError):
            validate_sql_order_by("password", allowed)
    
    def test_validate_sql_order_by_cve_2026_1312_pattern(self):
        """Detect CVE-2026-1312 column alias pattern."""
        # Column aliases with periods + FilteredRelation
        with pytest.raises(SQLInjectionError):
            validate_sql_order_by("col..name")


# =============================================================================
# Pass 35: Advanced XXE Prevention
# =============================================================================

class TestXXEPrevention:
    """Test XXE prevention (CVE-2026-24400, CVE-2026-1227)."""
    
    def test_parse_xml_securely_valid(self):
        """Parse valid XML."""
        xml = "<root><item>value</item></root>"
        result = parse_xml_securely(xml)
        assert result.tag == "root"
    
    def test_parse_xml_securely_doctype_rejected(self):
        """Reject XML with DOCTYPE."""
        xml = """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>"""
        with pytest.raises(XXEError, match="DOCTYPE"):
            parse_xml_securely(xml)
    
    def test_parse_xml_securely_external_entity_rejected(self):
        """Reject XML with external entities."""
        xml = """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY xxe SYSTEM "http://attacker.com/evil">
]>
<root>&xxe;</root>"""
        # Should be rejected by DOCTYPE check first
        with pytest.raises(XXEError):
            parse_xml_securely(xml)
    
    def test_parse_xml_securely_billion_laughs_rejected(self):
        """Reject XML with too many entity declarations."""
        # This should be caught by DOCTYPE check first
        xml = "<!DOCTYPE root [" + "<!ENTITY e" * 150 + ">]><root/>"
        with pytest.raises(XXEError):
            parse_xml_securely(xml)
    
    def test_parse_xml_securely_xinclude_rejected(self):
        """Reject XML with XInclude."""
        xml = """<root xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include href="/etc/passwd"/>
</root>"""
        with pytest.raises(XXEError, match="XInclude"):
            parse_xml_securely(xml)


# =============================================================================
# Pass 36: Secure File Upload
# =============================================================================

class TestSecureFileUpload:
    """Test secure file upload (CVE-2026-25737, CVE-2026-24486)."""
    
    def test_validate_file_extension_valid(self):
        """Accept valid file extensions."""
        validate_file_extension("document.pdf", {".pdf", ".doc"})
        validate_file_extension("image.png", {".png", ".jpg"})
    
    def test_validate_file_extension_dangerous(self):
        """Reject dangerous extensions."""
        for ext in ['.exe', '.php', '.py', '.sh']:
            with pytest.raises(FileUploadError):
                validate_file_extension(f"file{ext}")
    
    def test_validate_file_extension_not_allowed(self):
        """Reject extensions not in allowlist."""
        with pytest.raises(FileUploadError):
            validate_file_extension("file.exe", {".pdf", ".doc"})
    
    def test_validate_file_content_type_jpeg(self):
        """Detect JPEG from magic bytes."""
        content = b'\xff\xd8\xff' + b'\x00' * 100
        mime = validate_file_content_type(content)
        assert mime == "image/jpeg"
    
    def test_validate_file_content_type_png(self):
        """Detect PNG from magic bytes."""
        content = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        mime = validate_file_content_type(content)
        assert mime == "image/png"
    
    def test_sanitize_upload_filename_traversal(self):
        """Reject filenames with path traversal."""
        with pytest.raises(FileUploadError):
            sanitize_upload_filename("../../../etc/passwd")
        with pytest.raises(FileUploadError):
            sanitize_upload_filename("file\x00name.txt")
    
    def test_sanitize_upload_filename_valid(self):
        """Sanitize valid filenames."""
        result = sanitize_upload_filename("document.pdf")
        assert result.endswith(".pdf")
        assert ".." not in result
    
    def test_validate_upload_path_traversal(self):
        """Reject upload paths that escape base directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(FileUploadError):
                validate_upload_path("../../../etc/passwd", tmpdir)
    
    def test_validate_upload_path_valid(self):
        """Accept valid upload paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = validate_upload_path("subdir/file.txt", tmpdir)
            assert str(result).startswith(tmpdir)


# =============================================================================
# Pass 37: Open Redirect Prevention
# =============================================================================

class TestOpenRedirectPrevention:
    """Test open redirect prevention (CVE-2026-2709, CVE-2026-25477)."""
    
    def test_validate_redirect_url_relative(self):
        """Accept relative URLs."""
        result = validate_redirect_url("/dashboard")
        assert result == "/dashboard"
    
    def test_validate_redirect_url_data_uri_rejected(self):
        """Reject data: URIs."""
        with pytest.raises(OpenRedirectError, match="Data URIs"):
            validate_redirect_url("data:text/html,<script>alert(1)</script>")
    
    def test_validate_redirect_url_javascript_rejected(self):
        """Reject javascript: URIs."""
        with pytest.raises(OpenRedirectError, match="JavaScript URIs"):
            validate_redirect_url("javascript:alert(1)")
    
    def test_validate_redirect_url_authority_injection(self):
        """Reject URL authority injection (@ bypass)."""
        # CVE-2026-27191 pattern: @attacker.com after legitimate domain
        # When a domain-like string is used as username before @, it's suspicious
        with pytest.raises(OpenRedirectError, match="authority injection"):
            validate_redirect_url("https://trusted.com@evil.com/path")
        # Other patterns with domain-like usernames
        with pytest.raises(OpenRedirectError, match="authority injection"):
            validate_redirect_url("https://legitimate.site@attacker.com")
    
    def test_validate_redirect_url_domain_allowlist(self):
        """Enforce domain allowlist."""
        add_allowed_redirect_domain("trusted.com")
        validate_redirect_url("https://trusted.com/path")
        
        with pytest.raises(OpenRedirectError):
            validate_redirect_url("https://evil.com/path")
    
    def test_validate_redirect_url_cve_2026_25477_pattern(self):
        """Detect CVE-2026-25477 regex suffix bypass."""
        add_allowed_redirect_domain("trusted.com")
        # Suffix match should NOT work
        with pytest.raises(OpenRedirectError):
            validate_redirect_url("https://evil-trusted.com/path")


# =============================================================================
# Pass 38: Secure Deserialization
# =============================================================================

class TestSecureDeserialization:
    """Test secure deserialization (CVE-2026-21226, CVE-2026-23946)."""
    
    def test_validate_pickle_data_empty(self):
        """Reject empty pickle data."""
        with pytest.raises(DeserializationError):
            validate_pickle_data(b"")
    
    def test_validate_pickle_data_dangerous_types(self):
        """Reject pickle with dangerous types."""
        # Simulate pickle data with dangerous reference
        data = b"cos\nsystem\np0\n."
        # Should be rejected (either by format check or dangerous type check)
        with pytest.raises(DeserializationError):
            validate_pickle_data(data)
    
    def test_safe_json_deserialize_valid(self):
        """Parse valid JSON."""
        data = '{"name": "test", "value": 123}'
        result = safe_json_deserialize(data)
        assert result["name"] == "test"
        assert result["value"] == 123
    
    def test_safe_json_deserialize_prototype_pollution(self):
        """Reject prototype pollution attempts."""
        data = '{"__proto__": {"evil": true}}'
        with pytest.raises(DeserializationError):
            safe_json_deserialize(data)
    
    def test_safe_json_deserialize_dangerous_keys(self):
        """Reject dangerous keys."""
        data = '{"constructor.prototype.evil": true}'
        with pytest.raises(DeserializationError):
            safe_json_deserialize(data)


# =============================================================================
# Pass 39: Session Fixation Prevention
# =============================================================================

class TestSessionFixationPrevention:
    """Test session fixation prevention (CVE-2026-23796)."""
    
    def test_generate_secure_session_id(self):
        """Generate secure session ID."""
        session_id = generate_secure_session_id()
        assert len(session_id) >= 32
        assert session_id != generate_secure_session_id()  # Should be unique
    
    def test_regenerate_session_id_changes(self):
        """Session ID changes after regeneration."""
        old_id = "old_session_123"
        new_id = regenerate_session_id(old_id, "user_123")
        assert new_id != old_id
        assert len(new_id) >= 32
    
    def test_get_secure_cookie_flags(self):
        """Get secure cookie flags."""
        flags = get_secure_cookie_flags()
        assert flags["httponly"] is True
        assert flags["secure"] is True
        assert flags["samesite"] == "Strict"


# =============================================================================
# Pass 40: Clickjacking Prevention
# =============================================================================

class TestClickjackingPrevention:
    """Test clickjacking prevention (CVE-2026-24839, CVE-2026-23731)."""
    
    def test_get_clickjacking_protection_headers_deny(self):
        """Get headers to deny all framing."""
        headers = get_clickjacking_protection_headers(deny_all=True)
        assert headers["X-Frame-Options"] == "DENY"
        assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    
    def test_get_clickjacking_protection_headers_sameorigin(self):
        """Get headers for same-origin framing."""
        headers = get_clickjacking_protection_headers(deny_all=False)
        assert headers["X-Frame-Options"] == "SAMEORIGIN"
        assert "frame-ancestors 'self'" in headers["Content-Security-Policy"]
    
    def test_validate_frame_options_header_valid(self):
        """Validate valid X-Frame-Options values."""
        assert validate_frame_options_header("DENY") is True
        assert validate_frame_options_header("SAMEORIGIN") is True
        assert validate_frame_options_header("ALLOW-FROM https://example.com") is True
    
    def test_validate_frame_options_header_invalid(self):
        """Reject invalid X-Frame-Options values."""
        assert validate_frame_options_header("INVALID") is False


# =============================================================================
# Pass 41: LDAP Injection Prevention
# =============================================================================

class TestLDAPInjectionPrevention:
    """Test LDAP injection prevention (CVE-2026-24130, CVE-2026-21880)."""
    
    def test_escape_ldap_filter_value_valid(self):
        """Escape valid LDAP filter values."""
        result = escape_ldap_filter_value("username")
        assert result == "username"
    
    def test_escape_ldap_filter_value_special_chars(self):
        """Escape special LDAP filter characters."""
        result = escape_ldap_filter_value("user*name")
        assert "\\2a" in result  # * is escaped
        
        result = escape_ldap_filter_value("user(name)")
        assert "\\28" in result  # ( is escaped
        assert "\\29" in result  # ) is escaped
    
    def test_escape_ldap_filter_value_type_check(self):
        """Reject non-string values (CVE-2025-61911)."""
        with pytest.raises(LDAPInjectionError):
            escape_ldap_filter_value(["list"])
        with pytest.raises(LDAPInjectionError):
            escape_ldap_filter_value({"dict": "value"})
    
    def test_escape_ldap_dn_value(self):
        """Escape LDAP DN values."""
        result = escape_ldap_dn_value("cn=user,dc=example,dc=com")
        assert "\\2c" in result  # , is escaped
    
    def test_validate_ldap_filter_unbalanced(self):
        """Reject unbalanced parentheses."""
        with pytest.raises(LDAPInjectionError, match="Unbalanced"):
            validate_ldap_filter("(cn=user")
    
    def test_validate_ldap_filter_injection(self):
        """Reject LDAP injection patterns."""
        with pytest.raises(LDAPInjectionError, match="injection"):
            validate_ldap_filter("(cn=user*)")


# =============================================================================
# Pass 42: NoSQL Injection Prevention
# =============================================================================

class TestNoSQLInjectionPrevention:
    """Test NoSQL injection prevention."""
    
    def test_sanitize_mongodb_query_valid(self):
        """Sanitize valid MongoDB query."""
        query = {"username": "test", "active": True}
        result = sanitize_mongodb_query(query)
        assert result["username"] == "test"
    
    def test_sanitize_mongodb_query_js_operator(self):
        """Reject JavaScript operators."""
        with pytest.raises(NoSQLInjectionError, match="JavaScript"):
            sanitize_mongodb_query({"$where": "this.value > 0"})
    
    def test_sanitize_mongodb_query_nested_js(self):
        """Reject nested JavaScript operators."""
        with pytest.raises(NoSQLInjectionError, match="JavaScript"):
            sanitize_mongodb_query({"field": {"$where": "evil"}})
    
    def test_validate_mongodb_field_name_valid(self):
        """Accept valid field names."""
        validate_mongodb_field_name("username")
        validate_mongodb_field_name("user_name")
    
    def test_validate_mongodb_field_name_operator(self):
        """Reject field names starting with $."""
        with pytest.raises(NoSQLInjectionError, match="cannot start"):
            validate_mongodb_field_name("$where")
    
    def test_sanitize_redis_command_valid(self):
        """Sanitize valid Redis command."""
        result = sanitize_redis_command(["GET", "key"])
        assert result == ["GET", "key"]
    
    def test_sanitize_redis_command_dangerous(self):
        """Reject dangerous Redis commands."""
        with pytest.raises(NoSQLInjectionError, match="CONFIG"):
            sanitize_redis_command(["CONFIG", "GET", "*"])
        with pytest.raises(NoSQLInjectionError, match="FLUSHALL"):
            sanitize_redis_command(["FLUSHALL"])


# =============================================================================
# Pass 43: HTTP Header Injection Prevention
# =============================================================================

class TestHTTPHeaderInjectionPrevention:
    """Test HTTP header injection prevention (CVE-2026-24489, CVE-2026-0865)."""
    
    def test_sanitize_http_header_name_valid(self):
        """Accept valid header names."""
        result = sanitize_http_header_name("Content-Type")
        assert result == "Content-Type"
    
    def test_sanitize_http_header_name_forbidden_chars(self):
        """Reject header names with forbidden characters."""
        with pytest.raises(HeaderInjectionError):
            sanitize_http_header_name("X-Header\r\nEvil")
        with pytest.raises(HeaderInjectionError):
            sanitize_http_header_name("X-Header\x00")
    
    def test_sanitize_http_header_value_crlf(self):
        """Reject header values with CRLF."""
        with pytest.raises(HeaderInjectionError, match="forbidden"):
            sanitize_http_header_value("value\r\nX-Injection: evil")
        with pytest.raises(HeaderInjectionError, match="forbidden"):
            sanitize_http_header_value("value\n")
        with pytest.raises(HeaderInjectionError, match="forbidden"):
            sanitize_http_header_value("value\x00")
    
    def test_sanitize_http_header_value_valid(self):
        """Accept valid header values."""
        result = sanitize_http_header_value("application/json")
        assert result == "application/json"


# =============================================================================
# Pass 44: Information Disclosure Prevention
# =============================================================================

class TestInformationDisclosurePrevention:
    """Test information disclosure prevention (CVE-2026-2861, CVE-2026-21626)."""
    
    def test_sanitize_error_message_removes_stacktrace(self):
        """Remove stack traces from error messages."""
        error = """Something went wrong
  File "/app/server.py", line 42
    return process(data)
           ^
Error: Invalid input"""
        result = sanitize_error_message(error, is_production=True)
        assert "File \"/app/server.py\"" not in result
        assert "Something went wrong" in result
    
    def test_sanitize_error_message_masks_passwords(self):
        """Mask passwords in error messages."""
        error = "Login failed for user=admin password=secret123"
        result = sanitize_error_message(error, is_production=True)
        assert "secret123" not in result
        assert "***REDACTED***" in result
    
    def test_mask_sensitive_data_password(self):
        """Mask password in text."""
        text = "The password is: superSecret123!"
        result = mask_sensitive_data(text)
        assert "superSecret123" not in result
    
    def test_mask_sensitive_data_credit_card(self):
        """Mask credit card numbers."""
        text = "Card: 1234-5678-9012-3456"
        result = mask_sensitive_data(text)
        assert "3456" not in result
        assert "****" in result


# =============================================================================
# Pass 45: Secure Configuration Management
# =============================================================================

class TestSecureConfigurationManagement:
    """Test secure configuration management."""
    
    def test_validate_config_file_permissions_world_readable(self):
        """Reject world-readable config files."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"secret=value")
            path = f.name
        
        try:
            # Make world-readable
            os.chmod(path, 0o644)
            
            with pytest.raises(ConfigurationSecurityError, match="world-readable"):
                validate_config_file_permissions(path)
        finally:
            os.unlink(path)
    
    def test_validate_config_file_permissions_world_writable(self):
        """Reject world-writable config files."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"secret=value")
            path = f.name
        
        try:
            # Make world-writable but not world-readable (0o622)
            os.chmod(path, 0o622)
            
            with pytest.raises(ConfigurationSecurityError, match="world-writable"):
                validate_config_file_permissions(path)
        finally:
            os.unlink(path)
    
    def test_set_secure_file_permissions(self):
        """Set secure file permissions."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"secret=value")
            path = f.name
        
        try:
            set_secure_file_permissions(path)
            mode = os.stat(path).st_mode
            # Should be 0o600 (owner read/write only)
            assert (mode & 0o777) == 0o600
        finally:
            os.unlink(path)
    
    def test_validate_config_schema_missing_key(self):
        """Reject config with missing required key."""
        config = {"host": "localhost"}
        schema = {"host": "path", "port": "port"}
        
        with pytest.raises(ConfigurationSecurityError, match="missing"):
            validate_config_schema(config, schema)
    
    def test_validate_config_schema_invalid_port(self):
        """Reject config with invalid port."""
        config = {"port": "not_a_port"}
        schema = {"port": "port"}
        
        with pytest.raises(ConfigurationSecurityError, match="port"):
            validate_config_schema(config, schema)
    
    def test_validate_config_schema_secret_too_short(self):
        """Reject secret that is too short."""
        config = {"api_key": "short"}
        schema = {"api_key": "secret"}
        
        with pytest.raises(ConfigurationSecurityError, match="too short"):
            validate_config_schema(config, schema)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
