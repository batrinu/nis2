"""
Security tests for Passes 59-79 (Application Consolidation Phase - 21 passes)
Based on March 2026 CVE research focused on application-level security

Covers:
- Pass 59: Request Validation Middleware (CVE-2026-21962, CVE-2026-0958)
- Pass 60: Response Security Middleware (CVE-2026-2975, CVE-2026-24489)
- Pass 61: Authentication Middleware Integration (CVE-2026-27705, CVE-2026-1894)
- Pass 62: Authorization Enforcement Layer (CVE-2026-27705, CVE-2026-23982)
- Pass 63: Database Query Protection (CVE-2026-25544, CVE-2026-23984)
- Pass 64: Input Sanitization Pipeline (CVE-2026-25632, CVE-2026-25520)
- Pass 65: Output Encoding Framework (CVE-2026-25643, CVE-2026-25881)
- Pass 66: Session Management Integration (CVE-2026-23646, CVE-2026-22341)
- Pass 67: File Operation Security (CVE-2026-27897, CVE-2026-25766)
- Pass 68: API Security Hardening (CVE-2026-25544, CVE-2026-1894)
- Pass 69: Webhook Security (CVE-2026-27488, CVE-2026-28467)
- Pass 70: Background Job Security (CVE-2026-25643, CVE-2026-25641)
- Pass 71: Cache Security (CVE-2026-27897, CVE-2026-2835)
- Pass 72: Email Security Integration (CVE-2026-28289, CVE-2026-24486)
- Pass 73: Notification Security (CVE-2026-30839, CVE-2026-30953)
- Pass 74: Report Generation Security (CVE-2026-26144, CVE-2026-28794)
- Pass 75: Data Export Security (CVE-2026-21536, CVE-2026-27897)
- Pass 76: Admin Panel Security (CVE-2026-1731, CVE-2026-22769)
- Pass 77: Audit Logging Integration (CVE-2026-3494, CVE-2026-30928)
- Pass 78: Configuration Security Integration (CVE-2026-25253, CVE-2026-25643)
- Pass 79: Security Monitoring Integration (CVE-2026-1709, CVE-2026-1568)
"""
import pytest
import time
import sys
import os

# Add the app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'nis2-audit-app'))

from app.security_utils import (
    # Pass 59
    RequestValidationError, validate_request_size, validate_content_type,
    validate_json_payload, sanitize_request_path, MAX_JSON_SIZE,
    # Pass 60
    ResponseSecurityError, validate_response_headers, add_security_headers,
    validate_response_content_type,
    # Pass 61
    AuthenticationMiddlewareError, extract_auth_token, validate_auth_context,
    # Pass 62
    AuthorizationError, check_resource_access, require_permission,
    ROLE_ADMIN, ROLE_MEMBER, ROLE_GUEST,
    # Pass 63
    DatabaseSecurityError, validate_raw_query, sanitize_query_parameter,
    # Pass 64
    InputSanitizationError, sanitize_input_pipeline, sanitize_file_path_input,
    # Pass 65
    OutputEncodingError, encode_html_output, encode_javascript_output,
    encode_css_output, encode_url_output, encode_json_output,
    # Pass 66
    SessionManagementError, SecureSessionStore,
    # Pass 67
    FileOperationError, secure_file_read, secure_file_write,
    get_secure_download_headers,
    # Pass 68
    APISecurityError, validate_api_request, validate_graphql_query,
    validate_bulk_operation, API_RATE_LIMITS,
    # Pass 69
    WebhookSecurityError, validate_webhook_url, verify_webhook_signature,
    generate_webhook_signature,
    # Pass 70
    JobSecurityError, validate_job_payload, sanitize_job_result,
    # Pass 71
    CacheSecurityError, sanitize_cache_key, check_sensitive_cache_key,
    validate_cache_ttl,
    # Pass 72
    EmailSecurityError, sanitize_email_address, sanitize_email_subject,
    validate_email_attachment,
    # Pass 73
    NotificationSecurityError, validate_notification_payload,
    sanitize_notification_content,
    # Pass 74
    ReportSecurityError, sanitize_csv_field, generate_secure_csv,
    validate_report_access,
    # Pass 75
    ExportSecurityError, validate_export_request, mask_sensitive_export_data,
    # Pass 76
    AdminSecurityError, validate_admin_action, check_admin_ip_restriction,
    # Pass 77
    AuditLoggingError, should_audit_action, create_audit_event, SENSITIVE_ACTIONS,
    # Pass 78
    ConfigIntegrationError, validate_runtime_config_change, sanitize_config_value,
    # Pass 79
    SecurityMonitoringError, generate_security_event, check_anomaly_threshold,
)


