"""
Security tests for Passes 46-58 (Application Consolidation Phase)
Based on March 2026 CVE research

Covers:
- Pass 46: Rate Limiting (CVE-2026-25114, CVE-2026-28342, CVE-2026-23848)
- Pass 47: Authentication Flow Hardening (CVE-2026-23906, CVE-2026-28536)
- Pass 48: API Key and Credential Rotation (CVE-2026-21852, CVE-2026-25253)
- Pass 49: CSRF Protection Consolidation (CVE-2026-24885, CVE-2026-1148, CVE-2026-22030)
- Pass 50: WebSocket Origin Validation (CVE-2026-1692)
- Pass 51: CORS Policy Enforcement (CVE-2024-10906, CVE-2026-24435)
- Pass 52: Audit Log Integrity (CVE-2026-3494)
- Pass 53: Configuration Security Validation (CVE-2026-1731, CVE-2025-60262)
- Pass 54: Error Message Sanitization (CVE-2026-26144, CVE-2026-20838)
- Pass 55: Session Timeout Enforcement (CVE-2026-23646)
- Pass 56: File Upload Restriction (CVE-2026-21536)
- Pass 57: Request Origin Validation (CVE-2026-25151, CVE-2026-25221)
- Pass 58: Security Header Consolidation
"""
import pytest
import time
import sys
import os

# Add the app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'nis2-audit-app'))

from app.security_utils import (
    # Pass 46
    RateLimitError, RateLimiter, check_rate_limit, extract_client_ip,
    # Pass 47
    AuthenticationError, validate_ldap_auth_response, validate_auth_attempt,
    # Pass 48
    CredentialRotationError, generate_secure_api_key, validate_api_key_format,
    should_rotate_api_key, mask_api_key,
    # Pass 49
    CSRFError, generate_csrf_token, validate_csrf_token, 
    validate_content_type_for_csrf, validate_origin_header,
    # Pass 50
    WebSocketSecurityError, validate_websocket_origin, get_websocket_security_headers,
    # Pass 51
    CORSError, validate_cors_origin, get_cors_headers, validate_cors_preflight_request,
    # Pass 52
    AuditIntegrityError, create_audit_log_entry, verify_audit_entry, sanitize_audit_user_id,
    # Pass 53
    ConfigValidationError, validate_configuration_security, check_secure_defaults,
    # Pass 54
    ErrorSanitizationError, sanitize_production_error, get_safe_error_response,
    # Pass 55
    SessionTimeoutError, validate_session_timeout, calculate_session_ttl, 
    should_refresh_session, MAX_SESSION_DURATION,
    # Pass 56
    FileUploadRestrictionError, validate_upload_file_extension, 
    validate_upload_file_size, sanitize_uploaded_filename,
    DANGEROUS_FILE_TYPES, SAFE_DOCUMENT_TYPES,
    # Pass 57
    OriginValidationError, validate_request_origin, validate_oauth_state,
    # Pass 58
    get_security_headers, get_content_security_policy, validate_security_headers,
    SECURITY_HEADERS,
)


# =============================================================================
# Pass 46: Rate Limiting Tests
# =============================================================================

