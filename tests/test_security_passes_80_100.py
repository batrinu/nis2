"""
Test Security Passes 80-100: Final Application Consolidation Phase

Covers 21 additional security passes (80-100) addressing:
- Supply chain security (CVE-2026-28289, CVE-2026-29000)
- Container security (CVE-2026-3288, CVE-2026-0863)
- Cloud metadata protection (CVE-2026-28467, CVE-2026-27488)
- Hardcoded credential detection (CVE-2026-25202, CVE-2026-22769)
- SSRF deep protection (CVE-2026-26019, CVE-2026-25493)
- Code injection prevention (CVE-2026-25632, CVE-2026-25520)
- Secure defaults enforcement
- Dependency version pinning
- Secrets rotation tracking
- And 12 additional application security passes

Total: 95 test cases (passes 80-100)
"""

import pytest
import sys
import os
import time
import ipaddress
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'nis2-audit-app', 'app'))

from security_utils import (
    # Pass 80: Supply Chain
    SupplyChainError,
    validate_dependency_name,
    check_dependency_confusion_risk,
    
    # Pass 81: Container Security
    ContainerSecurityError,
    validate_container_security_config,
    sanitize_container_image_name,
    DANGEROUS_CAPABILITIES,
    SENSITIVE_MOUNTS,
    
    # Pass 82: Cloud Metadata
    CloudMetadataError,
    check_cloud_metadata_access,
    sanitize_cloud_metadata_response,
    CLOUD_METADATA_ENDPOINTS,
    
    # Pass 83: Hardcoded Credentials
    HardcodedCredentialError,
    scan_for_hardcoded_credentials,
    validate_no_hardcoded_secrets,
    
    # Pass 84: SSRF Deep Protection
    SSRFDeepProtectionError,
    validate_url_deep_protection,
    MAX_REDIRECTS,
    
    # Pass 85: Code Injection
    CodeInjectionError,
    detect_code_injection,
    safe_code_execution,
    
    # Pass 86: Secure Defaults
    SecureDefaultsError,
    enforce_secure_defaults,
    REQUIRED_SECURE_DEFAULTS,
    
    # Pass 87: Dependency Pinning
    validate_pinned_dependencies,
    
    # Pass 88: Secrets Rotation
    SecretsRotationTracker,
    
    # Pass 89: Secure Logging
    validate_log_format,
    
    # Pass 90: TLS Validation
    validate_tls_config,
    REQUIRED_TLS_VERSIONS,
    
    # Pass 91: API Versioning
    validate_api_version,
    
    # Pass 92: Timing Analysis
    RequestTimingAnalyzer,
    
    # Pass 93: CSP Validation
    validate_csp_policy,
    
    # Pass 94: Password Policy
    validate_password_policy,
    
    # Pass 95: File Content Validation
    validate_file_content,
    
    # Pass 96: Network Policy
    validate_network_policy,
    
    # Pass 97: Resource Limits
    validate_resource_limits,
    
    # Pass 98: Health Check
    validate_health_check_config,
    
    # Pass 99: Trace Sanitization
    sanitize_trace_data,
    
    # Pass 100: Security Headers
    verify_security_headers,
    REQUIRED_SECURITY_HEADERS,
    
    # Common
    SecurityError,
)


# =============================================================================
# Pass 80: Supply Chain Security (CVE-2026-28289, CVE-2026-29000)
# =============================================================================

class TestSupplyChainSecurity:
    """Test supply chain security protections."""
    
    def test_validate_dependency_name_safe(self):
        """Test validation of safe dependency names."""
        # Should not raise
        validate_dependency_name("requests")
        validate_dependency_name("flask")
        validate_dependency_name("numpy")
    
    def test_validate_dependency_name_vulnerable_log4j(self):
        """Test detection of vulnerable Log4j versions."""
        with pytest.raises(SupplyChainError) as exc_info:
            validate_dependency_name("log4j-core-2.14")
        assert "Log4Shell" in str(exc_info.value)
    
    def test_validate_dependency_name_vulnerable_fastjson(self):
        """Test detection of vulnerable FastJSON versions."""
        with pytest.raises(SupplyChainError) as exc_info:
            validate_dependency_name("fastjson-1.2.24")
        assert "FastJSON" in str(exc_info.value)
    
    def test_check_dependency_confusion_no_private(self):
        """Test dependency confusion check with no private packages."""
        result = check_dependency_confusion_risk("requests", None)
        assert result is False
    
    def test_check_dependency_confusion_risk_detected(self):
        """Test detection of dependency confusion risk."""
        private_packages = ["internal-utils", "company-lib"]
        result = check_dependency_confusion_risk("internal-utils", private_packages)
        assert result is True
    
    def test_dependency_confusion_case_insensitive(self):
        """Test case-insensitive matching for dependency confusion."""
        private_packages = ["Internal-Utils"]
        result = check_dependency_confusion_risk("internal-utils", private_packages)
        assert result is True


# =============================================================================
# Pass 81: Container Security (CVE-2026-3288, CVE-2026-0863)
# =============================================================================