# =============================================================================
# Pass 59: Request Validation Middleware Tests
# =============================================================================

class TestRequestValidation:
    """Test request validation middleware (CVE-2026-21962, CVE-2026-0958)"""
    
    def test_validate_request_size_within_limit(self):
        """Test request size validation within limit"""
        # Should not raise
        validate_request_size(1024 * 1024, max_size=10*1024*1024)
    
    def test_validate_request_size_exceeds_limit(self):
        """Test request size validation exceeding limit"""
        with pytest.raises(RequestValidationError) as exc_info:
            validate_request_size(15*1024*1024, max_size=10*1024*1024)
        assert "exceeds" in str(exc_info.value).lower()
    
    def test_validate_content_type_allowed(self):
        """Test allowed content type validation"""
        # Should not raise
        validate_content_type("application/json")
        validate_content_type("application/json; charset=utf-8")
    
    def test_validate_content_type_not_allowed(self):
        """Test disallowed content type"""
        with pytest.raises(RequestValidationError) as exc_info:
            validate_content_type("application/octet-stream", 
                                  allowed_types=['application/json'])
        assert "not allowed" in str(exc_info.value).lower()
    
    def test_validate_json_payload_valid(self):
        """Test valid JSON payload validation"""
        result = validate_json_payload('{"key": "value"}')
        assert result == {"key": "value"}
    
    def test_validate_json_payload_invalid(self):
        """Test invalid JSON payload"""
        with pytest.raises(RequestValidationError):
            validate_json_payload('not valid json')
    
    def test_validate_json_payload_prototype_pollution(self):
        """Test prototype pollution detection (CVE-2026-28794)"""
        with pytest.raises(RequestValidationError) as exc_info:
            validate_json_payload('{"__proto__": {"evil": true}}')
        assert "prototype pollution" in str(exc_info.value).lower()
    
    def test_sanitize_request_path_valid(self):
        """Test valid path sanitization"""
        result = sanitize_request_path("/api/users/123")
        assert result == "/api/users/123"
    
    def test_sanitize_request_path_traversal(self):
        """Test path traversal detection (CVE-2026-21962)"""
        with pytest.raises(RequestValidationError) as exc_info:
            sanitize_request_path("/api/../admin")
        assert "traversal" in str(exc_info.value).lower()
    
    def test_sanitize_request_path_null_byte(self):
        """Test null byte detection"""
        with pytest.raises(RequestValidationError):
            sanitize_request_path("/api/users\x00/admin")


# =============================================================================
# Pass 60: Response Security Middleware Tests
# =============================================================================

class TestResponseSecurity:
    """Test response security middleware (CVE-2026-2975, CVE-2026-24489)"""
    
    def test_validate_response_headers(self):
        """Test response header validation"""
        headers = {'Content-Type': 'text/html', 'X-Custom': 'value'}
        result = validate_response_headers(headers)
        assert 'Content-Type' in result
    
    def test_add_security_headers(self):
        """Test adding security headers"""
        headers = {}
        result = add_security_headers(headers, https_only=True)
        assert 'X-Frame-Options' in result
        assert 'Strict-Transport-Security' in result
    
    def test_validate_response_content_type_dangerous(self):
        """Test dangerous content type detection"""
        with pytest.raises(ResponseSecurityError) as exc_info:
            validate_response_content_type("application/x-msdownload")
        assert "dangerous" in str(exc_info.value).lower()