class TestRateLimiting:
    """Test rate limiting enforcement (CVE-2026-25114, CVE-2026-28342, CVE-2026-23848)"""
    
    def test_rate_limiter_allows_initial_requests(self):
        """Test rate limiter allows requests under limit"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        for i in range(5):
            assert limiter.is_allowed("client1") is True, f"Request {i+1} should be allowed"
    
    def test_rate_limiter_blocks_excess_requests(self):
        """Test rate limiter blocks requests over limit"""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        
        # Consume all tokens
        for _ in range(3):
            limiter.is_allowed("client1")
        
        # Next request should be blocked
        assert limiter.is_allowed("client1") is False
    
    def test_rate_limiter_tracks_different_clients_separately(self):
        """Test rate limiter tracks each client independently"""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        # Client 1 uses both requests
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")
        
        # Client 2 should still be allowed
        assert limiter.is_allowed("client2") is True
    
    def test_check_rate_limit_raises_exception(self):
        """Test check_rate_limit raises RateLimitError"""
        # First requests should pass
        assert check_rate_limit("test_client", max_requests=3, window_seconds=60) is True
        assert check_rate_limit("test_client", max_requests=3, window_seconds=60) is True
        assert check_rate_limit("test_client", max_requests=3, window_seconds=60) is True
        
        # Fourth request should raise exception
        with pytest.raises(RateLimitError):
            check_rate_limit("test_client", max_requests=3, window_seconds=60)
    
    def test_extract_client_ip_from_x_forwarded_for(self):
        """Test extracting client IP from X-Forwarded-For (CVE-2026-23848)"""
        headers = {'X-Forwarded-For': '192.168.1.100, 10.0.0.1'}
        ip = extract_client_ip(headers)
        assert ip == '192.168.1.100'
    
    def test_extract_client_ip_with_trusted_proxies(self):
        """Test extracting client IP with trusted proxies configured"""
        headers = {'X-Forwarded-For': '192.168.1.100, 10.0.0.1, 10.0.0.2'}
        ip = extract_client_ip(headers, trusted_proxies=['10.0.0.1', '10.0.0.2'])
        assert ip == '192.168.1.100'
    
    def test_extract_client_ip_fallback_to_remote_addr(self):
        """Test fallback to REMOTE_ADDR when no forwarded headers"""
        headers = {'REMOTE_ADDR': '127.0.0.1'}
        ip = extract_client_ip(headers)
        assert ip == '127.0.0.1'
    
    def test_extract_client_ip_from_x_real_ip(self):
        """Test extracting client IP from X-Real-IP header"""
        headers = {'X-Real-IP': '192.168.1.50'}
        ip = extract_client_ip(headers)
        assert ip == '192.168.1.50'


# =============================================================================
# Pass 47: Authentication Flow Hardening Tests
# =============================================================================

class TestAuthenticationFlow:
    """Test authentication flow hardening (CVE-2026-23906, CVE-2026-28536)"""
    
    def test_ldap_anonymous_bind_detection(self):
        """Test detection of LDAP anonymous bind bypass (CVE-2026-23906)"""
        with pytest.raises(AuthenticationError) as exc_info:
            validate_ldap_auth_response(
                username="admin",
                password="",
                auth_result={'success': True, 'bind_dn': 'cn=admin'}
            )
        assert "anonymous bind bypass" in str(exc_info.value).lower()
    
    def test_ldap_whitespace_password_detection(self):
        """Test detection of whitespace-only password bypass"""
        with pytest.raises(AuthenticationError) as exc_info:
            validate_ldap_auth_response(
                username="admin",
                password="   ",
                auth_result={'success': True, 'bind_dn': 'cn=admin'}
            )
        assert "anonymous bind bypass" in str(exc_info.value).lower()
    
    def test_ldap_username_mismatch_detection(self):
        """Test detection of LDAP username mismatch"""
        with pytest.raises(AuthenticationError) as exc_info:
            validate_ldap_auth_response(
                username="admin",
                password="secret",
                auth_result={'success': True, 'username': 'hacker', 'bind_dn': 'cn=hacker'}
            )
        assert "mismatch" in str(exc_info.value).lower()
    
    def test_ldap_missing_bind_dn_detection(self):
        """Test detection of missing bind DN"""
        with pytest.raises(AuthenticationError) as exc_info:
            validate_ldap_auth_response(
                username="admin",
                password="secret",
                auth_result={'success': True}
            )
        assert "missing bind dn" in str(exc_info.value).lower()
    
    def test_ldap_valid_auth_passes(self):
        """Test valid LDAP authentication passes"""
        # Should not raise
        validate_ldap_auth_response(
            username="admin",
            password="secret123",
            auth_result={'success': True, 'username': 'admin', 'bind_dn': 'cn=admin'}
        )
    
    def test_auth_attempt_exceeds_max(self):
        """Test account lockout after max attempts (CVE-2026-28536)"""
        with pytest.raises(AuthenticationError) as exc_info:
            validate_auth_attempt(
                username="admin",
                password="wrong",
                attempt_count=5,
                max_attempts=5
            )
        assert "locked" in str(exc_info.value).lower()
    
    def test_auth_attempt_weak_password(self):
        """Test weak password detection"""
        with pytest.raises(AuthenticationError) as exc_info:
            validate_auth_attempt(
                username="admin",
                password="123",
                attempt_count=0
            )
        assert "at least 8 characters" in str(exc_info.value).lower()
    
    def test_auth_attempt_empty_username(self):
        """Test empty username detection"""
        with pytest.raises(AuthenticationError) as exc_info:
            validate_auth_attempt(
                username="",
                password="password123",
                attempt_count=0
            )
        assert "username is required" in str(exc_info.value).lower()


# =============================================================================
# Pass 48: API Key and Credential Rotation Tests
# =============================================================================

class TestCredentialRotation:
    """Test API key and credential rotation (CVE-2026-21852, CVE-2026-25253)"""
    
    def test_generate_secure_api_key_format(self):
        """Test secure API key generation format"""
        key = generate_secure_api_key(prefix="test")
        assert key.startswith("test_")
        assert len(key) >= 32
    
    def test_generate_unique_api_keys(self):
        """Test that generated API keys are unique"""
        keys = [generate_secure_api_key() for _ in range(10)]
        assert len(set(keys)) == 10  # All unique
    
    def test_validate_api_key_format_valid(self):
        """Test validation of valid API key format"""
        key = generate_secure_api_key(prefix="nis2")
        assert validate_api_key_format(key, expected_prefix="nis2") is True
    
    def test_validate_api_key_format_too_short(self):
        """Test rejection of short API key"""
        with pytest.raises(CredentialRotationError) as exc_info:
            validate_api_key_format("short")
        assert "too short" in str(exc_info.value).lower()
    
    def test_validate_api_key_format_wrong_prefix(self):
        """Test rejection of API key with wrong prefix"""
        with pytest.raises(CredentialRotationError) as exc_info:
            validate_api_key_format("wrongprefix_123456789012345678901234567890", 
                                    expected_prefix="correct")
        assert "must start with" in str(exc_info.value).lower()
    
    def test_validate_api_key_format_injection_chars(self):
        """Test rejection of API key with injection characters"""
        with pytest.raises(CredentialRotationError) as exc_info:
            validate_api_key_format("nis2_1234567890;rm -rf /12345678901234567890")
        assert "invalid characters" in str(exc_info.value).lower()
    
    def test_should_rotate_old_key(self):
        """Test detection of old API key needing rotation"""
        old_timestamp = time.time() - (100 * 24 * 3600)  # 100 days ago
        assert should_rotate_api_key(old_timestamp, max_age_days=90) is True
    
    def test_should_not_rotate_fresh_key(self):
        """Test that fresh API key doesn't need rotation"""
        fresh_timestamp = time.time() - (30 * 24 * 3600)  # 30 days ago
        assert should_rotate_api_key(fresh_timestamp, max_age_days=90) is False
    
    def test_should_rotate_missing_timestamp(self):
        """Test that missing timestamp triggers rotation"""
        assert should_rotate_api_key(None, max_age_days=90) is True
    
    def test_mask_api_key(self):
        """Test API key masking"""
        key = "nis2_abcdefghijklmnopqrstuvwxyz1234567890"
        masked = mask_api_key(key)
        assert masked.startswith("nis2")
        assert masked.endswith("7890")
        assert "..." in masked
        assert len(masked) < len(key)
    
    def test_mask_short_key(self):
        """Test masking of short key returns generic mask"""
        assert mask_api_key("short") == "***"