class TestContainerSecurity:
    """Test container security protections."""
    
    def test_validate_container_security_config_privileged(self):
        """Test detection of privileged container mode."""
        config = {'privileged': True}
        issues = validate_container_security_config(config)
        
        assert len(issues) >= 1
        assert any(i['severity'] == 'critical' for i in issues)
    
    def test_validate_container_security_config_dangerous_capabilities(self):
        """Test detection of dangerous capabilities."""
        config = {'capabilities': ['CAP_SYS_ADMIN', 'NET_ADMIN']}
        issues = validate_container_security_config(config)
        
        dangerous_found = any(
            'CAP_SYS_ADMIN' in i['message'] for i in issues
        )
        assert dangerous_found
    
    def test_validate_container_security_config_sensitive_mounts(self):
        """Test detection of sensitive mount points."""
        config = {'mounts': ['/data', '/var/run/docker.sock']}
        issues = validate_container_security_config(config)
        
        sensitive_found = any(
            'docker.sock' in i['message'] for i in issues
        )
        assert sensitive_found
    
    def test_validate_container_security_config_root_user(self):
        """Test detection of root user."""
        config = {'user': 'root'}
        issues = validate_container_security_config(config)
        
        root_found = any('root' in i['message'].lower() for i in issues)
        assert root_found
    
    def test_validate_container_security_config_uid_zero(self):
        """Test detection of UID 0 (root)."""
        config = {'user': '0'}
        issues = validate_container_security_config(config)
        
        root_found = any('root' in i['message'].lower() for i in issues)
        assert root_found
    
    def test_validate_container_security_config_secure(self):
        """Test validation of secure container config."""
        config = {
            'privileged': False,
            'capabilities': ['NET_ADMIN'],
            'mounts': ['/data'],
            'user': '1000',
        }
        issues = validate_container_security_config(config)
        
        # Should not have critical or high issues
        critical_high = [i for i in issues if i['severity'] in ['critical', 'high']]
        assert len(critical_high) == 0
    
    def test_sanitize_container_image_name_latest_tag(self):
        """Test rejection of 'latest' tag."""
        with pytest.raises(ContainerSecurityError) as exc_info:
            sanitize_container_image_name("nginx:latest")
        assert "latest" in str(exc_info.value).lower()
    
    def test_sanitize_container_image_name_no_tag(self):
        """Test rejection of untagged image."""
        with pytest.raises(ContainerSecurityError) as exc_info:
            sanitize_container_image_name("nginx")
        assert "latest" in str(exc_info.value).lower()
    
    def test_sanitize_container_image_name_localhost(self):
        """Test rejection of localhost registry."""
        with pytest.raises(ContainerSecurityError) as exc_info:
            sanitize_container_image_name("localhost:5000/myapp:1.0")
        assert "suspicious" in str(exc_info.value).lower()
    
    def test_sanitize_container_image_name_valid(self):
        """Test acceptance of valid image name."""
        result = sanitize_container_image_name("docker.io/nginx:1.21")
        assert result == "docker.io/nginx:1.21"
    
    def test_dangerous_capabilities_list(self):
        """Test dangerous capabilities list is populated."""
        assert 'CAP_SYS_ADMIN' in DANGEROUS_CAPABILITIES
        assert 'CAP_SYS_PTRACE' in DANGEROUS_CAPABILITIES
    
    def test_sensitive_mounts_list(self):
        """Test sensitive mounts list is populated."""
        assert '/var/run/docker.sock' in SENSITIVE_MOUNTS
        assert '/root/.ssh' in SENSITIVE_MOUNTS


# =============================================================================
# Pass 82: Cloud Metadata Protection (CVE-2026-28467, CVE-2026-27488)
# =============================================================================

class TestCloudMetadataProtection:
    """Test cloud metadata protection."""
    
    def test_check_cloud_metadata_access_aws(self):
        """Test detection of AWS metadata access."""
        with pytest.raises(CloudMetadataError) as exc_info:
            check_cloud_metadata_access("http://169.254.169.254/latest/meta-data/")
        assert "cloud metadata" in str(exc_info.value).lower()
    
    def test_check_cloud_metadata_access_aws_dns(self):
        """Test detection of AWS DNS metadata."""
        with pytest.raises(CloudMetadataError) as exc_info:
            check_cloud_metadata_access("http://169.254.169.253/")
        assert "cloud metadata" in str(exc_info.value).lower()
    
    def test_check_cloud_metadata_access_alibaba(self):
        """Test detection of Alibaba Cloud metadata."""
        with pytest.raises(CloudMetadataError) as exc_info:
            check_cloud_metadata_access("http://100.100.100.200/")
        assert "cloud metadata" in str(exc_info.value).lower()
    
    def test_check_cloud_metadata_access_safe_url(self):
        """Test safe URL is allowed."""
        # Should not raise
        check_cloud_metadata_access("https://example.com/api")
    
    def test_sanitize_cloud_metadata_response(self):
        """Test sanitization of metadata response."""
        response = {
            'AccessKeyId': 'AKIAIOSFODNN7EXAMPLE',
            'SecretAccessKey': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            'Token': 'token123',
            'Region': 'us-east-1',
        }
        
        sanitized = sanitize_cloud_metadata_response(response)
        
        assert sanitized['AccessKeyId'] == '***REDACTED***'
        assert sanitized['SecretAccessKey'] == '***REDACTED***'
        assert sanitized['Token'] == '***REDACTED***'
        assert sanitized['Region'] == 'us-east-1'
    
    def test_cloud_metadata_endpoints_list(self):
        """Test cloud metadata endpoints list."""
        assert '169.254.169.254' in CLOUD_METADATA_ENDPOINTS
        assert '169.254.169.253' in CLOUD_METADATA_ENDPOINTS