# =============================================================================
# Pass 61: Authentication Middleware Tests
# =============================================================================

class TestAuthenticationMiddleware:
    """Test authentication middleware (CVE-2026-27705, CVE-2026-1894)"""
    
    def test_extract_auth_token_bearer(self):
        """Test Bearer token extraction"""
        headers = {'Authorization': 'Bearer token123'}
        token_type, token = extract_auth_token(headers)
        assert token_type == 'bearer'
        assert token == 'token123'
    
    def test_extract_auth_token_api_key(self):
        """Test API key extraction"""
        headers = {'X-API-Key': 'secret_key'}
        token_type, token = extract_auth_token(headers)
        assert token_type == 'apikey'
        assert token == 'secret_key'
    
    def test_extract_auth_token_missing(self):
        """Test missing token"""
        headers = {}
        token_type, token = extract_auth_token(headers)
        assert token_type is None
        assert token is None
    
    def test_validate_auth_context_valid(self):
        """Test valid auth context"""
        result = validate_auth_context("valid_token_12345678", "bearer")
        assert result['valid'] is True
    
    def test_validate_auth_context_short_token(self):
        """Test short token rejection"""
        with pytest.raises(AuthenticationMiddlewareError) as exc_info:
            validate_auth_context("short", "bearer")
        assert "too short" in str(exc_info.value).lower()


# =============================================================================
# Pass 62: Authorization Enforcement Tests
# =============================================================================

class TestAuthorization:
    """Test authorization enforcement (CVE-2026-27705, CVE-2026-23982)"""
    
    def test_check_resource_access_admin(self):
        """Test admin can access any resource"""
        # Should not raise
        check_resource_access(ROLE_ADMIN, "other_user", "admin_user", "delete")
    
    def test_check_resource_access_own_resource(self):
        """Test user can access own resource"""
        # Should not raise
        check_resource_access(ROLE_MEMBER, "user123", "user123", "write")
    
    def test_check_resource_access_insufficient_permissions(self):
        """Test insufficient permissions (CVE-2026-27705)"""
        with pytest.raises(AuthorizationError) as exc_info:
            check_resource_access(ROLE_GUEST, "other_user", "guest_user", "delete")
        assert "only admins" in str(exc_info.value).lower()
    
    def test_require_permission_sufficient(self):
        """Test sufficient role level"""
        # Should not raise
        require_permission(ROLE_MEMBER, ROLE_ADMIN)
    
    def test_require_permission_insufficient(self):
        """Test insufficient role level"""
        with pytest.raises(AuthorizationError) as exc_info:
            require_permission(ROLE_ADMIN, ROLE_GUEST)
        assert "insufficient" in str(exc_info.value).lower()


# =============================================================================
# Pass 63: Database Query Protection Tests
# =============================================================================

class TestDatabaseSecurity:
    """Test database query protection (CVE-2026-25544, CVE-2026-23984)"""
    
    def test_validate_raw_query_safe(self):
        """Test safe query validation"""
        # Should not raise
        validate_raw_query("SELECT * FROM users WHERE id = ?", 
                          allowed_tables=['users'])
    
    def test_validate_raw_query_dangerous_keyword(self):
        """Test dangerous keyword detection (CVE-2026-25544)"""
        with pytest.raises(DatabaseSecurityError) as exc_info:
            validate_raw_query("DROP TABLE users")
        assert "dangerous keyword" in str(exc_info.value).lower()
    
    def test_validate_raw_query_table_not_allowed(self):
        """Test table allowlist enforcement"""
        with pytest.raises(DatabaseSecurityError) as exc_info:
            validate_raw_query("SELECT * FROM secret_table", 
                              allowed_tables=['users', 'posts'])
        assert "not in allowlist" in str(exc_info.value).lower()
    
    def test_sanitize_query_parameter(self):
        """Test query parameter sanitization"""
        result = sanitize_query_parameter("test'; DROP TABLE users; --")
        assert "--" not in result
        assert ";" not in result