# =============================================================================
# Pass 49: CSRF Protection Tests
# =============================================================================

class TestCSRFProtection:
    """Test CSRF protection consolidation (CVE-2026-24885, CVE-2026-1148, CVE-2026-22030)"""
    
    def test_generate_csrf_token(self):
        """Test CSRF token generation"""
        token = generate_csrf_token()
        assert len(token) >= 32
    
    def test_generate_unique_csrf_tokens(self):
        """Test that CSRF tokens are unique"""
        tokens = [generate_csrf_token() for _ in range(10)]
        assert len(set(tokens)) == 10
    
    def test_validate_csrf_token_match(self):
        """Test valid CSRF token validation"""
        token = generate_csrf_token()
        # Should not raise
        validate_csrf_token(token, token)
    
    def test_validate_csrf_token_mismatch(self):
        """Test CSRF token mismatch detection"""
        with pytest.raises(CSRFError) as exc_info:
            validate_csrf_token("token1", "token2")
        assert "mismatch" in str(exc_info.value).lower()
    
    def test_validate_csrf_token_missing(self):
        """Test missing CSRF token detection"""
        with pytest.raises(CSRFError) as exc_info:
            validate_csrf_token(None, "expected")
        assert "missing" in str(exc_info.value).lower()
    
    def test_validate_content_type_blocks_text_plain(self):
        """Test blocking text/plain Content-Type (CVE-2026-24885)"""
        with pytest.raises(CSRFError) as exc_info:
            validate_content_type_for_csrf("text/plain")
        assert "text/plain" in str(exc_info.value)
    
    def test_validate_content_type_allows_json(self):
        """Test allowing application/json Content-Type"""
        # Should not raise
        validate_content_type_for_csrf("application/json")
    
    def test_validate_content_type_allows_form_encoded(self):
        """Test allowing form Content-Type with charset"""
        # Should not raise
        validate_content_type_for_csrf("application/x-www-form-urlencoded; charset=utf-8")
    
    def test_validate_content_type_missing(self):
        """Test missing Content-Type detection"""
        with pytest.raises(CSRFError) as exc_info:
            validate_content_type_for_csrf(None)
        assert "required" in str(exc_info.value).lower()
    
    def test_validate_origin_header_allowed(self):
        """Test allowed origin validation"""
        # Should not raise
        validate_origin_header("https://app.example.com", 
                               ["https://app.example.com"])
    
    def test_validate_origin_header_not_allowed(self):
        """Test rejected origin (CVE-2026-22030)"""
        with pytest.raises(CSRFError) as exc_info:
            validate_origin_header("https://evil.com", 
                                   ["https://app.example.com"])
        assert "not allowed" in str(exc_info.value).lower()
    
    def test_validate_origin_header_subdomain_match(self):
        """Test subdomain origin matching"""
        # Should not raise
        validate_origin_header("https://sub.example.com",
                               ["https://example.com"])