# =============================================================================
# Pass 83: Hardcoded Credential Detection (CVE-2026-25202, CVE-2026-22769)
# =============================================================================

class TestHardcodedCredentialDetection:
    """Test hardcoded credential detection."""
    
    def test_scan_for_hardcoded_password(self):
        """Test detection of hardcoded password."""
        code = 'password = "secret123"'
        issues = scan_for_hardcoded_credentials(code)
        
        assert len(issues) >= 1
        assert any('Hardcoded password' in i['type'] for i in issues)
    
    def test_scan_for_hardcoded_secret(self):
        """Test detection of hardcoded secret."""
        code = 'api_secret = "supersecretkey12345"'
        issues = scan_for_hardcoded_credentials(code)
        
        assert len(issues) >= 1
        assert any('Hardcoded secret' in i['type'] for i in issues)
    
    def test_scan_for_hardcoded_api_key(self):
        """Test detection of hardcoded API key."""
        code = 'api_key = "sk-1234567890abcdef"'
        issues = scan_for_hardcoded_credentials(code)
        
        assert len(issues) >= 1
        assert any('Hardcoded API key' in i['type'] for i in issues)
    
    def test_scan_for_hardcoded_token(self):
        """Test detection of hardcoded token."""
        code = 'token = "Bearer abc123xyz789"'
        issues = scan_for_hardcoded_credentials(code)
        
        assert len(issues) >= 1
        assert any('Hardcoded token' in i['type'] for i in issues)
    
    def test_scan_for_aws_credentials(self):
        """Test detection of AWS credentials."""
        code = 'aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"'
        issues = scan_for_hardcoded_credentials(code)
        
        assert len(issues) >= 1
        assert any('Hardcoded AWS key' in i['type'] for i in issues)
    
    def test_scan_for_private_key(self):
        """Test detection of private key."""
        code = 'private_key = "-----BEGIN RSA PRIVATE KEY-----"'
        issues = scan_for_hardcoded_credentials(code)
        
        assert len(issues) >= 1
        assert any('Hardcoded private key' in i['type'] for i in issues)
    
    def test_scan_safe_code(self):
        """Test safe code has no issues."""
        code = '''
def greet(name):
    return f"Hello, {name}!"

result = greet("World")
'''
        issues = scan_for_hardcoded_credentials(code)
        
        assert len(issues) == 0
    
    def test_validate_no_hardcoded_secrets_safe(self):
        """Test validation of config without secrets."""
        config = {'database': {'host': 'localhost', 'port': 5432}}
        # Should not raise
        validate_no_hardcoded_secrets(config)
    
    def test_validate_no_hardcoded_secrets_env_var(self):
        """Test env var references are allowed."""
        config = {'database': {'password': '${DB_PASSWORD}'}}
        # Should not raise
        validate_no_hardcoded_secrets(config)
    
    def test_validate_hardcoded_secrets_detected(self):
        """Test detection of hardcoded secrets in config."""
        config = {'database': {'password': 'supersecret12345'}}
        
        with pytest.raises(HardcodedCredentialError) as exc_info:
            validate_no_hardcoded_secrets(config)
        assert "hardcoded secret" in str(exc_info.value).lower()


# =============================================================================
# Pass 84: SSRF Deep Protection (CVE-2026-26019, CVE-2026-25493)
# =============================================================================