# =============================================================================
# Pass 64: Input Sanitization Pipeline Tests
# =============================================================================

class TestInputSanitization:
    """Test input sanitization pipeline (CVE-2026-25632, CVE-2026-25520)"""
    
    def test_sanitize_input_pipeline_normal(self):
        """Test normal input sanitization"""
        result = sanitize_input_pipeline("Hello World")
        assert result == "Hello World"
    
    def test_sanitize_input_pipeline_unicode_dangerous(self):
        """Test Unicode dangerous character removal"""
        result = sanitize_input_pipeline("Hello\u200bWorld")  # Zero-width space
        assert "\u200b" not in result
    
    def test_sanitize_input_pipeline_html_stripping(self):
        """Test HTML stripping"""
        result = sanitize_input_pipeline("<script>alert(1)</script>Hello")
        assert "<script>" not in result
    
    def test_sanitize_input_pipeline_too_long(self):
        """Test length limit enforcement"""
        with pytest.raises(InputSanitizationError):
            sanitize_input_pipeline("x" * 20000, max_length=10000)
    
    def test_sanitize_file_path_input_traversal(self):
        """Test file path traversal detection"""
        with pytest.raises(InputSanitizationError) as exc_info:
            sanitize_file_path_input("/etc/../passwd")
        assert "traversal" in str(exc_info.value).lower()


# =============================================================================
# Pass 65: Output Encoding Framework Tests
# =============================================================================

class TestOutputEncoding:
    """Test output encoding framework (CVE-2026-25643, CVE-2026-25881)"""
    
    def test_encode_html_output(self):
        """Test HTML output encoding"""
        result = encode_html_output("<script>alert('xss')</script>")
        assert "<" not in result
        assert "&lt;" in result
    
    def test_encode_javascript_output(self):
        """Test JavaScript output encoding"""
        result = encode_javascript_output("alert('xss');")
        assert ";" not in result or "\\" in result
    
    def test_encode_css_output(self):
        """Test CSS output encoding"""
        result = encode_css_output("expression(alert(1))")
        assert "(" not in result
    
    def test_encode_url_output(self):
        """Test URL output encoding"""
        result = encode_url_output("https://example.com/path?key=value&other=test")
        assert "https://" in result
    
    def test_encode_json_output(self):
        """Test JSON output encoding"""
        result = encode_json_output({"key": "value", "num": 123})
        assert '"key": "value"' in result


# =============================================================================
# Pass 66: Session Management Integration Tests
# =============================================================================

class TestSessionManagement:
    """Test session management integration (CVE-2026-23646, CVE-2026-22341)"""
    
    def test_secure_session_store_create(self):
        """Test session creation"""
        store = SecureSessionStore()
        session_id = store.create_session("user123", "192.168.1.1", "Mozilla/5.0")
        assert len(session_id) >= 32
    
    def test_secure_session_store_validate_valid(self):
        """Test valid session validation"""
        store = SecureSessionStore()
        session_id = store.create_session("user123", "192.168.1.1")
        result = store.validate_session(session_id)
        assert result['user_id'] == "user123"
    
    def test_secure_session_store_validate_invalid(self):
        """Test invalid session rejection"""
        store = SecureSessionStore()
        with pytest.raises(SessionManagementError) as exc_info:
            store.validate_session("invalid_session")
        assert "invalid session" in str(exc_info.value).lower()
    
    def test_secure_session_store_regenerate(self):
        """Test session regeneration (prevents fixation)"""
        store = SecureSessionStore()
        old_id = store.create_session("user123")
        new_id = store.regenerate_session(old_id)
        assert old_id != new_id
        # Old session should be invalid
        with pytest.raises(SessionManagementError):
            store.validate_session(old_id)