# =============================================================================
# Pass 50: WebSocket Security Tests
# =============================================================================

class TestWebSocketSecurity:
    """Test WebSocket origin validation (CVE-2026-1692)"""
    
    def test_validate_websocket_origin_allowed(self):
        """Test allowed WebSocket origin"""
        # Should not raise
        validate_websocket_origin("https://app.example.com",
                                   ["https://app.example.com"])
    
    def test_validate_websocket_origin_missing(self):
        """Test missing WebSocket origin (CVE-2026-1692)"""
        with pytest.raises(WebSocketSecurityError) as exc_info:
            validate_websocket_origin(None, ["https://app.example.com"])
        assert "missing" in str(exc_info.value).lower()
    
    def test_validate_websocket_origin_not_allowed(self):
        """Test rejected WebSocket origin"""
        with pytest.raises(WebSocketSecurityError) as exc_info:
            validate_websocket_origin("https://evil.com",
                                       ["https://app.example.com"])
        assert "not allowed" in str(exc_info.value).lower()
    
    def test_validate_websocket_origin_wildcard_subdomain(self):
        """Test WebSocket origin with wildcard subdomain"""
        # Should not raise
        validate_websocket_origin("https://ws.example.com",
                                   ["https://*.example.com"])
    
    def test_get_websocket_security_headers(self):
        """Test WebSocket security headers generation"""
        headers = get_websocket_security_headers()
        assert 'X-Content-Type-Options' in headers
        assert 'X-Frame-Options' in headers
        assert headers['X-Frame-Options'] == 'DENY'


# =============================================================================
# Pass 51: CORS Policy Tests
# =============================================================================

class TestCORSPolicy:
    """Test CORS policy enforcement (CVE-2024-10906, CVE-2026-24435)"""
    
    def test_validate_cors_origin_allowed(self):
        """Test allowed CORS origin"""
        assert validate_cors_origin("https://api.example.com",
                                     ["https://api.example.com"]) is True
    
    def test_validate_cors_origin_wildcard_rejected(self):
        """Test wildcard origin rejection (CVE-2024-10906)"""
        with pytest.raises(CORSError) as exc_info:
            validate_cors_origin("https://any.com", ["*"])
        assert "wildcard" in str(exc_info.value).lower()
    
    def test_validate_cors_origin_not_allowed(self):
        """Test rejected CORS origin (CVE-2026-24435)"""
        with pytest.raises(CORSError) as exc_info:
            validate_cors_origin("https://evil.com",
                                  ["https://api.example.com"])
        assert "not allowed" in str(exc_info.value).lower()
    
    def test_validate_cors_origin_empty_allowed(self):
        """Test empty origin (same-origin request) allowed"""
        assert validate_cors_origin(None, ["https://api.example.com"]) is True
    
    def test_get_cors_headers_structure(self):
        """Test CORS headers structure"""
        headers = get_cors_headers(
            origin="https://app.example.com",
            allowed_origins=["https://app.example.com"],
            allow_credentials=True
        )
        assert 'Access-Control-Allow-Origin' in headers
        assert 'Access-Control-Allow-Methods' in headers
        assert headers['Access-Control-Allow-Origin'] == "https://app.example.com"
    
    def test_get_cors_headers_rejects_disallowed_origin(self):
        """Test that CORS headers are empty for disallowed origin"""
        headers = get_cors_headers(
            origin="https://evil.com",
            allowed_origins=["https://app.example.com"]
        )
        assert headers == {}
    
    def test_validate_cors_preflight_valid(self):
        """Test valid CORS preflight request"""
        # Should not raise
        validate_cors_preflight_request(
            origin="https://app.example.com",
            requested_method="POST",
            requested_headers="Content-Type, X-Custom-Header",
            allowed_methods=["GET", "POST"],
            allowed_headers=["Content-Type", "X-Custom-Header"]
        )
    
    def test_validate_cors_preflight_invalid_method(self):
        """Test CORS preflight with invalid method"""
        with pytest.raises(CORSError) as exc_info:
            validate_cors_preflight_request(
                origin="https://app.example.com",
                requested_method="DELETE",
                requested_headers="",
                allowed_methods=["GET", "POST"],
                allowed_headers=["Content-Type"]
            )
        assert "not allowed" in str(exc_info.value).lower()
    
    def test_validate_cors_preflight_invalid_header(self):
        """Test CORS preflight with invalid header"""
        with pytest.raises(CORSError) as exc_info:
            validate_cors_preflight_request(
                origin="https://app.example.com",
                requested_method="POST",
                requested_headers="X-Evil-Header",
                allowed_methods=["GET", "POST"],
                allowed_headers=["Content-Type"]
            )
        assert "not allowed" in str(exc_info.value).lower()