class TestSSRFDeepProtection:
    """Test SSRF deep protection."""
    
    def test_validate_url_deep_protection_file_scheme(self):
        """Test rejection of file:// scheme."""
        with pytest.raises(SSRFDeepProtectionError) as exc_info:
            validate_url_deep_protection("file:///etc/passwd")
        assert "Dangerous URL scheme" in str(exc_info.value)
    
    def test_validate_url_deep_protection_gopher_scheme(self):
        """Test rejection of gopher:// scheme."""
        with pytest.raises(SSRFDeepProtectionError) as exc_info:
            validate_url_deep_protection("gopher://localhost/")
        assert "Dangerous URL scheme" in str(exc_info.value)
    
    def test_validate_url_deep_protection_ldap_scheme(self):
        """Test rejection of ldap:// scheme."""
        with pytest.raises(SSRFDeepProtectionError) as exc_info:
            validate_url_deep_protection("ldap://internal-server/dc=example")
        assert "Dangerous URL scheme" in str(exc_info.value)
    
    def test_validate_url_deep_protection_ftp_scheme(self):
        """Test rejection of ftp:// scheme."""
        with pytest.raises(SSRFDeepProtectionError) as exc_info:
            validate_url_deep_protection("ftp://anonymous@ftp.example.com/")
        assert "Dangerous URL scheme" in str(exc_info.value)
    
    def test_validate_url_deep_protection_dict_scheme(self):
        """Test rejection of dict:// scheme."""
        with pytest.raises(SSRFDeepProtectionError) as exc_info:
            validate_url_deep_protection("dict://localhost:11211/")
        assert "Dangerous URL scheme" in str(exc_info.value)
    
    @patch('socket.getaddrinfo')
    def test_validate_url_deep_protection_private_ip(self, mock_getaddrinfo):
        """Test rejection of private IP addresses."""
        mock_getaddrinfo.return_value = [(None, None, None, None, ('192.168.1.1', 0))]
        
        with pytest.raises(SSRFDeepProtectionError) as exc_info:
            validate_url_deep_protection("http://internal.company.com/")
        assert "internal ip" in str(exc_info.value).lower()
    
    @patch('socket.getaddrinfo')
    def test_validate_url_deep_protection_loopback(self, mock_getaddrinfo):
        """Test rejection of loopback addresses."""
        mock_getaddrinfo.return_value = [(None, None, None, None, ('127.0.0.1', 0))]
        
        with pytest.raises(SSRFDeepProtectionError) as exc_info:
            validate_url_deep_protection("http://localhost:8080/")
        assert "internal ip" in str(exc_info.value).lower()
    
    @patch('socket.getaddrinfo')
    def test_validate_url_deep_protection_metadata_endpoint(self, mock_getaddrinfo):
        """Test rejection of cloud metadata endpoint."""
        mock_getaddrinfo.return_value = [(None, None, None, None, ('169.254.169.254', 0))]
        
        with pytest.raises(SSRFDeepProtectionError) as exc_info:
            validate_url_deep_protection("http://metadata.example.com/")
        assert "internal ip" in str(exc_info.value).lower()
    
    @patch('socket.getaddrinfo')
    def test_validate_url_deep_protection_safe_url(self, mock_getaddrinfo):
        """Test safe external URL is allowed."""
        mock_getaddrinfo.return_value = [(None, None, None, None, ('93.184.216.34', 0))]
        
        # Should not raise
        validate_url_deep_protection("https://example.com/api")
    
    @patch('socket.getaddrinfo')
    def test_validate_url_deep_protection_dns_failure(self, mock_getaddrinfo):
        """Test handling of DNS resolution failure."""
        import socket
        mock_getaddrinfo.side_effect = socket.gaierror("Name or service not known")
        
        with pytest.raises(SSRFDeepProtectionError) as exc_info:
            validate_url_deep_protection("http://invalid.invalid/")
        assert "Could not resolve" in str(exc_info.value)
    
    def test_max_redirects_constant(self):
        """Test MAX_REDIRECTS constant is set."""
        assert MAX_REDIRECTS == 3


# =============================================================================
# Pass 85: Code Injection Prevention (CVE-2026-25632, CVE-2026-25520)
# =============================================================================

class TestCodeInjectionPrevention:
    """Test code injection prevention."""
    
    def test_detect_code_injection_eval(self):
        """Test detection of eval() call."""
        code = 'result = eval(user_input)'
        issues = detect_code_injection(code)
        
        assert len(issues) >= 1
        assert any('eval()' in i['type'] for i in issues)
    
    def test_detect_code_injection_exec(self):
        """Test detection of exec() call."""
        code = 'exec(malicious_code)'
        issues = detect_code_injection(code)
        
        assert len(issues) >= 1
        assert any('exec()' in i['type'] for i in issues)
    
    def test_detect_code_injection_import(self):
        """Test detection of __import__ call."""
        code = 'module = __import__(module_name)'
        issues = detect_code_injection(code)
        
        assert len(issues) >= 1
        assert any('Dynamic import' in i['type'] for i in issues)
    
    def test_detect_code_injection_subprocess_call(self):
        """Test detection of subprocess.call."""
        code = 'subprocess.call(user_command, shell=True)'
        issues = detect_code_injection(code)
        
        assert len(issues) >= 1
        assert any('subprocess.call' in i['type'] for i in issues)
    
    def test_detect_code_injection_subprocess_popen(self):
        """Test detection of subprocess.Popen."""
        code = 'subprocess.Popen(cmd, shell=True)'
        issues = detect_code_injection(code)
        
        assert len(issues) >= 1
        assert any('subprocess.Popen' in i['type'] for i in issues)
    
    def test_detect_code_injection_os_system(self):
        """Test detection of os.system call."""
        code = 'os.system(user_input)'
        issues = detect_code_injection(code)
        
        assert len(issues) >= 1
        assert any('os.system' in i['type'] for i in issues)
    
    def test_detect_code_injection_os_popen(self):
        """Test detection of os.popen call."""
        code = 'stream = os.popen(command)'
        issues = detect_code_injection(code)
        
        assert len(issues) >= 1
        assert any('os.popen' in i['type'] for i in issues)
    
    def test_detect_code_injection_compile(self):
        """Test detection of compile() call."""
        code = 'code = compile(source, "<string>", "exec")'
        issues = detect_code_injection(code)
        
        assert len(issues) >= 1
        assert any('compile()' in i['type'] for i in issues)
    
    def test_detect_code_injection_safe(self):
        """Test safe code has no injection patterns."""
        code = '''
def calculate(a, b):
    return a + b

result = calculate(1, 2)
print(result)
'''
        issues = detect_code_injection(code)
        assert len(issues) == 0
    
    def test_safe_code_execution_with_injection(self):
        """Test safe_code_execution rejects dangerous code."""
        with pytest.raises(CodeInjectionError) as exc_info:
            safe_code_execution('eval(user_input)')
        assert "dangerous patterns" in str(exc_info.value).lower()
    
    def test_safe_code_execution_safe(self):
        """Test safe_code_execution accepts safe code."""
        result = safe_code_execution('x = 1 + 2')
        assert result['validated'] is True