# =============================================================================
# Pass 67: File Operation Security Tests
# =============================================================================

class TestFileOperationSecurity:
    """Test file operation security (CVE-2026-27897, CVE-2026-25766)"""
    
    def test_get_secure_download_headers(self):
        """Test download security headers"""
        headers = get_secure_download_headers("report.pdf", "application/pdf")
        assert headers['X-Content-Type-Options'] == 'nosniff'
        assert 'Content-Disposition' in headers


# =============================================================================
# Pass 68: API Security Hardening Tests
# =============================================================================

class TestAPISecurity:
    """Test API security hardening (CVE-2026-25544, CVE-2026-1894)"""
    
    def test_validate_api_request_valid(self):
        """Test valid API request"""
        # Should not raise
        validate_api_request("/api/users", "GET", "user123")
    
    def test_validate_api_request_invalid_method(self):
        """Test invalid HTTP method"""
        with pytest.raises(APISecurityError) as exc_info:
            validate_api_request("/api/users", "TRACE")
        assert "not allowed" in str(exc_info.value).lower()
    
    def test_validate_graphql_query_depth(self):
        """Test GraphQL query depth limit"""
        deep_query = "{" * 15 + "field" + "}" * 15
        with pytest.raises(APISecurityError) as exc_info:
            validate_graphql_query(deep_query, max_depth=10)
        assert "depth" in str(exc_info.value).lower()
    
    def test_validate_bulk_operation_within_limit(self):
        """Test bulk operation within limit"""
        # Should not raise
        validate_bulk_operation([1, 2, 3], max_items=100)
    
    def test_validate_bulk_operation_exceeds_limit(self):
        """Test bulk operation exceeding limit"""
        with pytest.raises(APISecurityError) as exc_info:
            validate_bulk_operation([1] * 200, max_items=100)
        assert "exceeds" in str(exc_info.value).lower()


# =============================================================================
# Pass 69: Webhook Security Tests
# =============================================================================

class TestWebhookSecurity:
    """Test webhook security (CVE-2026-27488, CVE-2026-28467)"""
    
    def test_validate_webhook_url_valid_https(self):
        """Test valid HTTPS webhook URL"""
        # Should not raise
        validate_webhook_url("https://example.com/webhook")
    
    def test_validate_webhook_url_http_rejected(self):
        """Test HTTP URL rejection"""
        with pytest.raises(WebhookSecurityError) as exc_info:
            validate_webhook_url("http://example.com/webhook")
        assert "https" in str(exc_info.value).lower()
    
    def test_validate_webhook_url_private_ip(self):
        """Test private IP rejection (CVE-2026-27488)"""
        with pytest.raises(WebhookSecurityError) as exc_info:
            validate_webhook_url("https://192.168.1.1/webhook")
        assert "private" in str(exc_info.value).lower()
    
    def test_validate_webhook_url_localhost(self):
        """Test localhost rejection"""
        with pytest.raises(WebhookSecurityError) as exc_info:
            validate_webhook_url("https://localhost/webhook")
        assert "blocked" in str(exc_info.value).lower()
    
    def test_generate_and_verify_webhook_signature(self):
        """Test webhook signature generation and verification"""
        payload = b'{"event": "test"}'
        secret = "webhook_secret"
        signature = generate_webhook_signature(payload, secret)
        assert verify_webhook_signature(payload, signature, secret) is True
        assert verify_webhook_signature(payload, signature, "wrong_secret") is False


# =============================================================================
# Pass 70: Background Job Security Tests
# =============================================================================