# =============================================================================
# Pass 52: Audit Log Integrity Tests
# =============================================================================

class TestAuditLogIntegrity:
    """Test audit log integrity (CVE-2026-3494)"""
    
    def test_create_audit_log_entry_structure(self):
        """Test audit log entry has required fields"""
        entry = create_audit_log_entry(
            action="user_login",
            user="admin",
            resource="/api/login"
        )
        
        assert 'timestamp' in entry
        assert 'timestamp_iso' in entry
        assert entry['action'] == "user_login"
        assert entry['user'] == "admin"
        assert entry['resource'] == "/api/login"
        assert 'integrity_hash' in entry
    
    def test_create_audit_log_entry_sanitizes_input(self):
        """Test audit log entry sanitizes input"""
        entry = create_audit_log_entry(
            action="login\ninject",
            user="admin\r\n",
            resource="/api/test\x00"
        )
        
        assert '\n' not in entry['action']
        assert '\r' not in entry['user']
        assert '\x00' not in entry['resource']
    
    def test_verify_audit_entry_valid(self):
        """Test valid audit entry verification"""
        entry = create_audit_log_entry(
            action="test",
            user="admin",
            resource="/api/test"
        )
        
        assert verify_audit_entry(entry) is True
    
    def test_verify_audit_entry_tampered(self):
        """Test tampered audit entry detection"""
        entry = create_audit_log_entry(
            action="test",
            user="admin",
            resource="/api/test"
        )
        
        # Tamper with the entry
        entry['action'] = "hacked"
        
        assert verify_audit_entry(entry) is False
    
    def test_verify_audit_entry_missing_hash(self):
        """Test verification with missing hash"""
        entry = {
            'timestamp': time.time(),
            'action': 'test',
            'user': 'admin',
            'resource': '/api/test'
        }
        
        assert verify_audit_entry(entry) is False
    
    def test_sanitize_audit_user_id(self):
        """Test user ID sanitization"""
        sanitized = sanitize_audit_user_id("user\n123\r\n")
        assert '\n' not in sanitized
        assert '\r' not in sanitized
        assert sanitized == "user123"
    
    def test_sanitize_audit_user_id_empty(self):
        """Test empty user ID sanitization"""
        assert sanitize_audit_user_id(None) == "anonymous"
        assert sanitize_audit_user_id("") == "anonymous"


# =============================================================================
# Pass 53: Configuration Security Tests
# =============================================================================

class TestConfigurationSecurity:
    """Test configuration security validation (CVE-2026-1731, CVE-2025-60262)"""
    
    def test_validate_config_security_detects_empty_password(self):
        """Test detection of empty password (CVE-2026-1731)"""
        config = "password=''\nsecret=''"
        issues = validate_configuration_security(config)
        
        descriptions = [i['description'] for i in issues]
        assert "Empty password" in descriptions
    
    def test_validate_config_security_detects_debug_mode(self):
        """Test detection of debug mode enabled"""
        config = "debug=true"
        issues = validate_configuration_security(config)
        
        descriptions = [i['description'] for i in issues]
        assert "Debug mode enabled" in descriptions
    
    def test_validate_config_security_detects_wildcard_cors(self):
        """Test detection of wildcard CORS (CVE-2024-10906)"""
        config = "allow_origin=*"
        issues = validate_configuration_security(config)
        
        descriptions = [i['description'] for i in issues]
        assert "Wildcard CORS origin" in descriptions
    
    def test_validate_config_security_detects_bind_all_interfaces(self):
        """Test detection of binding to all interfaces"""
        config = "bind=0.0.0.0"
        issues = validate_configuration_security(config)
        
        descriptions = [i['description'] for i in issues]
        assert "Binding to all interfaces" in descriptions
    
    def test_validate_config_security_detects_hardcoded_api_key(self):
        """Test detection of hardcoded API key (CVE-2026-25253)"""
        config = 'api_key="sklive1234567890abcdefghijklmn"'
        issues = validate_configuration_security(config)
        
        # Check that we detected the hardcoded API key
        descriptions = [i['description'].lower() for i in issues]
        assert any('api key' in d for d in descriptions)
    
    def test_check_secure_defaults_missing_settings(self):
        """Test detection of missing security settings"""
        config = {}
        missing = check_secure_defaults(config)
        
        settings = [m['setting'] for m in missing]
        assert 'csrf_protection' in settings
        assert 'secure_cookies' in settings
        assert 'http_only_cookies' in settings
    
    def test_check_secure_defaults_incorrect_values(self):
        """Test detection of insecure security settings"""
        config = {
            'csrf_protection': False,
            'secure_cookies': False,
        }
        missing = check_secure_defaults(config)
        
        for m in missing:
            if m['setting'] == 'csrf_protection':
                assert m['current'] is False
                assert m['recommended'] is True