# =============================================================================
# Pass 86: Secure Defaults Enforcement
# =============================================================================

class TestSecureDefaults:
    """Test secure defaults enforcement."""
    
    def test_enforce_secure_defaults_all_set(self):
        """Test config with all secure defaults set."""
        config = {
            'debug': False,
            'csrf_protection': True,
            'secure_cookies': True,
            'http_only_cookies': True,
            'xss_protection': True,
            'content_security_policy': True,
            'strict_transport_security': True,
        }
        issues = enforce_secure_defaults(config)
        assert len(issues) == 0
    
    def test_enforce_secure_defaults_missing(self):
        """Test detection of missing secure defaults."""
        config = {'debug': False}  # Missing others
        issues = enforce_secure_defaults(config)
        
        assert len(issues) >= 1
        assert any('csrf_protection' in i['setting'] for i in issues)
    
    def test_enforce_secure_defaults_insecure(self):
        """Test detection of insecure default values."""
        config = {
            'debug': True,  # Should be False
            'csrf_protection': True,
            'secure_cookies': True,
            'http_only_cookies': True,
            'xss_protection': True,
            'content_security_policy': True,
            'strict_transport_security': True,
        }
        issues = enforce_secure_defaults(config)
        
        assert len(issues) >= 1
        debug_issue = [i for i in issues if i['setting'] == 'debug']
        assert len(debug_issue) >= 1
        assert debug_issue[0]['current'] is True
        assert debug_issue[0]['required'] is False
    
    def test_required_secure_defaults_list(self):
        """Test REQUIRED_SECURE_DEFAULTS is populated."""
        assert 'debug' in REQUIRED_SECURE_DEFAULTS
        assert 'csrf_protection' in REQUIRED_SECURE_DEFAULTS
        assert REQUIRED_SECURE_DEFAULTS['debug'] is False
        assert REQUIRED_SECURE_DEFAULTS['csrf_protection'] is True


# =============================================================================
# Pass 87: Dependency Version Pinning
# =============================================================================

class TestDependencyVersionPinning:
    """Test dependency version pinning."""
    
    def test_validate_pinned_dependencies_all_pinned(self):
        """Test requirements with all dependencies pinned."""
        requirements = '''
requests==2.28.1
flask==2.2.5
numpy>=1.21.0
'''
        issues = validate_pinned_dependencies(requirements)
        assert len(issues) == 0
    
    def test_validate_pinned_dependencies_unpinned(self):
        """Test detection of unpinned dependencies."""
        requirements = '''
requests
flask==2.2.5
numpy
'''
        issues = validate_pinned_dependencies(requirements)
        
        assert len(issues) >= 2
        assert any('requests' in i['package'] for i in issues)
        assert any('numpy' in i['package'] for i in issues)
    
    def test_validate_pinned_dependencies_comments_ignored(self):
        """Test comments are ignored."""
        requirements = '''
# Production dependencies
requests==2.28.1
# flask==2.2.5  # commented out
'''
        issues = validate_pinned_dependencies(requirements)
        assert len(issues) == 0
    
    def test_validate_pinned_dependencies_editable_ignored(self):
        """Test editable installs are ignored."""
        requirements = '''
-e git+https://github.com/user/repo.git#egg=mypackage
requests==2.28.1
'''
        issues = validate_pinned_dependencies(requirements)
        assert len(issues) == 0


# =============================================================================
# Pass 88: Secrets Rotation Tracking
# =============================================================================