class TestJobSecurity:
    """Test background job security (CVE-2026-25643, CVE-2026-25641)"""
    
    def test_validate_job_payload_valid(self):
        """Test valid job payload"""
        # Should not raise
        validate_job_payload("send_email", {"to": "user@example.com"})
    
    def test_validate_job_payload_invalid_type(self):
        """Test invalid job type"""
        with pytest.raises(JobSecurityError) as exc_info:
            validate_job_payload("malicious_job", {})
        assert "not allowed" in str(exc_info.value).lower()
    
    def test_validate_job_payload_dangerous_pattern(self):
        """Test dangerous pattern detection (CVE-2026-25643)"""
        with pytest.raises(JobSecurityError) as exc_info:
            validate_job_payload("send_email", {"code": "eval('os.system(\"rm -rf /\")')"})
        assert "dangerous pattern" in str(exc_info.value).lower()


# =============================================================================
# Pass 71: Cache Security Tests
# =============================================================================

class TestCacheSecurity:
    """Test cache security (CVE-2026-27897, CVE-2026-2835)"""
    
    def test_sanitize_cache_key_normal(self):
        """Test normal cache key sanitization"""
        result = sanitize_cache_key("user:123:profile")
        assert result == "user:123:profile"
    
    def test_sanitize_cache_key_control_chars(self):
        """Test control character removal"""
        result = sanitize_cache_key("user\x00:123")
        assert "\x00" not in result
    
    def test_sanitize_cache_key_long_key(self):
        """Test long key hashing"""
        long_key = "x" * 300
        result = sanitize_cache_key(long_key)
        assert len(result) <= 64  # SHA-256 hex length
    
    def test_check_sensitive_cache_key(self):
        """Test sensitive cache key detection"""
        with pytest.raises(CacheSecurityError) as exc_info:
            check_sensitive_cache_key("user:password:hash")
        assert "sensitive" in str(exc_info.value).lower()
    
    def test_validate_cache_ttl_normal(self):
        """Test normal TTL validation"""
        result = validate_cache_ttl(3600, max_ttl=86400)
        assert result == 3600
    
    def test_validate_cache_ttl_too_high(self):
        """Test TTL clamping"""
        result = validate_cache_ttl(100000, max_ttl=86400)
        assert result == 86400


# =============================================================================
# Pass 72: Email Security Integration Tests
# =============================================================================

class TestEmailSecurity:
    """Test email security integration (CVE-2026-28289, CVE-2026-24486)"""
    
    def test_sanitize_email_address_valid(self):
        """Test valid email sanitization"""
        result = sanitize_email_address("user@example.com")
        assert result == "user@example.com"
    
    def test_sanitize_email_address_newline(self):
        """Test newline injection detection (CVE-2026-28289)"""
        with pytest.raises(EmailSecurityError) as exc_info:
            sanitize_email_address("user@example.com\nBcc: attacker@evil.com")
        assert "dangerous" in str(exc_info.value).lower()
    
    def test_sanitize_email_address_invalid(self):
        """Test invalid email rejection"""
        with pytest.raises(EmailSecurityError) as exc_info:
            sanitize_email_address("not-an-email")
        assert "invalid" in str(exc_info.value).lower()
    
    def test_sanitize_email_subject(self):
        """Test subject sanitization"""
        result = sanitize_email_subject("Hello\nWorld")
        assert "\n" not in result
    
    def test_validate_email_attachment_dangerous(self):
        """Test dangerous attachment rejection"""
        with pytest.raises(EmailSecurityError) as exc_info:
            validate_email_attachment("malware.exe", "application/octet-stream")
        assert "not allowed" in str(exc_info.value).lower()


# =============================================================================
# Pass 73: Notification Security Tests
# =============================================================================

class TestNotificationSecurity:
    """Test notification security (CVE-2026-30839, CVE-2026-30953)"""
    
    def test_validate_notification_payload_valid(self):
        """Test valid notification payload"""
        # Should not raise
        validate_notification_payload({"title": "Hello", "body": "World"})
    
    def test_validate_notification_payload_url_in_payload(self):
        """Test URL validation in payload (CVE-2026-30839)"""
        with pytest.raises(NotificationSecurityError) as exc_info:
            validate_notification_payload({
                "title": "Test",
                "url": "http://192.168.1.1/internal"
            })
        assert "invalid url" in str(exc_info.value).lower()
    
    def test_sanitize_notification_content_html(self):
        """Test HTML removal from content"""
        result = sanitize_notification_content("<b>Hello</b> World")
        assert "<b>" not in result
    
    def test_sanitize_notification_content_markdown(self):
        """Test markdown link removal"""
        result = sanitize_notification_content("[Click](http://evil.com)")
        assert "http://evil.com" not in result
        assert "Click" in result