# =============================================================================
# Pass 54: Error Message Sanitization Tests
# =============================================================================

class TestErrorSanitization:
    """Test error message sanitization (CVE-2026-26144, CVE-2026-20838)"""
    
    def test_sanitize_production_error_database(self):
        """Test database error sanitization"""
        error = "Database connection failed: SQL syntax error near 'SELECT'"
        sanitized = sanitize_production_error(error, is_production=True)
        assert sanitized == "Database operation failed"
    
    def test_sanitize_production_error_file_not_found(self):
        """Test file error sanitization"""
        error = "File '/etc/passwd' not found at line 42"
        sanitized = sanitize_production_error(error, is_production=True)
        assert sanitized == "Resource not found"
    
    def test_sanitize_production_error_permission(self):
        """Test permission error sanitization"""
        error = "Permission denied accessing /admin/config"
        sanitized = sanitize_production_error(error, is_production=True)
        assert sanitized == "Access denied"
    
    def test_sanitize_production_error_authentication(self):
        """Test authentication error sanitization"""
        error = "Authentication failed: password mismatch for user admin"
        sanitized = sanitize_production_error(error, is_production=True)
        assert sanitized == "Authentication failed"
    
    def test_sanitize_production_error_generic(self):
        """Test generic error sanitization"""
        error = "Something unexpected happened in the system"
        sanitized = sanitize_production_error(error, is_production=True)
        assert sanitized == "An unexpected error occurred"
    
    def test_sanitize_production_error_development_mode(self):
        """Test that development mode preserves error"""
        error = "Detailed stack trace and internal information"
        sanitized = sanitize_production_error(error, is_production=False)
        assert sanitized == error
    
    def test_get_safe_error_response_production(self):
        """Test safe error response for production"""
        error = ValueError("Database connection failed")
        response = get_safe_error_response(error, is_production=True)
        
        assert response['error'] == 'Internal Server Error'
        assert 'error_id' in response
        assert response['message'] == "Database operation failed"
    
    def test_get_safe_error_response_development(self):
        """Test error response for development"""
        error = ValueError("Something went wrong")
        response = get_safe_error_response(error, is_production=False)
        
        assert response['error'] == 'ValueError'
        assert 'error_id' in response
        assert response['message'] == "Something went wrong"


# =============================================================================
# Pass 55: Session Timeout Tests
# =============================================================================

class TestSessionTimeout:
    """Test session timeout enforcement (CVE-2026-23646)"""
    
    def test_validate_session_timeout_valid(self):
        """Test valid session (within timeouts)"""
        now = time.time()
        # Should not raise
        validate_session_timeout(
            created_at=now - 300,  # 5 minutes ago
            last_activity=now - 60,  # 1 minute ago
            max_duration=3600,
            idle_timeout=900
        )
    
    def test_validate_session_timeout_max_duration_exceeded(self):
        """Test session exceeding maximum duration"""
        now = time.time()
        with pytest.raises(SessionTimeoutError) as exc_info:
            validate_session_timeout(
                created_at=now - 90000,  # 25 hours ago
                last_activity=now - 60,
                max_duration=86400,  # 24 hours
                idle_timeout=900
            )
        assert "maximum duration" in str(exc_info.value).lower()
    
    def test_validate_session_timeout_idle_exceeded(self):
        """Test session exceeding idle timeout"""
        now = time.time()
        with pytest.raises(SessionTimeoutError) as exc_info:
            validate_session_timeout(
                created_at=now - 300,
                last_activity=now - 1000,  # 16+ minutes ago
                max_duration=3600,
                idle_timeout=900  # 15 minutes
            )
        assert "idle timeout" in str(exc_info.value).lower()
    
    def test_calculate_session_ttl_valid(self):
        """Test TTL calculation for valid session"""
        now = time.time()
        ttl = calculate_session_ttl(
            created_at=now - 300,
            last_activity=now - 60,
            max_duration=3600,
            idle_timeout=900
        )
        assert ttl > 0
        assert ttl <= 900  # Limited by idle timeout
    
    def test_calculate_session_ttl_expired(self):
        """Test TTL calculation for expired session"""
        now = time.time()
        ttl = calculate_session_ttl(
            created_at=now - 90000,  # Expired
            last_activity=now - 60,
            max_duration=86400,
            idle_timeout=900
        )
        assert ttl == 0
    
    def test_should_refresh_session_true(self):
        """Test session refresh recommendation (over threshold)"""
        now = time.time()
        threshold_reached = MAX_SESSION_DURATION * 0.8 + 100
        should_refresh = should_refresh_session(
            created_at=now - threshold_reached,
            refresh_threshold=0.8
        )
        assert should_refresh is True
    
    def test_should_refresh_session_false(self):
        """Test session refresh recommendation (under threshold)"""
        now = time.time()
        should_refresh = should_refresh_session(
            created_at=now - 1000,  # Very fresh
            refresh_threshold=0.8
        )
        assert should_refresh is False