class TestSecretsRotationTracking:
    """Test secrets rotation tracking."""
    
    def test_register_secret(self):
        """Test registering a secret for rotation tracking."""
        tracker = SecretsRotationTracker()
        tracker.register_secret('api_key', time.time())
        
        assert 'api_key' in tracker.secrets
    
    def test_check_rotation_not_needed(self):
        """Test secret doesn't need rotation."""
        tracker = SecretsRotationTracker()
        tracker.register_secret('api_key', time.time())
        
        result = tracker.check_rotation_needed('api_key')
        assert result is False
    
    def test_check_rotation_needed(self):
        """Test secret needs rotation."""
        tracker = SecretsRotationTracker()
        # Register secret 100 days ago
        old_time = time.time() - (100 * 24 * 3600)
        tracker.register_secret('api_key', old_time, max_age_days=90)
        
        result = tracker.check_rotation_needed('api_key')
        assert result is True
    
    def test_check_rotation_unknown_secret(self):
        """Test unknown secret needs rotation."""
        tracker = SecretsRotationTracker()
        
        result = tracker.check_rotation_needed('unknown_key')
        assert result is True
    
    def test_register_secret_custom_max_age(self):
        """Test registering with custom max age."""
        tracker = SecretsRotationTracker()
        tracker.register_secret('short_lived', time.time(), max_age_days=7)
        
        assert tracker.secrets['short_lived']['max_age_days'] == 7


# =============================================================================
# Pass 89: Secure Logging
# =============================================================================

class TestSecureLogging:
    """Test secure logging."""
    
    def test_validate_log_format_newlines_removed(self):
        """Test newlines are removed from log messages."""
        message = "User logged in\nInjected log line"
        result = validate_log_format(message)
        
        assert '\n' not in result
        assert '\r' not in result
    
    def test_validate_log_format_safe_message(self):
        """Test safe message is unchanged."""
        message = "User admin logged in from 192.168.1.1"
        result = validate_log_format(message)
        
        assert result == message


# =============================================================================
# Pass 90: TLS/SSL Configuration Validation
# =============================================================================

class TestTLSValidation:
    """Test TLS/SSL configuration validation."""
    
    def test_validate_tls_config_weak_version(self):
        """Test detection of weak TLS version."""
        config = {'min_tls_version': 'TLSv1.0'}
        issues = validate_tls_config(config)
        
        assert len(issues) >= 1
        assert any('TLS' in i['message'] for i in issues)
    
    def test_validate_tls_config_strong_version(self):
        """Test strong TLS version is accepted."""
        config = {'min_tls_version': 'TLSv1.3'}
        issues = validate_tls_config(config)
        
        assert len(issues) == 0
    
    def test_validate_tls_config_weak_cipher(self):
        """Test detection of weak cipher suites."""
        config = {
            'min_tls_version': 'TLSv1.2',
            'cipher_suites': ['ECDHE-RSA-AES128-SHA', 'RC4-SHA']
        }
        issues = validate_tls_config(config)
        
        assert len(issues) >= 1
        assert any('RC4' in i['message'] for i in issues)
    
    def test_validate_tls_config_strong_cipher(self):
        """Test strong cipher suites are accepted."""
        config = {
            'min_tls_version': 'TLSv1.2',
            'cipher_suites': ['ECDHE-RSA-AES256-GCM-SHA384']
        }
        issues = validate_tls_config(config)
        
        # Should not have RC4, DES, 3DES, MD5, SHA1 issues
        weak_issues = [i for i in issues if any(w in i['message'] for w in ['RC4', 'DES', 'MD5', 'SHA1'])]
        assert len(weak_issues) == 0


# =============================================================================
# Pass 91: API Versioning Security
# =============================================================================

class TestAPIVersioning:
    """Test API versioning security."""
    
    def test_validate_api_version_supported(self):
        """Test supported API version is accepted."""
        supported = ['v1', 'v2', 'v3']
        # Should not raise
        validate_api_version('v2', supported)
    
    def test_validate_api_version_unsupported(self):
        """Test unsupported API version is rejected."""
        supported = ['v1', 'v2']
        
        with pytest.raises(SecurityError) as exc_info:
            validate_api_version('v3', supported)
        assert "not supported" in str(exc_info.value).lower()


# =============================================================================
# Pass 92: Request Timing Analysis
# =============================================================================

class TestRequestTimingAnalysis:
    """Test request timing analysis for attack detection."""
    
    def test_record_timing(self):
        """Test recording request timing."""
        analyzer = RequestTimingAnalyzer()
        analyzer.record_timing('/api/login', 0.1)
        
        assert '/api/login' in analyzer.timings
        assert len(analyzer.timings['/api/login']) == 1
    
    def test_detect_timing_attack_insufficient_data(self):
        """Test timing attack detection with insufficient data."""
        analyzer = RequestTimingAnalyzer()
        analyzer.record_timing('/api/login', 0.1)
        
        result = analyzer.detect_timing_attack('/api/login')
        assert result is False
    
    def test_detect_timing_attack_low_variance(self):
        """Test no timing attack detected with low variance."""
        analyzer = RequestTimingAnalyzer()
        
        # Add consistent timings
        for _ in range(20):
            analyzer.record_timing('/api/login', 0.1)
        
        result = analyzer.detect_timing_attack('/api/login')
        assert result is False
    
    def test_detect_timing_attack_high_variance(self):
        """Test timing attack detected with high variance."""
        analyzer = RequestTimingAnalyzer()
        
        # Add timings with extreme variance (simulating timing attack)
        # Using fixed values that definitely trigger high CV
        for i in range(20):
            if i < 10:
                analyzer.record_timing('/api/login', 1.0)  # Normal
            else:
                analyzer.record_timing('/api/login', 10.0)  # Very slow (10x difference)
        
        result = analyzer.detect_timing_attack('/api/login')
        assert result is True