# =============================================================================
# Pass 74: Report Generation Security Tests
# =============================================================================

class TestReportSecurity:
    """Test report generation security (CVE-2026-26144, CVE-2026-28794)"""
    
    def test_sanitize_csv_field_formula_injection(self):
        """Test CSV formula injection prevention (CVE-2026-26144)"""
        result = sanitize_csv_field("=SUM(A1:A10)")
        assert result.startswith("'")
    
    def test_sanitize_csv_field_plus_prefix(self):
        """Test plus prefix sanitization"""
        result = sanitize_csv_field("+cmd|' /C calc'!A0")
        assert result.startswith("'")
    
    def test_generate_secure_csv(self):
        """Test secure CSV generation"""
        rows = [{"name": "John", "value": "=SUM(1+1)"}]
        result = generate_secure_csv(rows, headers=["name", "value"])
        assert "=SUM" not in result or "'=SUM" in result
    
    def test_validate_report_access_admin(self):
        """Test admin report access"""
        # Should not raise
        validate_report_access("financial", ROLE_ADMIN)
    
    def test_validate_report_access_unauthorized(self):
        """Test unauthorized report access"""
        with pytest.raises(ReportSecurityError) as exc_info:
            validate_report_access("financial", ROLE_MEMBER, 
                                   allowed_types=["basic"])
        assert "not allowed" in str(exc_info.value).lower()


# =============================================================================
# Pass 75: Data Export Security Tests
# =============================================================================

class TestExportSecurity:
    """Test data export security (CVE-2026-21536, CVE-2026-27897)"""
    
    def test_validate_export_request_valid(self):
        """Test valid export request"""
        # Should not raise
        validate_export_request("csv", "user_data", ROLE_MEMBER)
    
    def test_validate_export_request_invalid_format(self):
        """Test invalid export format"""
        with pytest.raises(ExportSecurityError) as exc_info:
            validate_export_request("exe", "user_data", ROLE_MEMBER)
        assert "not allowed" in str(exc_info.value).lower()
    
    def test_validate_export_request_admin_scope(self):
        """Test admin scope restriction (CVE-2026-27897)"""
        with pytest.raises(ExportSecurityError) as exc_info:
            validate_export_request("csv", "all", ROLE_MEMBER)
        assert "only admins" in str(exc_info.value).lower()
    
    def test_mask_sensitive_export_data(self):
        """Test sensitive data masking"""
        data = {"name": "John", "password": "secret123", "ssn": "123-45-6789"}
        result = mask_sensitive_export_data(data)
        assert result["password"] == "***REDACTED***"
        assert result["ssn"] == "***REDACTED***"
        assert result["name"] == "John"


# =============================================================================
# Pass 76: Admin Panel Security Tests
# =============================================================================

class TestAdminSecurity:
    """Test admin panel security (CVE-2026-1731, CVE-2026-22769)"""
    
    def test_validate_admin_action_as_admin(self):
        """Test admin action as admin"""
        # Should not raise
        validate_admin_action("create_user", ROLE_ADMIN)
    
    def test_validate_admin_action_as_non_admin(self):
        """Test admin action as non-admin"""
        with pytest.raises(AdminSecurityError) as exc_info:
            validate_admin_action("create_user", ROLE_MEMBER)
        assert "admin privileges" in str(exc_info.value).lower()
    
    def test_check_admin_ip_restriction_allowed(self):
        """Test allowed admin IP"""
        # Should not raise
        check_admin_ip_restriction("192.168.1.100", ["192.168.1."])
    
    def test_check_admin_ip_restriction_blocked(self):
        """Test blocked admin IP"""
        with pytest.raises(AdminSecurityError) as exc_info:
            check_admin_ip_restriction("10.0.0.1", ["192.168.1."])
        assert "not allowed" in str(exc_info.value).lower()