# =============================================================================
# Pass 56: File Upload Restriction Tests
# =============================================================================

class TestFileUploadRestriction:
    """Test file upload restrictions (CVE-2026-21536)"""
    
    def test_validate_upload_extension_allows_pdf(self):
        """Test PDF upload allowed"""
        # Should not raise
        validate_upload_file_extension("document.pdf")
    
    def test_validate_upload_extension_rejects_exe(self):
        """Test executable rejection (CVE-2026-21536)"""
        with pytest.raises(FileUploadRestrictionError) as exc_info:
            validate_upload_file_extension("malware.exe")
        assert ".exe" in str(exc_info.value).lower()
    
    def test_validate_upload_extension_rejects_php(self):
        """Test PHP file rejection"""
        with pytest.raises(FileUploadRestrictionError) as exc_info:
            validate_upload_file_extension("shell.php")
        assert ".php" in str(exc_info.value).lower()
    
    def test_validate_upload_extension_rejects_double_extension(self):
        """Test double extension bypass attempt"""
        with pytest.raises(FileUploadRestrictionError) as exc_info:
            validate_upload_file_extension("file.pdf.exe")
        assert ".exe" in str(exc_info.value).lower()
    
    def test_validate_upload_extension_empty_filename(self):
        """Test empty filename rejection"""
        with pytest.raises(FileUploadRestrictionError) as exc_info:
            validate_upload_file_extension("")
        assert "filename is required" in str(exc_info.value).lower()
    
    def test_validate_upload_size_allows_small(self):
        """Test small file size allowed"""
        # Should not raise
        validate_upload_file_size(1024 * 1024, max_size_mb=10)  # 1MB
    
    def test_validate_upload_size_rejects_large(self):
        """Test large file size rejection"""
        with pytest.raises(FileUploadRestrictionError) as exc_info:
            validate_upload_file_size(15 * 1024 * 1024, max_size_mb=10)  # 15MB
        assert "exceeds" in str(exc_info.value).lower()
    
    def test_sanitize_uploaded_filename_removes_path(self):
        """Test path removal from filename"""
        sanitized = sanitize_uploaded_filename("/etc/passwd")
        assert sanitized == "passwd"
    
    def test_sanitize_uploaded_filename_removes_null_bytes(self):
        """Test null byte removal"""
        sanitized = sanitize_uploaded_filename("file\x00.txt")
        assert '\x00' not in sanitized
    
    def test_sanitize_uploaded_filename_handles_hidden_file(self):
        """Test hidden file handling"""
        sanitized = sanitize_uploaded_filename(".htaccess")
        assert sanitized.startswith("file_")
    
    def test_sanitize_uploaded_filename_limits_length(self):
        """Test filename length limiting"""
        long_name = "a" * 200 + ".txt"
        sanitized = sanitize_uploaded_filename(long_name)
        assert len(sanitized) <= 108  # 100 + ".txt"


# =============================================================================
# Pass 57: Request Origin Validation Tests
# =============================================================================