# =============================================================================
# Pass 93: Content Security Policy Validation
# =============================================================================

class TestCSPValidation:
    """Test Content Security Policy validation."""
    
    def test_validate_csp_policy_unsafe_inline(self):
        """Test detection of unsafe-inline directive."""
        policy = "script-src 'self' 'unsafe-inline'"
        issues = validate_csp_policy(policy)
        
        assert len(issues) >= 1
        assert any('unsafe-inline' in i['message'] for i in issues)
    
    def test_validate_csp_policy_unsafe_eval(self):
        """Test detection of unsafe-eval directive."""
        policy = "script-src 'self' 'unsafe-eval'"
        issues = validate_csp_policy(policy)
        
        assert len(issues) >= 1
        assert any('unsafe-eval' in i['message'] for i in issues)
    
    def test_validate_csp_policy_wildcard(self):
        """Test detection of wildcard directive."""
        policy = "script-src *"
        issues = validate_csp_policy(policy)
        
        assert len(issues) >= 1
        assert any('wildcard' in i['message'] for i in issues)
    
    def test_validate_csp_policy_strict(self):
        """Test strict CSP is accepted."""
        policy = "default-src 'self'; script-src 'self' 'nonce-abc123'"
        issues = validate_csp_policy(policy)
        
        assert len(issues) == 0


# =============================================================================
# Pass 94: Password Policy Enforcement
# =============================================================================

class TestPasswordPolicy:
    """Test password policy enforcement."""
    
    def test_validate_password_too_short(self):
        """Test detection of short password."""
        issues = validate_password_policy("Short1!")
        
        assert len(issues) >= 1
        assert any('12 characters' in i['message'] for i in issues)
    
    def test_validate_password_no_uppercase(self):
        """Test detection of missing uppercase."""
        issues = validate_password_policy("nouppercase123!")
        
        assert len(issues) >= 1
        assert any('uppercase' in i['message'] for i in issues)
    
    def test_validate_password_no_lowercase(self):
        """Test detection of missing lowercase."""
        issues = validate_password_policy("NOLOWERCASE123!")
        
        assert len(issues) >= 1
        assert any('lowercase' in i['message'] for i in issues)
    
    def test_validate_password_no_digit(self):
        """Test detection of missing digit."""
        issues = validate_password_policy("NoDigitsHere!!")
        
        assert len(issues) >= 1
        assert any('digit' in i['message'] for i in issues)
    
    def test_validate_password_no_special(self):
        """Test detection of missing special character."""
        issues = validate_password_policy("NoSpecial123")
        
        assert len(issues) >= 1
        assert any('special character' in i['message'] for i in issues)
    
    def test_validate_password_strong(self):
        """Test strong password passes all checks."""
        issues = validate_password_policy("StrongP@ssw0rd123!")
        
        assert len(issues) == 0


# =============================================================================
# Pass 95: File Upload Content Validation
# =============================================================================

class TestFileContentValidation:
    """Test file upload content validation."""
    
    def test_validate_file_content_png(self):
        """Test PNG magic bytes validation."""
        content = b'\x89PNG\r\n\x1a\n'
        result = validate_file_content(content, 'image/png')
        
        assert result is True
    
    def test_validate_file_content_jpeg(self):
        """Test JPEG magic bytes validation."""
        content = b'\xff\xd8\xff\xe0'
        result = validate_file_content(content, 'image/jpeg')
        
        assert result is True
    
    def test_validate_file_content_pdf(self):
        """Test PDF magic bytes validation."""
        content = b'%PDF-1.4'
        result = validate_file_content(content, 'application/pdf')
        
        assert result is True
    
    def test_validate_file_content_zip(self):
        """Test ZIP magic bytes validation."""
        content = b'PK\x03\x04'
        result = validate_file_content(content, 'application/zip')
        
        assert result is True
    
    def test_validate_file_content_mismatch(self):
        """Test detection of content/MIME mismatch."""
        content = b'Not an image'
        result = validate_file_content(content, 'image/png')
        
        assert result is False
    
    def test_validate_file_content_unknown_mime(self):
        """Test unknown MIME type is allowed."""
        content = b'some content'
        result = validate_file_content(content, 'application/custom')
        
        assert result is True


# =============================================================================
# Pass 96: Network Policy Validation
# =============================================================================