# =============================================================================
# Pass 77: Audit Logging Integration Tests
# =============================================================================

class TestAuditLogging:
    """Test audit logging integration (CVE-2026-3494, CVE-2026-30928)"""
    
    def test_should_audit_action_sensitive(self):
        """Test sensitive action detection"""
        assert should_audit_action("login") is True
        assert should_audit_action("password_change") is True
    
    def test_should_audit_action_data_modification(self):
        """Test data modification detection"""
        assert should_audit_action("create", "user") is True
        assert should_audit_action("delete", "post") is True
    
    def test_should_audit_action_normal(self):
        """Test normal action (not audited)"""
        assert should_audit_action("view", "page") is False
    
    def test_create_audit_event(self):
        """Test audit event creation"""
        event = create_audit_event("login", "user123", 
                                   resource_type="session",
                                   ip_address="192.168.1.1")
        assert event['action'] == "login"
        assert event['user'] == "user123"
        assert event['ip_address'] == "192.168.1.1"
        assert 'integrity_hash' in event


# =============================================================================
# Pass 78: Configuration Security Integration Tests
# =============================================================================

class TestConfigSecurity:
    """Test configuration security integration (CVE-2026-25253, CVE-2026-25643)"""
    
    def test_validate_runtime_config_change_as_admin(self):
        """Test config change as admin"""
        # Should not raise
        validate_runtime_config_change("app.name", "MyApp", ROLE_ADMIN)
    
    def test_validate_runtime_config_change_as_non_admin(self):
        """Test config change as non-admin"""
        with pytest.raises(ConfigIntegrationError) as exc_info:
            validate_runtime_config_change("app.name", "MyApp", ROLE_MEMBER)
        assert "admin privileges" in str(exc_info.value).lower()
    
    def test_validate_runtime_config_change_short_secret(self):
        """Test short secret rejection (CVE-2026-25253)"""
        with pytest.raises(ConfigIntegrationError) as exc_info:
            validate_runtime_config_change("api.secret", "short", ROLE_ADMIN)
        assert "at least 8 characters" in str(exc_info.value).lower()
    
    def test_sanitize_config_value_command_injection(self):
        """Test command injection detection (CVE-2026-25643)"""
        with pytest.raises(ConfigIntegrationError) as exc_info:
            sanitize_config_value("exec.command", "rm -rf /; ls")
        assert "dangerous character" in str(exc_info.value).lower()


# =============================================================================
# Pass 79: Security Monitoring Integration Tests
# =============================================================================

class TestSecurityMonitoring:
    """Test security monitoring integration (CVE-2026-1709, CVE-2026-1568)"""
    
    def test_generate_security_event(self):
        """Test security event generation"""
        event = generate_security_event('auth_failure', 
                                        source_ip='192.168.1.1',
                                        user_id='user123')
        assert event['type'] == 'auth_failure'
        assert event['severity'] == 'warning'
        assert event['source_ip'] == '192.168.1.1'
    
    def test_generate_security_event_unknown_type(self):
        """Test unknown event type rejection"""
        with pytest.raises(SecurityMonitoringError):
            generate_security_event('unknown_event')
    
    def test_check_anomaly_threshold_exceeded(self):
        """Test anomaly threshold detection"""
        result = check_anomaly_threshold('auth_failure', count=10, window_seconds=300)
        assert result is True  # Exceeds threshold of 5
    
    def test_check_anomaly_threshold_not_exceeded(self):
        """Test anomaly threshold not exceeded"""
        result = check_anomaly_threshold('auth_failure', count=3, window_seconds=300)
        assert result is False  # Below threshold


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