class TestRequestOriginValidation:
    """Test request origin validation (CVE-2026-25151, CVE-2026-25221)"""
    
    def test_validate_request_origin_with_origin_header(self):
        """Test validation with Origin header"""
        headers = {
            'Origin': 'https://app.example.com',
            'Host': 'api.example.com'
        }
        # Should not raise
        validate_request_origin(
            headers,
            allowed_hosts=['app.example.com'],
            require_https=True
        )
    
    def test_validate_request_origin_with_referer_header(self):
        """Test validation with Referer header fallback"""
        headers = {
            'Referer': 'https://app.example.com/page',
            'Host': 'api.example.com'
        }
        # Should not raise
        validate_request_origin(
            headers,
            allowed_hosts=['app.example.com'],
            require_https=True
        )
    
    def test_validate_request_origin_missing_headers(self):
        """Test rejection when both Origin and Referer missing"""
        headers = {'Host': 'api.example.com'}
        with pytest.raises(OriginValidationError) as exc_info:
            validate_request_origin(
                headers,
                allowed_hosts=['app.example.com'],
                require_https=True
            )
        assert "required" in str(exc_info.value).lower()
    
    def test_validate_request_origin_not_allowed(self):
        """Test rejection of disallowed origin"""
        headers = {'Origin': 'https://evil.com'}
        with pytest.raises(OriginValidationError) as exc_info:
            validate_request_origin(
                headers,
                allowed_hosts=['app.example.com'],
                require_https=True
            )
        assert "not in allowed hosts" in str(exc_info.value).lower()
    
    def test_validate_request_origin_http_rejected(self):
        """Test HTTP origin rejection when HTTPS required"""
        headers = {'Origin': 'http://app.example.com'}
        with pytest.raises(OriginValidationError) as exc_info:
            validate_request_origin(
                headers,
                allowed_hosts=['app.example.com'],
                require_https=True
            )
        assert "https required" in str(exc_info.value).lower()
    
    def test_validate_request_origin_localhost_allowed(self):
        """Test localhost HTTP allowed in development"""
        headers = {'Origin': 'http://localhost:3000'}
        # Should not raise
        validate_request_origin(
            headers,
            allowed_hosts=['localhost:3000'],
            require_https=True
        )
    
    def test_validate_oauth_state_match(self):
        """Test valid OAuth state validation (CVE-2026-25221)"""
        state = "random_state_value_12345"
        # Should not raise
        validate_oauth_state(state, state)
    
    def test_validate_oauth_state_mismatch(self):
        """Test OAuth state mismatch detection"""
        with pytest.raises(OriginValidationError) as exc_info:
            validate_oauth_state("state1", "state2")
        assert "mismatch" in str(exc_info.value).lower()
    
    def test_validate_oauth_state_missing(self):
        """Test missing OAuth state detection"""
        with pytest.raises(OriginValidationError) as exc_info:
            validate_oauth_state(None, "expected")
        assert "missing" in str(exc_info.value).lower()


# =============================================================================
# Pass 58: Security Header Consolidation Tests
# =============================================================================

class TestSecurityHeaders:
    """Test security header consolidation"""
    
    def test_get_security_headers_structure(self):
        """Test security headers structure"""
        headers = get_security_headers(https_only=True)
        
        assert 'X-Content-Type-Options' in headers
        assert 'X-XSS-Protection' in headers
        assert 'X-Frame-Options' in headers
        assert 'Strict-Transport-Security' in headers
        assert 'Referrer-Policy' in headers
        assert 'Permissions-Policy' in headers
    
    def test_get_security_headers_no_https(self):
        """Test headers without HTTPS enforcement"""
        headers = get_security_headers(https_only=False)
        
        assert 'Strict-Transport-Security' not in headers
        assert 'X-Content-Type-Options' in headers
    
    def test_get_content_security_policy_structure(self):
        """Test CSP structure"""
        csp = get_content_security_policy()
        
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp
        assert "object-src 'none'" in csp
        assert "frame-ancestors 'none'" in csp
    
    def test_get_content_security_policy_with_nonce(self):
        """Test CSP with nonce"""
        csp = get_content_security_policy(nonce="abc123")
        
        assert "'nonce-abc123'" in csp
    
    def test_validate_security_headers_detects_missing(self):
        """Test detection of missing security headers"""
        response_headers = {}  # Empty headers
        issues = validate_security_headers(response_headers)
        
        header_names = [i['header'] for i in issues]
        assert 'x-content-type-options' in header_names
        assert 'x-frame-options' in header_names
    
    def test_validate_security_headers_detects_weak_values(self):
        """Test detection of weak header values"""
        response_headers = {
            'X-Frame-Options': 'ALLOWALL',  # Weak
            'X-Content-Type-Options': 'nosniff',  # Good
        }
        issues = validate_security_headers(response_headers)
        
        weak_issues = [i for i in issues if i.get('issue') == 'weak']
        assert len(weak_issues) > 0
    
    def test_validate_security_headers_passes_valid(self):
        """Test validation passes with valid headers"""
        response_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'Strict-Transport-Security': 'max-age=31536000',
        }
        issues = validate_security_headers(response_headers)
        
        # Should have no issues (or minimal)
        assert len(issues) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