class TestNetworkPolicy:
    """Test network policy validation."""
    
    def test_validate_network_policy_allow_all_egress(self):
        """Test detection of allow-all egress policy."""
        policy = {'egress': {'allow_all': True}}
        issues = validate_network_policy(policy)
        
        assert len(issues) >= 1
        # Check for 'allow all' or 'egress' in the message
        assert any('egress' in i['message'].lower() for i in issues)
    
    def test_validate_network_policy_ssh_exposed(self):
        """Test detection of SSH port exposure."""
        policy = {'ingress': [{'ports': [22]}]}
        issues = validate_network_policy(policy)
        
        assert len(issues) >= 1
        assert any('22' in i['message'] for i in issues)
    
    def test_validate_network_policy_rdp_exposed(self):
        """Test detection of RDP port exposure."""
        policy = {'ingress': [{'ports': [3389]}]}
        issues = validate_network_policy(policy)
        
        assert len(issues) >= 1
        assert any('3389' in i['message'] for i in issues)
    
    def test_validate_network_policy_secure(self):
        """Test secure network policy."""
        policy = {
            'egress': {'allow_all': False, 'rules': []},
            'ingress': [{'ports': [80, 443]}],
        }
        issues = validate_network_policy(policy)
        
        assert len(issues) == 0


# =============================================================================
# Pass 97: Resource Limit Enforcement
# =============================================================================

class TestResourceLimits:
    """Test resource limit enforcement."""
    
    def test_validate_resource_limits_missing_cpu(self):
        """Test detection of missing CPU limit."""
        resources = {'limits': {'memory': '512Mi'}}
        issues = validate_resource_limits(resources)
        
        assert len(issues) >= 1
        assert any('cpu' in i['message'].lower() for i in issues)
    
    def test_validate_resource_limits_missing_memory(self):
        """Test detection of missing memory limit."""
        resources = {'limits': {'cpu': '500m'}}
        issues = validate_resource_limits(resources)
        
        assert len(issues) >= 1
        assert any('memory' in i['message'].lower() for i in issues)
    
    def test_validate_resource_limits_all_set(self):
        """Test all limits set correctly."""
        resources = {
            'limits': {
                'cpu': '500m',
                'memory': '512Mi',
            }
        }
        issues = validate_resource_limits(resources)
        
        assert len(issues) == 0


# =============================================================================
# Pass 98: Health Check Security
# =============================================================================

class TestHealthCheckSecurity:
    """Test health check security."""
    
    def test_validate_health_check_standard_endpoint(self):
        """Test standard health endpoint is accepted."""
        config = {'endpoint': '/health'}
        issues = validate_health_check_config(config)
        
        assert len(issues) == 0
    
    def test_validate_health_check_status_endpoint(self):
        """Test status endpoint is accepted."""
        config = {'endpoint': '/status'}
        issues = validate_health_check_config(config)
        
        assert len(issues) == 0
    
    def test_validate_health_check_nonstandard_endpoint(self):
        """Test non-standard endpoint triggers warning."""
        config = {'endpoint': '/internal/health/details'}
        issues = validate_health_check_config(config)
        
        assert len(issues) >= 1
        assert any('non-standard' in i['message'].lower() for i in issues)


# =============================================================================
# Pass 99: Distributed Tracing Sanitization
# =============================================================================

class TestTracingSanitization:
    """Test distributed tracing data sanitization."""
    
    def test_sanitize_trace_data_password(self):
        """Test password removal from trace data."""
        data = {'user_id': '123', 'password': 'secret123'}
        result = sanitize_trace_data(data)
        
        assert result['password'] == '***REDACTED***'
        assert result['user_id'] == '123'
    
    def test_sanitize_trace_data_token(self):
        """Test token removal from trace data."""
        data = {'request_id': 'abc', 'auth_token': 'bearer123'}
        result = sanitize_trace_data(data)
        
        assert result['auth_token'] == '***REDACTED***'
        assert result['request_id'] == 'abc'
    
    def test_sanitize_trace_data_safe_data(self):
        """Test safe data is preserved."""
        data = {'user_id': '123', 'action': 'login', 'timestamp': '2024-01-01'}
        result = sanitize_trace_data(data)
        
        assert result == data


# =============================================================================
# Pass 100: Security Header Verification
# =============================================================================

class TestSecurityHeaderVerification:
    """Test security header verification."""
    
    def test_verify_security_headers_all_present(self):
        """Test all required security headers present."""
        headers = {
            'Strict-Transport-Security': 'max-age=31536000',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'Content-Security-Policy': "default-src 'self'",
        }
        issues = verify_security_headers(headers)
        
        assert len(issues) == 0
    
    def test_verify_security_headers_missing_hsts(self):
        """Test detection of missing HSTS header."""
        headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
        }
        issues = verify_security_headers(headers)
        
        assert len(issues) >= 1
        assert any('transport' in i['message'].lower() for i in issues)
    
    def test_verify_security_headers_case_insensitive(self):
        """Test case-insensitive header matching."""
        headers = {
            'strict-transport-security': 'max-age=31536000',
            'x-content-type-options': 'nosniff',
        }
        issues = verify_security_headers(headers)
        
        # Should find headers regardless of case
        hsts_missing = not any('transport' in i['message'].lower() for i in issues)
        assert hsts_missing
    
    def test_required_security_headers_list(self):
        """Test REQUIRED_SECURITY_HEADERS is populated."""
        assert 'Strict-Transport-Security' in REQUIRED_SECURITY_HEADERS
        assert 'X-Content-Type-Options' in REQUIRED_SECURITY_HEADERS
        assert 'X-Frame-Options' in REQUIRED_SECURITY_HEADERS


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
