# NIS2 Field Audit Tool - Security Documentation

## Overview

This document describes the security measures implemented in the NIS2 Field Audit Tool, organized by security pass and vulnerability patterns mitigated.

## Security Passes 1-32 Summary

### Pass 1-6: Initial Hardening (Completed)
- SQLite hardening (WAL mode, secure_delete, extension loading disabled)
- Production logging with rotation
- Command injection prevention
- SSH security (strict host key verification, Terrapin fix)
- Rate limiting (scans, connections)
- Input validation

### Pass 7: PyYAML Safe Loading (CVE-2026-24009 Pattern)
**Vulnerability**: Unsafe YAML deserialization can lead to RCE  
**Mitigation**: 
- Use `yaml.safe_load()` exclusively
- PyYAML >= 6.0.1 required
- Never use `yaml.load()` with unsafe loaders

**Code Location**: `app/security_utils.py::safe_yaml_load()`

### Pass 8: XML XXE Prevention (CVE-2026-24400 Pattern)
**Vulnerability**: XML External Entity attacks can read arbitrary files  
**Mitigation**:
- Use `defusedxml` library when available
- Fallback to standard library with XXE pattern detection
- Block DOCTYPE, ENTITY declarations

**Code Location**: `app/security_utils.py::secure_xml_parse()`  
**Applied In**: `app/scanner/network_scanner.py`

### Pass 9: Path Traversal Protection (CVE-2026-28518 Pattern)
**Vulnerability**: Directory traversal via `../` sequences  
**Mitigation**:
- Path canonicalization
- Base directory validation
- Dangerous pattern detection (.., %2e%2e, etc.)
- Filename sanitization

**Code Location**: `app/security_utils.py::validate_path()`, `safe_filename()`

### Pass 10: Race Condition / TOCTOU (CVE-2026-22701 Pattern)
**Vulnerability**: Time-of-check time-of-use in file operations  
**Mitigation**:
- Atomic file writes (write to temp, then rename)
- Proper file locking
- Secure temporary file creation

**Code Location**: `app/security_utils.py::atomic_write()`  
**Applied In**: `app/config.py`

### Pass 11: ReDoS Prevention (CVE-2026-26006 Pattern)
**Vulnerability**: Catastrophic regex backtracking  
**Mitigation**:
- Regex timeout protection (Unix signal-based)
- Bounded pattern lengths
- Safe regex wrapper

**Code Location**: `app/security_utils.py::RegexValidator`, `safe_regex_match()`  
**Applied In**: `app/scanner/network_scanner.py`

### Pass 12: Pickle Deserialization (CVE-2026-28277 Pattern)
**Vulnerability**: Unsafe pickle can execute arbitrary code  
**Mitigation**:
- Ban pickle for untrusted data
- Use JSON for serialization
- `safe_json_dump()`, `safe_json_load()` wrappers

**Code Location**: `app/security_utils.py::safe_json_dump()`, `safe_json_load()`

### Pass 13: Log Injection Prevention (CVE-2026-23566 Pattern)
**Vulnerability**: Newline injection can forge log entries  
**Mitigation**:
- Sanitize log messages (replace `\n`, `\r` with visible equivalents)
- JSON formatter with proper escaping
- Context variable sanitization

**Code Location**: `app/security_utils.py::sanitize_for_logging()`  
**Applied In**: `app/logging_config.py`

### Pass 14: Dependency Version Pinning
**Vulnerability**: Transitive dependency vulnerabilities  
**Mitigation**:
- Pinned minimum versions for security
- setuptools >= 70.0.0
- wheel >= 0.43.0
- pyyaml >= 6.0.1

**Code Location**: `requirements.txt`

### Pass 15: File Permission Hardening
**Vulnerability**: World-readable sensitive files  
**Mitigation**:
- Database files: 0o600 (owner read/write only)
- Config files: 0o600
- Log files: 0o600
- Secure directory creation: 0o700

**Code Location**: `app/security_utils.py::secure_file_permissions()`  
**Applied In**: `app/storage/db.py`, `app/config.py`

### Pass 16: Environment Variable Leak Prevention
**Vulnerability**: Secrets in environment/process listing  
**Mitigation**:
- No credential persistence to disk
- Memory-only credential storage
- Automatic credential clearing after use

**Code Location**: `app/models/device.py` (credentials field)

### Pass 17: Input Validation Hardening
**Vulnerability**: Type confusion and injection  
**Mitigation**:
- Strict type checking (`validate_type()`)
- Range validation (`validate_range()`)
- String length limits (`validate_string_length()`)

**Code Location**: `app/security_utils.py`

### Pass 18: Secure Defaults
**Vulnerability**: Insecure default configurations  
**Mitigation**:
- Strict host key verification enabled by default
- Rate limiting enabled by default
- Encryption required by default
- Dangerous commands blocked by default

**Code Location**: `app/config.py`, `app/connector/device_manager.py`

### Pass 19: Security Documentation
This document and inline security comments throughout the codebase.

---

## Extended Security Hardening (Passes 20-32) - March 2026

### Pass 20: Supply Chain Security (Dependency Confusion/Typosquatting)
**Research**: 73% increase in malicious packages (ReversingLabs 2026 Report)  
**Vulnerabilities**: Dependency confusion, typosquatting, malicious maintainer accounts  
**CVEs**: Various supply chain attacks (npm, PyPI incidents)  
**Mitigation**:
- Package name validation against known typosquatting patterns
- Requirements file integrity hashing
- Private registry validation
- Dependency graph auditing

**Code Location**: `app/security_utils.py::validate_package_name()`, `generate_requirements_hash()`

### Pass 21: Package Installation Security (Wheel/Pip Vulnerabilities)
**Vulnerabilities**: 
- CVE-2026-1703: pip path traversal in wheel extraction
- CVE-2026-24049: wheel privilege escalation via malicious filenames  
**Mitigation**:
- Wheel entry name validation for path traversal patterns
- Block absolute paths in archive entries
- Block system directory references (`/etc/`, `C:\\`, etc.)
- Permission validation on extracted files

**Code Location**: `app/security_utils.py::validate_wheel_entry_name()`

### Pass 22: DNS Rebinding Protection
**Vulnerabilities**:
- CVE-2025-66416: MCP Python SDK DNS rebinding
- CVE-2026-30858: WeKnora web_fetch DNS rebinding  
**Attack**: Malicious domains resolve to public IP during validation, then to private IP during execution  
**Mitigation**:
- Validate resolved IPs against private/reserved ranges
- Block cloud metadata endpoints (169.254.169.254)
- DNS resolution validation before requests

**Code Location**: `app/security_utils.py::validate_host_against_dns_rebinding()`, `is_private_ip()`

### Pass 23: SSRF Prevention (Server-Side Request Forgery)
**Vulnerabilities**:
- CVE-2026-25580: Pydantic AI URL download SSRF
- CVE-2026-30953: LinkAce internal network access
- CVE-2026-2654: HuggingFace SmolAgents SSRF  
**Mitigation**:
- URL scheme allowlist (http/https only)
- Private IP range blocking (RFC 1918)
- Cloud metadata endpoint protection
- Hostname allowlist support
- DNS rebinding integration

**Code Location**: `app/security_utils.py::validate_url_for_ssrf()`, `create_safe_url_validator()`

### Pass 24: Memory Safety (Buffer Overflow Prevention)
**Vulnerabilities**:
- CVE-2026-25990: Pillow PSD buffer overflow
- CVE-2026-24814: Swoole integer overflow  
**Mitigation**:
- Buffer size validation with configurable limits
- String length limits (default 10MB)
- File size limits (default 100MB)
- Collection size limits (1M items)
- JSON nesting depth limits (100 levels)

**Code Location**: `app/security_utils.py::validate_buffer_size()`, `validate_string_for_memory_safety()`

### Pass 25: Object Pollution Prevention
**Vulnerabilities**:
- CVE-2026-27212: Swiper prototype pollution (CVSS 9.4)
- CVE-2026-26021: set-in npm prototype pollution  
**Attack**: Injecting properties into `__proto__`, `constructor`, or `prototype`  
**Mitigation**:
- Property name validation against dangerous names
- Path validation for nested object access
- `safe_set_nested_value()` with pollution protection
- Block `__proto__`, `constructor`, `prototype` access

**Code Location**: `app/security_utils.py::validate_property_name()`, `validate_object_path()`, `safe_set_nested_value()`

### Pass 26: Dynamic Code Execution Prevention
**Vulnerabilities**:
- CVE-2026-0863: n8n eval injection via python-task-executor
- CVE-2026-1470: n8n expression evaluation RCE
- CVE-2026-26030: Semantic Kernel InMemoryVectorStore eval injection  
**Attack Pattern**: User input reaching `eval()`, `exec()`, or dynamic code execution  
**Mitigation**:
- Code string validation for dangerous patterns
- Restricted `safe_eval()` with ast.literal_eval preference
- Block `eval()`, `exec()`, `compile()`, `__import__()` patterns
- Minimal globals in evaluation context

**Code Location**: `app/security_utils.py::validate_code_string()`, `safe_eval()`

### Pass 27: Hash Collision DoS Prevention
**Vulnerability**: Hash flooding attacks on dictionaries  
**Mitigation**:
- Python hash randomization verification
- PYTHONHASHSEED enforcement
- Collection size limits
- Rate limiting on hash-based operations

**Code Location**: `app/security_utils.py::ensure_hash_randomization()`

### Pass 28: Certificate Pinning and Validation
**Vulnerabilities**:
- CVE-2026-3336: AWS-LC PKCS7 certificate validation bypass
- CVE-2026-22696: Intel dcap-qvl attestation bypass  
**Mitigation**:
- Certificate fingerprint pinning
- Chain validation enforcement
- OCSP verification
- Self-signed certificate rejection

**Code Location**: `app/security_utils.py::validate_certificate_pin()`, `add_certificate_pin()`

### Pass 29: Constant-Time Operations (Timing Attack Prevention)
**Research**: Bleichenbacher timing attacks on RSA (CVE-2020-25659 pattern)  
**Attack**: Measuring execution time to infer secret data  
**Mitigation**:
- `constant_time_compare()` for string/bytes comparison
- `hmac.compare_digest()` wrapper
- Avoid short-circuit comparison operators for secrets

**Code Location**: `app/security_utils.py::constant_time_compare()`, `constant_time_compare_hmac()`

### Pass 30: Safe Deserialization (Pickle Security)
**Vulnerabilities**:
- CVE-2025-10155: PickleScan file extension bypass
- CVE-2025-10156: PickleScan ZIP CRC bypass
- CVE-2025-10157: PickleScan blacklist bypass  
**Mitigation**:
- Pickle opcode scanning for dangerous operations
- Restricted unpickler with allowlist
- `__reduce__` detection
- Prefer JSON over pickle
- Model file extension validation

**Code Location**: `app/security_utils.py::scan_pickle_for_dangerous_opcodes()`, `safe_pickle_load()`

### Pass 31: ML/AI Pipeline Security (Model Poisoning Prevention)
**Research**: Training data poisoning, model extraction attacks (2026)  
**Vulnerabilities**: Backdoored models, data poisoning, supply chain via model hubs  
**Mitigation**:
- Safe model format preference (SafeTensors)
- Model file extension validation
- Model hash verification
- Model integrity checking
- Suspicious format warnings

**Code Location**: `app/security_utils.py::validate_model_file_extension()`, `compute_model_hash()`

### Pass 32: Import System Security
**Vulnerability**: CVE-2026-2297 - CPython import hook bypasses sys.audit  
**Issue**: SourcelessFileLoader doesn't use io.open_code(), bypassing audit hooks  
**Mitigation**:
- Import path restrictions
- Audit hook registration
- `.pyc` file security checks
- World-writable file detection
- Import event monitoring

**Code Location**: `app/security_utils.py::register_import_audit_hook()`, `check_sourceless_import_security()`

---

## Cryptographic Security

### CVE-2026-26007 (Cryptography Package)
- **Status**: Fixed
- **Fix**: `cryptography>=46.0.5`
- **Issue**: Elliptic curve subgroup validation

### SSH Security
- **Terrapin Attack**: Fixed with `paramiko>=3.4.0`
- **Strict Host Key Verification**: Enabled
- **Session Timeout**: 60 seconds
- **Auth Timeout**: 30 seconds

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Network scans | 10 per minute |
| SSH connections (global) | 20 per minute |
| SSH connections (per IP) | 5 per minute |
| JSON field size | 10 MB |
| SQLite parameters | 900 max |
| Buffer size | 10 MB |
| File size | 100 MB |
| Collection size | 1M items |
| JSON nesting | 100 levels |

## Database Security

- **WAL Mode**: Enabled for crash recovery
- **secure_delete**: ON
- **Extension Loading**: Disabled
- **Busy Timeout**: 5000ms
- **File Permissions**: 0o600

## Security Contact

For security issues, please follow responsible disclosure practices.

## References

- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [ReversingLabs 2026 Supply Chain Report](https://www.reversinglabs.com/)
- [Python Security Best Practices](https://python.org/security)


---

## Extended Security Hardening (Passes 33-45) - March 2026

### Pass 33: JWT Authentication Bypass Prevention
**CVEs**:
- CVE-2026-29000: pac4j-jwt authentication bypass (CVSS 10.0 Critical)
- CVE-2026-28802: Authlib JWT signature verification bypass

**Vulnerability**: Authentication bypass via JWE-wrapped PlainJWT, alg:none attacks, and key confusion. Attackers can forge tokens using public keys or bypass signature verification entirely.

**Mitigation**:
- Strict JWT algorithm validation (reject alg:none, None, NONE)
- Enforce signature verification (no soft-fail branches)
- JWE inner token signature validation
- Key confusion prevention (RSA/HMAC separation)
- JWK embedded header rejection
- Comprehensive algorithm allowlist

**Code Location**: `app/security_utils.py::validate_jwt_algorithm()`, `validate_jwt_header()`, `sanitize_jwt_token()`

---

### Pass 34: SQL Injection Prevention (Django Pattern)
**CVEs**:
- CVE-2026-1312: Django QuerySet.order_by() SQL injection via column aliases with FilteredRelation
- CVE-2026-3057: pearProjectApi SQL injection via dateTotalForProject
- CVE-2026-21892: Parsl SQL injection via unsafe string formatting

**Vulnerability**: SQL injection through column aliases, unsanitized parameters, and Python string formatting (% operator) in SQL construction.

**Mitigation**:
- Mandatory parameterized queries (no string formatting/interpolation)
- Column alias allowlisting with dangerous character filtering
- ORM query method security (order_by, filter, annotate validation)
- SQL dialect-specific input validation
- Semicolon and comment detection
- Period character validation in column names (CVE-2026-1312 pattern)

**Code Location**: `app/security_utils.py::validate_sql_column_alias()`, `validate_sql_order_by()`

---

### Pass 35: Advanced XXE Prevention
**CVEs**:
- CVE-2026-24400: AssertJ XXE via XmlStringPrettyFormatter (default DocumentBuilderFactory settings)
- CVE-2026-1227: EBO Server XXE via TGML graphics files
- CVE-2026-1218: Bjskzy Zhiyou ERP XXE via initRCForm

**Vulnerability**: XXE via insecure XML parser configuration allowing external entity resolution, DTD processing, and XInclude processing.

**Mitigation**:
- Secure XML parser factory configuration
- DTD/DOCTYPE declaration blocking
- External entity (SYSTEM, PUBLIC) blocking
- XInclude processing disabled
- XML catalog restrictions
- Entity expansion limits (Billion Laughs DoS prevention)
- XML nesting depth limits (100 levels)

**Code Location**: `app/security_utils.py::create_secure_xml_parser()`, `parse_xml_securely()`

---

### Pass 36: Secure File Upload
**CVEs**:
- CVE-2026-25737: Budibase arbitrary file upload bypass (client-side only validation)
- CVE-2026-24486: Python-Multipart path traversal (UPLOAD_KEEP_FILENAME=True)
- CVE-2026-23704: Movable Type unrestricted file upload

**Vulnerability**: File extension bypass, path traversal in upload filenames, dangerous file type uploads, and MIME type spoofing.

**Mitigation**:
- Server-side file extension validation (not just client)
- Dangerous extension blocklist (.exe, .php, .py, .sh, etc.)
- MIME type verification via magic bytes (not just extension)
- Upload directory path traversal prevention
- Configurable file size limits
- Safe filename sanitization (UUID-based naming option)
- Content-Type header validation

**Code Location**: `app/security_utils.py::validate_file_extension()`, `validate_file_content_type()`, `sanitize_upload_filename()`, `validate_upload_path()`

---

### Pass 37: Open Redirect Prevention
**CVEs**:
- CVE-2026-2709: Busy Framework open redirect via state parameter
- CVE-2026-25477: AFFiNE open redirect via regex suffix bypass
- CVE-2026-1406: BootDo open redirect via Host header manipulation
- CVE-2026-23729: WeGIA open redirect via nextPage parameter
- CVE-2026-27191: feathersjs URL authority injection (@attacker.com bypass)

**Vulnerability**: URL redirection to untrusted sites via unvalidated redirect parameters, regex bypasses, and URL authority injection.

**Mitigation**:
- Strict redirect URL allowlist with exact domain matching
- Domain validation (no suffix/prefix matching)
- URL authority injection prevention (detect @ symbol abuse)
- Relative URL enforcement option
- data:, javascript:, vbscript: URI blocking
- Host header validation

**Code Location**: `app/security_utils.py::validate_redirect_url()`, `add_allowed_redirect_domain()`

---

### Pass 38: Secure Deserialization (Advanced)
**CVEs**:
- CVE-2026-21226: Azure Core shared client library insecure deserialization
- CVE-2026-27830: c3p0 userOverridesAsString deserialization RCE
- CVE-2026-23946: Tendenci RCE via pickle deserialization
- CVE-2026-28277: LangGraph checkpoint unsafe msgpack deserialization

**Vulnerability**: Insecure deserialization of untrusted data via pickle, msgpack, and Java serialization leading to RCE.

**Mitigation**:
- JSON-only deserialization policy (prefer JSON over pickle)
- Pickle data scanning for dangerous types (eval, exec, os.system, etc.)
- Restricted unpickler with class allowlist
- msgpack safety validation
- Serialized object signature verification
- Deserialization depth limits
- Type checking before object instantiation

**Code Location**: `app/security_utils.py::validate_pickle_data()`, `safe_json_deserialize()`, `safe_unpickle()`

---

### Pass 39: Session Fixation Prevention
**CVEs**:
- CVE-2026-23796: Quick.Cart session fixation - session ID not regenerated after authentication

**Vulnerability**: Session fixation attacks where session ID remains unchanged after login, allowing attackers to hijack authenticated sessions.

**Mitigation**:
- Session ID regeneration on login (invalidate old, create new)
- Cryptographically secure session ID generation (secrets.token_urlsafe)
- Session ID optional binding to IP/User-Agent
- Secure cookie flags (HttpOnly, Secure, SameSite=Strict)
- Session timeout enforcement
- Concurrent session limits per user

**Code Location**: `app/security_utils.py::generate_secure_session_id()`, `regenerate_session_id()`, `get_secure_cookie_flags()`

---

### Pass 40: Clickjacking Prevention
**CVEs**:
- CVE-2026-24839: Dokploy clickjacking via missing frame-busting headers
- CVE-2026-23731: WeGIA clickjacking (missing X-Frame-Options, no CSP frame-ancestors)

**Vulnerability**: UI redressing attacks via iframe embedding without frame-busting protections.

**Mitigation**:
- X-Frame-Options: DENY or SAMEORIGIN headers
- Content-Security-Policy frame-ancestors directive
- X-Content-Type-Options: nosniff
- Referrer-Policy: strict-origin-when-cross-origin
- Frame-busting JavaScript (legacy browser support)
- Clickjacking-aware UI design

**Code Location**: `app/security_utils.py::get_clickjacking_protection_headers()`, `validate_frame_options_header()`, `generate_frame_busting_js()`

---

### Pass 41: LDAP Injection Prevention
**CVEs**:
- CVE-2026-24130: Moonraker LDAP search filter injection (401 response enumeration)
- CVE-2026-21880: Kanboard LDAP injection via unsanitized user input
- CVE-2025-61911: python-ldap escape_filter_chars bypass (list/dict type confusion)
- CVE-2025-61912: python-ldap escape_dn_chars NUL handling issue

**Vulnerability**: LDAP search filter injection via unsanitized user input in authentication queries.

**Mitigation**:
- LDAP filter metacharacter escaping (*, (, ), \, NUL)
- Type checking for assertion_value parameter (CVE-2025-61911)
- RFC 4515/RFC 4514 compliant escaping
- Parameterized LDAP queries
- DN component validation
- Balanced parentheses validation
- Injection pattern detection

**Code Location**: `app/security_utils.py::escape_ldap_filter_value()`, `escape_ldap_dn_value()`, `validate_ldap_filter()`

---

### Pass 42: NoSQL Injection Prevention
**Research**: MongoDB operator injection, Redis command injection patterns (2026)

**Vulnerability**: NoSQL injection attacks targeting MongoDB ($where, $ne operators) and Redis command injection.

**Mitigation**:
- NoSQL operator injection prevention ($where, $ne, $gt, etc.)
- JavaScript execution operator blocking ($where, $accumulator, $function)
- Query object type validation
- MongoDB query sanitization (recursive)
- MongoDB field name validation ($ prefix blocking)
- Redis command injection prevention (newline filtering)
- Dangerous Redis command blocking (CONFIG, FLUSHALL, etc.)
- JSON schema validation for queries

**Code Location**: `app/security_utils.py::sanitize_mongodb_query()`, `validate_mongodb_field_name()`, `sanitize_redis_command()`

---

### Pass 43: HTTP Header Injection Prevention
**CVEs**:
- CVE-2026-24489: Gakido HTTP header injection via CRLF in header values
- CVE-2026-0865: wsgiref.headers control character injection (\r\n in headers)

**Vulnerability**: CRLF injection in HTTP headers enabling response splitting, cache poisoning, and XSS.

**Mitigation**:
- CRLF (\r\n) character filtering in header names and values
- Null byte (\x00) filtering
- Header name validation (no :, space, tab)
- Printable ASCII enforcement for header names
- Header value whitespace trimming
- HTTP/2 header validation
- Response splitting prevention

**Code Location**: `app/security_utils.py::sanitize_http_header_name()`, `sanitize_http_header_value()`, `validate_http_headers()`

---

### Pass 44: Information Disclosure Prevention
**CVEs**:
- CVE-2026-2297: CPython information disclosure (SourcelessFileLoader bypasses sys.audit)
- CVE-2026-2861: Foswiki information disclosure via error messages
- CVE-2026-21626: Forum post ACL information disclosure via JSON output

**Vulnerability**: Sensitive information disclosure via error messages, stack traces, debug information, and audit log bypasses.

**Mitigation**:
- Error message sanitization (stack trace removal in production)
- Debug mode detection and blocking
- Sensitive data masking in logs (passwords, secrets, tokens)
- Credit card number masking
- SSN masking
- Version information hiding
- .pyc file audit event verification

**Code Location**: `app/security_utils.py::sanitize_error_message()`, `mask_sensitive_data()`, `check_pyc_audit_event()`

---

### Pass 45: Secure Configuration Management
**Research**: 2026 configuration security patterns

**Vulnerability**: Insecure defaults, configuration injection, secret exposure in config files, overly permissive file permissions.

**Mitigation**:
- Configuration file permission validation (0o600 required)
- World-readable/writable file detection
- Secure file permission setting
- Environment variable sanitization (shell injection prevention)
- Configuration schema validation (type checking, secret length validation)
- Port number validation
- Path validation
- JSON/YAML/TOML secure loading
- Runtime configuration change detection support

**Code Location**: `app/security_utils.py::validate_config_file_permissions()`, `set_secure_file_permissions()`, `validate_config_schema()`, `load_secure_config()`

---

## Security Testing

All security passes have corresponding tests in `tests/test_security.py`:

```bash
# Run all security tests
python -m pytest tests/test_security.py -v

# Run specific pass tests
python -m pytest tests/test_security.py::TestJWTValidation -v
python -m pytest tests/test_security.py::TestSQLInjectionPrevention -v
```

---

## Quick Reference: Security Function Mapping

| Pass | Function(s) | Primary Protection |
|------|-------------|-------------------|
| 33 | `validate_jwt_algorithm()`, `sanitize_jwt_token()` | JWT bypass prevention |
| 34 | `validate_sql_column_alias()`, `validate_sql_order_by()` | SQL injection |
| 35 | `parse_xml_securely()` | XXE prevention |
| 36 | `validate_file_extension()`, `sanitize_upload_filename()` | File upload security |
| 37 | `validate_redirect_url()` | Open redirect prevention |
| 38 | `validate_pickle_data()`, `safe_json_deserialize()` | Deserialization safety |
| 39 | `regenerate_session_id()`, `get_secure_cookie_flags()` | Session fixation |
| 40 | `get_clickjacking_protection_headers()` | Clickjacking |
| 41 | `escape_ldap_filter_value()`, `validate_ldap_filter()` | LDAP injection |
| 42 | `sanitize_mongodb_query()`, `sanitize_redis_command()` | NoSQL injection |
| 43 | `sanitize_http_header_name()`, `sanitize_http_header_value()` | Header injection |
| 44 | `sanitize_error_message()`, `mask_sensitive_data()` | Info disclosure |
| 45 | `validate_config_file_permissions()`, `validate_config_schema()` | Config security |

---

## Summary

The NIS2 Field Audit Tool now implements **45 comprehensive security passes** covering:

- **Passes 1-19**: Baseline hardening (SQLite, SSH, XML, YAML, logging, input validation)
- **Passes 20-32**: Extended coverage (supply chain, SSRF, DNS rebinding, deserialization, ML security)
- **Passes 33-45**: 2026 CVE coverage (JWT bypass, SQL injection, XXE, file uploads, open redirects, LDAP/NoSQL injection, clickjacking, session fixation)

Total: **45 security passes** addressing **40+ CVE patterns** and **2026 security research findings**.

---

*Last Updated: March 2026*
*Security Passes 33-45 implemented based on fresh 2026 web search research*


---

## Application Consolidation Phase (Passes 46-58) - March 2026

The following security passes were implemented as part of the application consolidation phase, addressing March 2026 CVE research and application-level security hardening.

### Pass 46: Rate Limiting Enforcement
**CVEs**:
- CVE-2026-25114: CloudCharge WebSocket API authentication DoS (unlimited auth attempts)
- CVE-2026-28342: OliveTin PasswordHash API DoS via concurrent requests
- CVE-2026-23848: MyTube rate limiting bypass via X-Forwarded-For spoofing

**Vulnerability**: Missing or bypassable rate limiting allowing brute force attacks, DoS, and resource exhaustion.

**Mitigation**:
- Token bucket rate limiting with configurable limits
- Per-client rate tracking (IP, user ID, API key)
- X-Forwarded-For spoofing protection with trusted proxy configuration
- Rate limit exception raising (not silent failure)
- Remaining request tracking
- IP extraction from multiple headers (X-Forwarded-For, X-Real-IP, REMOTE_ADDR)

**Code Location**: `app/security_utils.py::RateLimiter`, `check_rate_limit()`, `extract_client_ip()`

---

### Pass 47: Authentication Flow Hardening
**CVEs**:
- CVE-2026-23906: Apache Druid LDAP authentication bypass via anonymous bind
- CVE-2026-28536: NuxtJS Nitro authentication bypass via path manipulation
- CVE-2026-2095: Progress Telerik Report Server authentication bypass

**Vulnerability**: Authentication bypass via LDAP anonymous bind, empty passwords, and insufficient auth response validation.

**Mitigation**:
- LDAP anonymous bind detection (empty/whitespace password + successful auth)
- Username mismatch detection in auth responses
- Bind DN validation requirement
- Brute force protection with account lockout
- Weak password detection (minimum length enforcement)
- Failed attempt tracking and progressive delays

**Code Location**: `app/security_utils.py::validate_ldap_auth_response()`, `validate_auth_attempt()`

---

### Pass 48: API Key and Credential Rotation
**CVEs**:
- CVE-2026-21852: Claude Code API key theft via ANTHROPIC_BASE_URL override
- CVE-2026-25253: Moltbook API key exposure (1.5M tokens leaked)
- CVE-2026-22038: Samsung Shop authentication token manipulation

**Vulnerability**: Hardcoded API keys, insecure credential storage, and lack of credential rotation policies.

**Mitigation**:
- Secure API key generation with high entropy (secrets.token_urlsafe)
- API key format validation (prefix, length, character restrictions)
- Key rotation scheduling based on creation timestamp
- Key masking for display/logging (first 4 + ... + last 4)
- Dangerous character detection in keys (command injection prevention)
- Prefix-based key identification

**Code Location**: `app/security_utils.py::generate_secure_api_key()`, `validate_api_key_format()`, `should_rotate_api_key()`, `mask_api_key()`

---

### Pass 49: CSRF Protection Consolidation
**CVEs**:
- CVE-2026-24885: Kanboard CSRF via Content-Type misconfiguration (text/plain allowed)
- CVE-2026-1148: Queue Management System CSRF via missing token validation
- CVE-2026-22030: React Router CSRF via insufficient origin validation

**Vulnerability**: CSRF attacks via Content-Type bypass, missing tokens, and origin validation failures.

**Mitigation**:
- Cryptographically secure CSRF token generation
- Constant-time token comparison (HMAC.compare_digest)
- Content-Type validation (block text/plain for state-changing operations)
- Origin header validation with allowlist
- Subdomain origin matching support
- Token mismatch detection with clear error messages

**Code Location**: `app/security_utils.py::generate_csrf_token()`, `validate_csrf_token()`, `validate_content_type_for_csrf()`, `validate_origin_header()`

---

### Pass 50: WebSocket Origin Validation
**CVEs**:
- CVE-2026-1692: PcVue WebSocket missing origin validation (SignalR endpoints)
- CVE-2026-25114: CloudCharge WebSocket authentication without rate limiting

**Vulnerability**: Cross-site WebSocket hijacking (CSWSH) via missing origin validation in WebSocket handshake.

**Mitigation**:
- WebSocket origin header mandatory validation
- Origin allowlist with wildcard subdomain support (*.example.com)
- Missing origin rejection
- WebSocket-specific security headers
- Content-Security-Policy with connect-src restrictions

**Code Location**: `app/security_utils.py::validate_websocket_origin()`, `get_websocket_security_headers()`

---

### Pass 51: CORS Policy Enforcement
**CVEs**:
- CVE-2024-10906: DB-GPT overly permissive CORS (* wildcard with credentials)
- CVE-2026-24435: Tenda W30E router CORS misconfiguration

**Vulnerability**: Overly permissive CORS policies allowing cross-origin attacks with credentials.

**Mitigation**:
- Strict origin allowlist (no wildcard * allowed)
- HTTPS enforcement for production origins
- Subdomain matching with explicit wildcards
- Preflight request validation (methods and headers)
- Credentials only with specific origins (never with wildcard)
- CORS header generation with security checks

**Code Location**: `app/security_utils.py::validate_cors_origin()`, `get_cors_headers()`, `validate_cors_preflight_request()`

---

### Pass 52: Audit Log Integrity
**CVEs**:
- CVE-2026-3494: Delta Electronics DRASim audit log bypass via newline injection
- CVE-2026-30928: ZOHO ManageEngine ADAudit Plus security bypass

**Vulnerability**: Audit log tampering via injection attacks and lack of integrity verification.

**Mitigation**:
- Tamper-evident audit log entries with SHA-256 integrity hashes
- Audit entry verification against stored hashes
- Log injection prevention (newline, carriage return, null byte removal)
- Structured logging with timestamps (ISO 8601)
- User ID sanitization for audit entries
- Entry tampering detection

**Code Location**: `app/security_utils.py::create_audit_log_entry()`, `verify_audit_entry()`, `sanitize_audit_user_id()`

---

### Pass 53: Configuration Security Validation
**CVEs**:
- CVE-2026-1731: BeyondTrust Remote Support command injection via improper input handling (CVSS 9.9)
- CVE-2025-60262: H3C wireless controller misconfiguration (vsftpd root ownership)
- CVE-2026-25253: Moltbook Supabase RLS misconfiguration (1.5M tokens exposed)

**Vulnerability**: Security misconfigurations including anonymous binds, debug modes, wildcard CORS, and hardcoded secrets.

**Mitigation**:
- Configuration file pattern scanning (empty passwords, debug=true, wildcard CORS)
- Hardcoded secret detection (API keys, passwords, private keys)
- Secure default validation (CSRF, secure cookies, HTTPOnly, XSS protection)
- Missing security setting detection
- Configuration schema validation (types, ports, paths)

**Code Location**: `app/security_utils.py::validate_configuration_security()`, `check_secure_defaults()`

---

### Pass 54: Error Message Sanitization
**CVEs**:
- CVE-2026-26144: Microsoft Excel information disclosure via improper input neutralization (zero-click Copilot exploitation)
- CVE-2026-20838: Windows Kernel information disclosure via overly detailed error messages
- CVE-2026-22604: OpenProject username disclosure via password change error responses

**Vulnerability**: Information disclosure via verbose error messages containing stack traces, file paths, and system details.

**Mitigation**:
- Production error message sanitization (generic messages only)
- Error categorization (database, file, permission, authentication, connection)
- Stack trace removal in production mode
- Safe error response generation with error IDs
- Development mode support for debugging

**Code Location**: `app/security_utils.py::sanitize_production_error()`, `get_safe_error_response()`

---

### Pass 55: Session Timeout Enforcement
**CVEs**:
- CVE-2026-23646: Node.js session fixation and insufficient timeout
- CVE-2026-22341: IBM Security Verify Access OIDC session fixation

**Vulnerability**: Sessions without proper timeout enforcement leading to session hijacking and fixation attacks.

**Mitigation**:
- Dual timeout enforcement (absolute max duration + idle timeout)
- Configurable timeouts (default: 24h max, 15min idle)
- Session TTL calculation
- Session refresh recommendations based on age threshold
- Clear timeout exceeded error messages

**Code Location**: `app/security_utils.py::validate_session_timeout()`, `calculate_session_ttl()`, `should_refresh_session()`

---

### Pass 56: File Upload Restriction
**CVEs**:
- CVE-2026-21536: Microsoft Devices Pricing Program RCE via unrestricted file upload (CVSS 9.8)
- CVE-2026-25737: Budibase arbitrary file upload bypass

**Vulnerability**: Unrestricted file uploads allowing remote code execution via executable file uploads.

**Mitigation**:
- Dangerous extension blocklist (.exe, .php, .py, .sh, .jar, .jsp, etc.)
- Double extension detection (file.pdf.exe)
- Safe file type allowlist for documents (.pdf, .docx, .txt, etc.)
- File size validation
- Filename sanitization (path traversal removal, null byte stripping)
- Hidden file handling (prefix with 'file_')
- Filename length limiting

**Code Location**: `app/security_utils.py::validate_upload_file_extension()`, `validate_upload_file_size()`, `sanitize_uploaded_filename()`

---

### Pass 57: Request Origin Validation
**CVEs**:
- CVE-2026-25151: Qwik CSRF via Content-Type parsing edge cases
- CVE-2026-25221: PolarLearn OAuth Login CSRF via missing state parameter
- CVE-2026-25631: n8n credential domain validation bypass

**Vulnerability**: CSRF attacks via OAuth flow manipulation and missing origin validation.

**Mitigation**:
- Origin/Referer header validation for state-changing requests
- Allowed host allowlist with HTTPS enforcement
- HTTP origin rejection (except localhost for development)
- OAuth state parameter validation with constant-time comparison
- Missing state parameter detection
- State mismatch detection with CSRF warning

**Code Location**: `app/security_utils.py::validate_request_origin()`, `validate_oauth_state()`

---

### Pass 58: Security Header Consolidation
**Research**: 2026 security header best practices

**Vulnerability**: Missing or weak security headers enabling XSS, clickjacking, MIME sniffing, and other attacks.

**Mitigation**:
- Comprehensive security headers:
  - X-Content-Type-Options: nosniff
  - X-XSS-Protection: 1; mode=block
  - X-Frame-Options: DENY
  - Strict-Transport-Security: max-age=31536000; includeSubDomains
  - Referrer-Policy: strict-origin-when-cross-origin
  - Permissions-Policy: Restricted feature access
- Content Security Policy (CSP) generation with nonce support
- Header validation (detect missing/weak headers)
- HTTPS-only mode option

**Code Location**: `app/security_utils.py::get_security_headers()`, `get_content_security_policy()`, `validate_security_headers()`

---

## Security Testing

All security passes have corresponding tests:

```bash
# Run all security tests
python -m pytest tests/test_security.py tests/test_security_passes_46_58.py -v

# Run specific phase tests
python -m pytest tests/test_security.py -v                    # Passes 33-45
python -m pytest tests/test_security_passes_46_58.py -v       # Passes 46-58
```

---

## Quick Reference: Security Function Mapping (Extended)

| Pass | Function(s) | Primary Protection |
|------|-------------|-------------------|
| 33 | `validate_jwt_algorithm()`, `sanitize_jwt_token()` | JWT bypass prevention |
| 34 | `validate_sql_column_alias()`, `validate_sql_order_by()` | SQL injection |
| 35 | `parse_xml_securely()` | XXE prevention |
| 36 | `validate_file_extension()`, `sanitize_upload_filename()` | File upload security |
| 37 | `validate_redirect_url()` | Open redirect prevention |
| 38 | `validate_pickle_data()`, `safe_json_deserialize()` | Deserialization safety |
| 39 | `regenerate_session_id()`, `get_secure_cookie_flags()` | Session fixation |
| 40 | `get_clickjacking_protection_headers()` | Clickjacking |
| 41 | `escape_ldap_filter_value()`, `validate_ldap_filter()` | LDAP injection |
| 42 | `sanitize_mongodb_query()`, `sanitize_redis_command()` | NoSQL injection |
| 43 | `sanitize_http_header_name()`, `sanitize_http_header_value()` | Header injection |
| 44 | `sanitize_error_message()`, `mask_sensitive_data()` | Info disclosure |
| 45 | `validate_config_file_permissions()`, `validate_config_schema()` | Config security |
| 46 | `RateLimiter`, `check_rate_limit()`, `extract_client_ip()` | Rate limiting |
| 47 | `validate_ldap_auth_response()`, `validate_auth_attempt()` | Auth flow security |
| 48 | `generate_secure_api_key()`, `validate_api_key_format()` | Credential rotation |
| 49 | `generate_csrf_token()`, `validate_csrf_token()` | CSRF protection |
| 50 | `validate_websocket_origin()` | WebSocket security |
| 51 | `validate_cors_origin()`, `get_cors_headers()` | CORS enforcement |
| 52 | `create_audit_log_entry()`, `verify_audit_entry()` | Audit integrity |
| 53 | `validate_configuration_security()` | Config validation |
| 54 | `sanitize_production_error()` | Error sanitization |
| 55 | `validate_session_timeout()` | Session timeout |
| 56 | `validate_upload_file_extension()` | Upload restriction |
| 57 | `validate_request_origin()`, `validate_oauth_state()` | Origin validation |
| 58 | `get_security_headers()`, `get_content_security_policy()` | Security headers |

---

## Summary

The NIS2 Field Audit Tool now implements **58 comprehensive security passes** covering:

- **Passes 1-19**: Baseline hardening (SQLite, SSH, XML, YAML, logging, input validation)
- **Passes 20-32**: Extended coverage (supply chain, SSRF, DNS rebinding, deserialization, ML security)
- **Passes 33-45**: March 2026 CVE coverage (JWT bypass, SQL injection, XXE, file uploads, open redirects, LDAP/NoSQL injection, clickjacking, session fixation, config management)
- **Passes 46-58**: Application consolidation (rate limiting, auth hardening, CSRF, CORS, audit integrity, session management, security headers)

Total: **58 security passes** addressing **50+ CVE patterns** and **2026 security research findings**.

---

*Last Updated: March 13, 2026*
*Security Passes 46-58 implemented based on March 2026 web research for application consolidation*


---

## Application Consolidation Phase (Passes 59-79) - March 2026

The following security passes were implemented as part of the application consolidation phase, integrating security controls into the application middleware, database layer, and core functionality.

### Pass 59: Request Validation Middleware
**CVEs**:
- CVE-2026-21962: Oracle Fusion Middleware auth bypass via crafted HTTP requests (CVSS 10.0)
- CVE-2026-0958: GitLab JSON validation middleware DoS via resource exhaustion
- CVE-2026-28794: Prototype pollution in RPC JSON deserializer

**Vulnerability**: Request validation bypasses, resource exhaustion via malformed requests, prototype pollution via JSON payloads.

**Mitigation**:
- Request size limits with configurable maximums
- Content-Type validation with allowlist
- JSON payload validation with prototype pollution detection
- Request path sanitization (traversal, null byte, encoded slash detection)
- Unicode dangerous character removal

**Code Location**: `app/security_utils.py::validate_request_size()`, `validate_content_type()`, `validate_json_payload()`, `sanitize_request_path()`

---

### Pass 60: Response Security Middleware
**CVEs**:
- CVE-2026-24489: HTTP header injection in Gakido
- CVE-2026-2975: FastAPI Admin information disclosure via documentation endpoint

**Vulnerability**: HTTP header injection, response splitting, information disclosure via response headers.

**Mitigation**:
- Response header validation and sanitization
- Automatic security header injection
- Dangerous Content-Type blocking
- Response content-type validation

**Code Location**: `app/security_utils.py::validate_response_headers()`, `add_security_headers()`, `validate_response_content_type()`

---

### Pass 61: Authentication Middleware Integration
**CVEs**:
- CVE-2026-27705: Plane auth bypass via missing workspace/project validation (IDOR)
- CVE-2026-1894: WeKan REST API auth bypass via checklistItems manipulation

**Vulnerability**: Authentication bypass via missing context validation, IDOR in API endpoints.

**Mitigation**:
- Multi-source token extraction (header, query, cookie)
- Auth context validation with workspace/project binding
- Token format validation (minimum length, structure)
- Constant-time token comparison

**Code Location**: `app/security_utils.py::extract_auth_token()`, `validate_auth_context()`

---

### Pass 62: Authorization Enforcement Layer
**CVEs**:
- CVE-2026-27705: Plane IDOR via asset patching without workspace validation
- CVE-2026-23982: Apache Superset data access control bypass via dataset overwrite

**Vulnerability**: Insecure Direct Object Reference (IDOR), horizontal/vertical privilege escalation.

**Mitigation**:
- Resource ownership validation
- Role-based access control (RBAC) with hierarchy
- Permission level enforcement
- Admin action restrictions

**Code Location**: `app/security_utils.py::check_resource_access()`, `require_permission()`, `ROLE_*` constants

---

### Pass 63: Database Query Protection
**CVEs**:
- CVE-2026-25544: Payload CMS SQL injection via JSON/richText fields (CVSS 9.8)
- CVE-2026-23984: Apache Superset SQL injection on read-only PostgreSQL connections

**Vulnerability**: SQL injection via unsanitized JSON fields, read-only bypass.

**Mitigation**:
- Raw query validation with dangerous keyword detection
- Table allowlist enforcement
- Query parameter sanitization
- SQL comment and concatenation detection

**Code Location**: `app/security_utils.py::validate_raw_query()`, `sanitize_query_parameter()`

---

### Pass 64: Input Sanitization Pipeline
**CVEs**:
- CVE-2026-25632: EPyT-Flow OS command injection via JSON type field (CVSS 10.0)
- CVE-2026-25520: SandboxJS injection vulnerabilities (CVSS 10.0)

**Vulnerability**: Command injection via JSON parsing, JavaScript injection via unsanitized input.

**Mitigation**:
- Unicode normalization (NFKC)
- Invisible character removal (zero-width spaces, BOM)
- HTML tag stripping option
- File path traversal detection
- Input length limits

**Code Location**: `app/security_utils.py::sanitize_input_pipeline()`, `sanitize_html_input()`, `sanitize_file_path_input()`

---

### Pass 65: Output Encoding Framework
**CVEs**:
- CVE-2026-25643: Frigate go2rtc RCE via config.yaml command injection (CVSS 9.1)
- CVE-2026-25881: SandboxJS sandbox escape via prototype pollution (CVSS 9.0)

**Vulnerability**: XSS via unencoded output, command injection via configuration.

**Mitigation**:
- HTML entity encoding for HTML context
- JavaScript string escaping for JS context
- CSS value sanitization
- URL component encoding
- JSON serialization with XSS protection

**Code Location**: `app/security_utils.py::encode_html_output()`, `encode_javascript_output()`, `encode_css_output()`, `encode_url_output()`, `encode_json_output()`

---

### Pass 66: Session Management Integration
**CVEs**:
- CVE-2026-23646: Node.js session fixation and insufficient timeout
- CVE-2026-22341: IBM Security Verify Access OIDC session fixation

**Vulnerability**: Session fixation attacks, insufficient session timeouts, missing session binding.

**Mitigation**:
- Secure session store with crypto-random IDs
- Session ID regeneration on privilege change
- IP/User-Agent optional binding
- Dual timeout enforcement (absolute + idle)
- Session validation with comprehensive checks

**Code Location**: `app/security_utils.py::SecureSessionStore`

---

### Pass 67: File Operation Security
**CVEs**:
- CVE-2026-27897: Vociferous path traversal via export_file route (CVSS 9.8)
- CVE-2026-25766: Echo middleware.Static path traversal via backslash

**Vulnerability**: Path traversal in file operations, unsafe file reading/writing.

**Mitigation**:
- Path validation with base directory enforcement
- File size limits
- Atomic file writes
- Secure download headers
- File permission validation

**Code Location**: `app/security_utils.py::secure_file_read()`, `secure_file_write()`, `get_secure_download_headers()`

---

### Pass 68: API Security Hardening
**CVEs**:
- CVE-2026-25544: Payload CMS API SQL injection via JSON fields
- CVE-2026-1894: WeKan REST API authorization bypass

**Vulnerability**: API endpoint vulnerabilities, GraphQL query abuse, bulk operation DoS.

**Mitigation**:
- Per-endpoint rate limiting
- GraphQL query depth limiting
- Bulk operation size limits
- HTTP method validation
- API versioning security

**Code Location**: `app/security_utils.py::validate_api_request()`, `validate_graphql_query()`, `validate_bulk_operation()`, `API_RATE_LIMITS`

---

### Pass 69: Webhook Security
**CVEs**:
- CVE-2026-27488: OpenClaw Cron webhook SSRF (CVSS 9.8)
- CVE-2026-28467: OpenClaw attachment/media URL hydration SSRF

**Vulnerability**: SSRF via webhook URLs, missing webhook signature validation.

**Mitigation**:
- URL scheme enforcement (HTTPS only)
- Private IP range blocking (RFC 1918, localhost, metadata)
- Webhook signature generation/verification (HMAC-SHA256)
- Host allowlist support

**Code Location**: `app/security_utils.py::validate_webhook_url()`, `verify_webhook_signature()`, `generate_webhook_signature()`

---

### Pass 70: Background Job Security
**CVEs**:
- CVE-2026-25643: Frigate go2rtc RCE via config.yaml (CVSS 9.1)
- CVE-2026-25641: SandboxJS TOCTOU race condition

**Vulnerability**: Command injection in job payloads, race conditions in job processing.

**Mitigation**:
- Job type allowlist
- Payload dangerous pattern detection (eval, exec, system calls)
- Job payload size limits
- Job result sanitization
- Job execution sandboxing hooks

**Code Location**: `app/security_utils.py::validate_job_payload()`, `sanitize_job_result()`, `ALLOWED_JOB_TYPES`

---

### Pass 71: Cache Security
**CVEs**:
- CVE-2026-27897: Vociferous cache key injection leading to path traversal
- CVE-2026-2835: Pingora HTTP request smuggling via cache poisoning (CVSS 9.3)

**Vulnerability**: Cache key injection, cache poisoning, sensitive data in cache keys.

**Mitigation**:
- Cache key sanitization (control character removal)
- Long key hashing (SHA-256)
- Sensitive key pattern detection
- TTL validation and clamping
- Cache poisoning detection hooks

**Code Location**: `app/security_utils.py::sanitize_cache_key()`, `check_sensitive_cache_key()`, `validate_cache_ttl()`

---

### Pass 72: Email Security Integration
**CVEs**:
- CVE-2026-28289: FreeScout Mail2Shell RCE via filename sanitization bypass (CVSS 10.0)
- CVE-2026-24486: Python-Multipart path traversal in email parsing

**Vulnerability**: Email header injection, dangerous attachment handling, filename bypasses.

**Mitigation**:
- Email address sanitization (newline/CRLF detection)
- Subject line sanitization
- Dangerous attachment type blocking
- Content-Type validation for attachments
- Email address format validation

**Code Location**: `app/security_utils.py::sanitize_email_address()`, `sanitize_email_subject()`, `validate_email_attachment()`

---

### Pass 73: Notification Security
**CVEs**:
- CVE-2026-30839: Wallos webhook notification SSRF (CVSS 8.6)
- CVE-2026-30953: LinkAce SSRF via notifications (CVSS 7.7)

**Vulnerability**: SSRF via notification payloads, markdown link injection.

**Mitigation**:
- Notification payload size limits
- URL validation in notification payloads
- HTML content stripping
- Markdown link target removal
- Content length limits

**Code Location**: `app/security_utils.py::validate_notification_payload()`, `sanitize_notification_content()`

---

### Pass 74: Report Generation Security
**CVEs**:
- CVE-2026-26144: Microsoft Excel information disclosure via formula injection (zero-click)
- CVE-2026-28794: Prototype pollution in RPC JSON deserializer

**Vulnerability**: CSV/Excel formula injection, prototype pollution in report data.

**Mitigation**:
- CSV formula injection prevention (prefix with apostrophe)
- Secure CSV generation with field sanitization
- Report access control by role
- Report type allowlist
- Sensitive field redaction

**Code Location**: `app/security_utils.py::sanitize_csv_field()`, `generate_secure_csv()`, `validate_report_access()`

---

### Pass 75: Data Export Security
**CVEs**:
- CVE-2026-21536: Microsoft Devices Pricing Program RCE via file upload (CVSS 9.8)
- CVE-2026-27897: Path traversal in export functionality

**Vulnerability**: Path traversal in exports, unauthorized data export, sensitive data exposure.

**Mitigation**:
- Export format allowlist
- Export scope permissions (admin-only for "all" data)
- Row count limits
- Sensitive data masking in exports
- Export audit logging

**Code Location**: `app/security_utils.py::validate_export_request()`, `mask_sensitive_export_data()`

---

### Pass 76: Admin Panel Security
**CVEs**:
- CVE-2026-1731: BeyondTrust Remote Support command injection (CVSS 9.9)
- CVE-2026-22769: Dell RecoverPoint critical vulnerability (CVSS 10.0)

**Vulnerability**: Admin privilege escalation, command injection in admin functions, missing IP restrictions.

**Mitigation**:
- Admin-only action validation
- Critical action confirmation requirements
- Admin IP restriction support
- Admin session hardening
- Bulk action protection

**Code Location**: `app/security_utils.py::validate_admin_action()`, `check_admin_ip_restriction()`, `ADMIN_CRITICAL_ACTIONS`

---

### Pass 77: Audit Logging Integration
**CVEs**:
- CVE-2026-3494: Delta Electronics DRASim audit log bypass via newline injection
- CVE-2026-30928: ZOHO ManageEngine ADAudit Plus security bypass

**Vulnerability**: Audit log tampering, log injection, missing audit events.

**Mitigation**:
- Automatic sensitive action detection
- Data modification auditing
- Audit event integrity hashing
- IP address and user context capture
- Comprehensive audit trail generation

**Code Location**: `app/security_utils.py::should_audit_action()`, `create_audit_event()`, `SENSITIVE_ACTIONS`

---

### Pass 78: Configuration Security Integration
**CVEs**:
- CVE-2026-25253: Moltbook Supabase RLS misconfiguration (1.5M tokens exposed)
- CVE-2026-25643: Frigate config.yaml command injection

**Vulnerability**: Runtime configuration changes without authorization, command injection in config values, secret exposure.

**Mitigation**:
- Admin-only configuration changes
- Sensitive config key validation (minimum length)
- Config value command injection detection
- Runtime config change auditing
- Secret rotation support

**Code Location**: `app/security_utils.py::validate_runtime_config_change()`, `sanitize_config_value()`

---

### Pass 79: Security Monitoring Integration
**CVEs**:
- CVE-2026-1709: Keylime missing client-side TLS authentication (CVSS 9.4)
- CVE-2026-1568: Rapid7 Insight Platform authentication bypass (CVSS 9.6)

**Vulnerability**: Missing security event generation, undetected attacks, no anomaly detection.

**Mitigation**:
- Security event generation with severity levels
- Anomaly threshold detection
- Event type validation
- Source IP and user tracking
- Automated response trigger support

**Code Location**: `app/security_utils.py::generate_security_event()`, `check_anomaly_threshold()`, `SECURITY_EVENTS`

---

## Complete Security Pass Summary

| Pass | Function(s) | Primary Protection |
|------|-------------|-------------------|
| 1-19 | Baseline hardening | SQLite, SSH, XML, YAML, logging |
| 20-32 | Extended coverage | Supply chain, SSRF, DNS rebinding, ML security |
| 33 | `validate_jwt_algorithm()` | JWT bypass prevention |
| 34 | `validate_sql_column_alias()` | SQL injection |
| 35 | `parse_xml_securely()` | XXE prevention |
| 36 | `validate_file_extension()` | File upload security |
| 37 | `validate_redirect_url()` | Open redirect prevention |
| 38 | `validate_pickle_data()` | Deserialization safety |
| 39 | `regenerate_session_id()` | Session fixation |
| 40 | `get_clickjacking_protection_headers()` | Clickjacking |
| 41 | `escape_ldap_filter_value()` | LDAP injection |
| 42 | `sanitize_mongodb_query()` | NoSQL injection |
| 43 | `sanitize_http_header_value()` | Header injection |
| 44 | `sanitize_error_message()` | Info disclosure |
| 45 | `validate_config_file_permissions()` | Config security |
| 46 | `RateLimiter`, `check_rate_limit()` | Rate limiting |
| 47 | `validate_ldap_auth_response()` | Auth flow security |
| 48 | `generate_secure_api_key()` | Credential rotation |
| 49 | `generate_csrf_token()` | CSRF protection |
| 50 | `validate_websocket_origin()` | WebSocket security |
| 51 | `validate_cors_origin()` | CORS enforcement |
| 52 | `create_audit_log_entry()` | Audit integrity |
| 53 | `validate_configuration_security()` | Config validation |
| 54 | `sanitize_production_error()` | Error sanitization |
| 55 | `validate_session_timeout()` | Session timeout |
| 56 | `validate_upload_file_extension()` | Upload restriction |
| 57 | `validate_request_origin()` | Origin validation |
| 58 | `get_security_headers()` | Security headers |
| 59 | `validate_json_payload()` | Request validation |
| 60 | `validate_response_headers()` | Response security |
| 61 | `extract_auth_token()` | Auth middleware |
| 62 | `check_resource_access()` | Authorization |
| 63 | `validate_raw_query()` | Database security |
| 64 | `sanitize_input_pipeline()` | Input sanitization |
| 65 | `encode_html_output()` | Output encoding |
| 66 | `SecureSessionStore` | Session management |
| 67 | `secure_file_read()` | File operations |
| 68 | `validate_api_request()` | API security |
| 69 | `validate_webhook_url()` | Webhook security |
| 70 | `validate_job_payload()` | Job security |
| 71 | `sanitize_cache_key()` | Cache security |
| 72 | `sanitize_email_address()` | Email security |
| 73 | `validate_notification_payload()` | Notification security |
| 74 | `sanitize_csv_field()` | Report security |
| 75 | `validate_export_request()` | Export security |
| 76 | `validate_admin_action()` | Admin security |
| 77 | `should_audit_action()` | Audit logging |
| 78 | `validate_runtime_config_change()` | Config integration |
| 79 | `generate_security_event()` | Security monitoring |

---

## Summary

The NIS2 Field Audit Tool now implements **79 comprehensive security passes** covering:

- **Passes 1-19**: Baseline hardening
- **Passes 20-32**: Extended coverage (supply chain, SSRF, ML security)
- **Passes 33-45**: March 2026 CVE coverage (JWT, SQL, XXE, file uploads, etc.)
- **Passes 46-58**: Application consolidation (rate limiting, CSRF, CORS, etc.)
- **Passes 59-79**: Deep application integration (middleware, database, jobs, monitoring)

**Total: 79 security passes** addressing **70+ CVE patterns** from March 2026 research.

**Test Coverage: 277 security tests** (all passing)

---

*Last Updated: March 13, 2026*
*Security Passes 59-79 implemented based on March 2026 web research*


---

## Final Application Consolidation Phase (Passes 80-100) - March 2026

The following security passes complete the application consolidation phase, integrating supply chain security, container security, cloud metadata protection, hardcoded credential detection, and comprehensive application security hardening.

### Pass 80: Supply Chain Security Integration
**CVEs**:
- CVE-2026-28289: FreeScout Mail2Shell RCE via filename sanitization (CVSS 10.0)
- CVE-2026-29000: pac4j-jwt authentication bypass (CVSS 10.0)

**Vulnerability**: Malicious packages, dependency confusion, typosquatting attacks targeting application dependencies.

**Mitigation**:
- Package name validation against known vulnerable patterns (Log4j, FastJSON)
- Dependency confusion risk detection (private vs public package names)
- Known vulnerable package version detection
- Supply chain integrity validation

**Code Location**: `app/security_utils.py::validate_dependency_name()`, `check_dependency_confusion_risk()`, `VULNERABLE_PACKAGE_PATTERNS`

---

### Pass 81: Container Security Integration
**CVEs**:
- CVE-2026-3288: Kubernetes ingress-nginx configuration injection (CVSS 8.8)
- CVE-2026-0863: n8n Python sandbox container escape

**Vulnerability**: Container escape via privileged mode, dangerous capabilities, sensitive mount points.

**Mitigation**:
- Privileged container mode detection
- Dangerous capability validation (CAP_SYS_ADMIN, CAP_SYS_PTRACE, etc.)
- Sensitive mount point blocking (/proc/sys, /dev, docker.sock, etc.)
- Root user execution detection
- Container image tag validation (reject 'latest')

**Code Location**: `app/security_utils.py::validate_container_security_config()`, `sanitize_container_image_name()`, `DANGEROUS_CAPABILITIES`

---

### Pass 82: Cloud Metadata Protection
**CVEs**:
- CVE-2026-28467: OpenClaw SSRF to cloud metadata (CVSS 9.8)
- CVE-2026-27488: OpenClaw Cron webhook SSRF (CVSS 9.8)
- CVE-2026-27732: AVideo SSRF to AWS metadata

**Vulnerability**: SSRF attacks targeting cloud metadata endpoints (169.254.169.254) to steal IAM credentials.

**Mitigation**:
- Cloud metadata endpoint blocking (169.254.169.254, 169.254.169.253, 100.100.100.200)
- Link-local address filtering
- Metadata response sanitization (redact AccessKeyId, SecretAccessKey, Token)
- Cloud provider metadata service detection

**Code Location**: `app/security_utils.py::check_cloud_metadata_access()`, `sanitize_cloud_metadata_response()`, `CLOUD_METADATA_ENDPOINTS`

---

### Pass 83: Hardcoded Credential Detection
**CVEs**:
- CVE-2026-25202: Samsung MagicINFO hardcoded database credentials (CVSS 9.8)
- CVE-2026-22769: Dell RecoverPoint hardcoded credentials (CVSS 10.0)
- CVE-2026-22906: AES-ECB with hardcoded encryption key

**Vulnerability**: Hardcoded passwords, API keys, tokens, and private keys in source code and configuration.

**Mitigation**:
- Source code scanning for credential patterns
- Hardcoded password detection
- API key pattern recognition
- Private key detection (PEM format)
- AWS credential detection
- Configuration secret validation (reject non-env values)

**Code Location**: `app/security_utils.py::scan_for_hardcoded_credentials()`, `validate_no_hardcoded_secrets()`, `HARDCODED_CREDENTIAL_PATTERNS`

---

### Pass 84: SSRF Deep Protection
**CVEs**:
- CVE-2026-26019: LangChain RecursiveUrlLoader SSRF bypass (CVSS 5.3)
- CVE-2026-25493: Craft CMS SSRF via redirect bypass

**Vulnerability**: SSRF attacks using redirect chains, DNS rebinding, and URL parsing inconsistencies.

**Mitigation**:
- DNS resolution validation before HTTP requests
- Private IP range blocking at request time (not just validation)
- Dangerous URL scheme blocking (file://, gopher://, ldap://, dict://, ftp://)
- Redirect chain validation
- Time-of-check to time-of-use (TOCTOU) protection

**Code Location**: `app/security_utils.py::validate_url_deep_protection()`, `MAX_REDIRECTS`

---

### Pass 85: Code Injection Prevention
**CVEs**:
- CVE-2026-25632: EPyT-Flow OS command injection via JSON (CVSS 10.0)
- CVE-2026-25520: SandboxJS injection vulnerabilities (CVSS 10.0)

**Vulnerability**: Code injection via eval(), exec(), dynamic imports, and subprocess calls.

**Mitigation**:
- eval() and exec() call detection
- Dynamic import (__import__) detection
- Subprocess call validation
- os.system/os.popen detection
- compile() and execfile detection
- Safe code execution wrapper

**Code Location**: `app/security_utils.py::detect_code_injection()`, `safe_code_execution()`, `DANGEROUS_PYTHON_PATTERNS`

---

### Pass 86: Secure Defaults Enforcement
**Vulnerability**: Applications deployed with insecure default configurations (debug mode, disabled CSRF, etc.).

**Mitigation**:
- Debug mode enforcement (must be False in production)
- CSRF protection mandatory
- Secure cookie flags required
- HttpOnly cookie enforcement
- XSS protection mandatory
- Content-Security-Policy required
- Strict-Transport-Security required
- Missing default detection

**Code Location**: `app/security_utils.py::enforce_secure_defaults()`, `REQUIRED_SECURE_DEFAULTS`

---

### Pass 87: Dependency Version Pinning
**Vulnerability**: Unpinned dependencies leading to unexpected version updates and supply chain attacks.

**Mitigation**:
- Requirements file parsing for version pins
- Unpinned dependency detection
- ==, >=, <= operator validation
- Editable install validation
- Comment line handling

**Code Location**: `app/security_utils.py::validate_pinned_dependencies()`

---

### Pass 88: Secrets Rotation Tracking
**Vulnerability**: Long-lived secrets without rotation policies increasing exposure risk.

**Mitigation**:
- Secret registration with creation timestamp
- Rotation age tracking (default 90 days)
- Rotation due date calculation
- Configurable max age per secret
- Rotation recommendation generation

**Code Location**: `app/security_utils.py::SecretsRotationTracker`

---

### Pass 89: Secure Logging
**Vulnerability**: Log injection attacks via newline characters forging log entries.

**Mitigation**:
- Newline character removal from log messages
- Carriage return sanitization
- Log format validation
- Structured logging enforcement

**Code Location**: `app/security_utils.py::validate_log_format()`

---

### Pass 90: TLS/SSL Configuration Validation
**Vulnerability**: Weak TLS versions and cipher suites enabling downgrade attacks.

**Mitigation**:
- Minimum TLS version enforcement (TLSv1.2, TLSv1.3)
- Weak cipher suite detection (RC4, DES, 3DES, MD5, SHA1)
- TLS configuration validation
- Cipher suite allowlist

**Code Location**: `app/security_utils.py::validate_tls_config()`, `REQUIRED_TLS_VERSIONS`, `DISABLED_CIPHER_SUITES`

---

### Pass 91: API Versioning Security
**Vulnerability**: Access to deprecated or unsupported API versions with known vulnerabilities.

**Mitigation**:
- API version allowlist validation
- Unsupported version rejection
- Version deprecation warnings
- Security-only version support

**Code Location**: `app/security_utils.py::validate_api_version()`

---

### Pass 92: Request Timing Analysis
**Vulnerability**: Timing attacks analyzing response times to infer secret data.

**Mitigation**:
- Request timing tracking per endpoint
- Timing variance detection
- Anomaly threshold analysis
- Timing attack pattern recognition
- High variance alerting

**Code Location**: `app/security_utils.py::RequestTimingAnalyzer`

---

### Pass 93: Content Security Policy Validation
**Vulnerability**: Weak CSP policies allowing XSS and injection attacks.

**Mitigation**:
- unsafe-inline directive detection
- unsafe-eval directive detection
- Wildcard (*) source detection
- Strict CSP policy enforcement

**Code Location**: `app/security_utils.py::validate_csp_policy()`

---

### Pass 94: Password Policy Enforcement
**Vulnerability**: Weak passwords susceptible to brute force attacks.

**Mitigation**:
- Minimum length enforcement (12 characters)
- Uppercase letter requirement
- Lowercase letter requirement
- Digit requirement
- Special character requirement
- Policy validation with detailed feedback

**Code Location**: `app/security_utils.py::validate_password_policy()`

---

### Pass 95: File Upload Content Validation
**Vulnerability**: MIME type spoofing via fake file extensions.

**Mitigation**:
- Magic bytes validation for file types
- PNG signature detection
- JPEG signature detection
- PDF signature detection
- ZIP signature detection
- Content/MIME mismatch detection

**Code Location**: `app/security_utils.py::validate_file_content()`

---

### Pass 96: Network Policy Validation
**Vulnerability**: Overly permissive network policies allowing unauthorized access.

**Mitigation**:
- Allow-all egress policy detection
- SSH port (22) exposure detection
- RDP port (3389) exposure detection
- Sensitive port access validation
- Network segmentation validation

**Code Location**: `app/security_utils.py::validate_network_policy()`

---

### Pass 97: Resource Limit Enforcement
**Vulnerability**: Missing resource limits leading to DoS via resource exhaustion.

**Mitigation**:
- CPU limit requirement validation
- Memory limit requirement validation
- Resource quota enforcement
- Container resource validation
- Limit detection and alerting

**Code Location**: `app/security_utils.py::validate_resource_limits()`

---

### Pass 98: Health Check Security
**Vulnerability**: Sensitive information exposure via health check endpoints.

**Mitigation**:
- Standard endpoint validation (/health, /status, /ping)
- Non-standard endpoint detection
- Health endpoint access control
- Sensitive data exclusion from health responses

**Code Location**: `app/security_utils.py::validate_health_check_config()`

---

### Pass 99: Distributed Tracing Sanitization
**Vulnerability**: Sensitive data exposure in distributed tracing systems.

**Mitigation**:
- Password field redaction
- Token field redaction
- Secret field redaction
- Key field redaction
- Auth field redaction
- Trace data sanitization

**Code Location**: `app/security_utils.py::sanitize_trace_data()`

---

### Pass 100: Security Header Verification
**Vulnerability**: Missing security headers enabling various attacks.

**Mitigation**:
- Strict-Transport-Security presence validation
- X-Content-Type-Options validation
- X-Frame-Options validation
- Content-Security-Policy validation
- Required header enforcement
- Case-insensitive header checking

**Code Location**: `app/security_utils.py::verify_security_headers()`, `REQUIRED_SECURITY_HEADERS`

---

## Final Security Pass Summary (All 100 Passes)

| Pass | Function(s) | Primary Protection |
|------|-------------|-------------------|
| 80 | `validate_dependency_name()` | Supply chain security |
| 81 | `validate_container_security_config()` | Container security |
| 82 | `check_cloud_metadata_access()` | Cloud metadata protection |
| 83 | `scan_for_hardcoded_credentials()` | Credential detection |
| 84 | `validate_url_deep_protection()` | SSRF deep protection |
| 85 | `detect_code_injection()` | Code injection prevention |
| 86 | `enforce_secure_defaults()` | Secure defaults |
| 87 | `validate_pinned_dependencies()` | Dependency pinning |
| 88 | `SecretsRotationTracker` | Secrets rotation |
| 89 | `validate_log_format()` | Secure logging |
| 90 | `validate_tls_config()` | TLS validation |
| 91 | `validate_api_version()` | API versioning |
| 92 | `RequestTimingAnalyzer` | Timing analysis |
| 93 | `validate_csp_policy()` | CSP validation |
| 94 | `validate_password_policy()` | Password policy |
| 95 | `validate_file_content()` | File content validation |
| 96 | `validate_network_policy()` | Network policy |
| 97 | `validate_resource_limits()` | Resource limits |
| 98 | `validate_health_check_config()` | Health check security |
| 99 | `sanitize_trace_data()` | Trace sanitization |
| 100 | `verify_security_headers()` | Security headers |

---

## Summary

The NIS2 Field Audit Tool now implements **100 comprehensive security passes** covering:

- **Passes 1-19**: Baseline hardening
- **Passes 20-32**: Extended coverage (supply chain, SSRF, ML security)
- **Passes 33-45**: March 2026 CVE coverage (JWT, SQL, XXE, file uploads, etc.)
- **Passes 46-58**: Application consolidation phase 1 (rate limiting, CSRF, CORS, etc.)
- **Passes 59-79**: Application consolidation phase 2 (middleware, database, jobs, monitoring)
- **Passes 80-100**: Final consolidation phase (supply chain, containers, cloud metadata, credentials, application hardening)

**Total: 100 security passes** addressing **90+ CVE patterns** from March 2026 research.

**Test Coverage: 372 security tests** (all passing)

---

*Last Updated: March 13, 2026*
*Security Passes 80-100 implemented based on March 2026 web research for final application consolidation*


---

## UI/UX Security Hardening Phase (Passes 101-121) - March 2026

The following security passes focus on UI/UX security, addressing modern frontend vulnerabilities, framework-specific issues, and user interface attack vectors.

### Pass 101: SVG XSS Prevention
**CVEs**:
- CVE-2026-22610: Angular SVG script href/xlink:href XSS (CVSS 8.5)

**Vulnerability**: XSS via SVG `<script>` elements with unsanitized `href` and `xlink:href` attributes that execute JavaScript when processed by Angular's template compiler.

**Mitigation**:
- SVG script tag detection and blocking
- JavaScript URL pattern matching in href attributes
- foreignObject content validation
- External URL reference blocking in `<use>` elements

**Code Location**: `app/security_utils.py::sanitize_svg_content()`, `SVG_SCRIPT_DANGEROUS_ATTRS`

---

### Pass 102: Markdown XSS Prevention
**CVEs**:
- CVE-2026-25516: NiceGUI ui.markdown() XSS via unsanitized HTML
- CVE-2026-25054: n8n markdown XSS in workflow sticky notes

**Vulnerability**: XSS through markdown rendering that allows raw HTML passthrough, enabling JavaScript execution via event handlers and script tags.

**Mitigation**:
- HTML tag stripping (when HTML not explicitly allowed)
- Script tag detection in markdown content
- JavaScript URL blocking
- Event handler pattern detection (onerror, onload, etc.)

**Code Location**: `app/security_utils.py::sanitize_markdown_content()`, `MARKDOWN_DANGEROUS_PATTERNS`

---

### Pass 103: React Router ScrollRestoration XSS Prevention
**CVEs**:
- CVE-2026-21884: React Router ScrollRestoration XSS via getKey/storageKey (CVSS 7.2)

**Vulnerability**: XSS through the `getKey` and `storageKey` props in React Router's ScrollRestoration component, allowing script injection via scroll position keys.

**Mitigation**:
- Scroll key type validation (must be string)
- HTML character detection in keys
- JavaScript URL pattern blocking
- Event handler detection

**Code Location**: `app/security_utils.py::validate_scroll_restoration_key()`

---

### Pass 104-106: Prototype Pollution Deep Defense
**CVEs**:
- CVE-2026-26021: set-in npm prototype pollution via Array.prototype bypass
- CVE-2026-1774: CASL Ability prototype pollution (versions 2.4.0-6.7.4)
- CVE-2026-27837: dottie.js prototype pollution incomplete fix bypass

**Vulnerability**: Prototype pollution attacks that bypass traditional `__proto__` blocking by using Array.prototype or placing `__proto__` at non-first positions in dot-notation paths.

**Mitigation**:
- Deep recursive object scanning for prototype pollution patterns
- Array.prototype bypass detection
- Nested `__proto__` detection (not just at root level)
- Object key sanitization with recursive cleaning

**Code Location**: `app/security_utils.py::deep_prototype_pollution_check()`, `sanitize_object_keys()`, `PROTOTYPE_POLLUTION_KEYS`

---

### Pass 107: CSS Injection Prevention
**CVEs**:
- CVE-2026-26000: XWiki CSS injection leading to clickjacking

**Vulnerability**: CSS injection attacks via expression(), behavior(), and javascript: URLs in stylesheets that enable script execution and UI manipulation.

**Mitigation**:
- CSS expression() blocking (IE-specific)
- CSS behavior: URL blocking (IE HTCs)
- JavaScript URL detection in CSS url()
- @import with URL blocking
- CSS comment removal to prevent hidden malicious content

**Code Location**: `app/security_utils.py::sanitize_css_content()`, `CSS_DANGEROUS_PATTERNS`

---

### Pass 108: Advanced Clickjacking Prevention
**CVEs**:
- CVE-2026-24839: Dokploy clickjacking (missing X-Frame-Options)
- CVE-2026-23731: WeGIA clickjacking (missing CSP frame-ancestors)

**Vulnerability**: Clickjacking/UI redressing attacks via iframe embedding without proper frame-busting protections.

**Mitigation**:
- X-Frame-Options header generation (DENY/SAMEORIGIN)
- CSP frame-ancestors directive
- Frame-busting JavaScript generation
- Comprehensive header validation

**Code Location**: `app/security_utils.py::get_clickjacking_protection_headers()`, `generate_frame_busting_js()`

---

### Pass 109: Clipboard API Security
**CVEs**:
- CVE-2026-0890: Firefox DOM spoofing via Copy & Paste/Drag & Drop
- CVE-2026-20844: Windows Clipboard Server privilege escalation

**Vulnerability**: Clipboard content spoofing and privilege escalation via unsanitized clipboard operations.

**Mitigation**:
- Clipboard content sanitization based on expected MIME type
- Script tag detection in clipboard data
- JavaScript URL pattern blocking
- Clipboard operation type validation
- Clipboard data size limits

**Code Location**: `app/security_utils.py::sanitize_clipboard_content()`, `validate_clipboard_operation()`

---

### Pass 110-111: Tapjacking/Overlay Attack Prevention
**CVEs**:
- CVE-2025-48634: Android tapjacking via relayoutWindow
- CVE-2026-0007: Android tapjacking/overlay attack in WindowInfo

**Vulnerability**: Tapjacking attacks using overlay windows with click-through, invisible, or high z-index UI elements to trick users into unintended actions.

**Mitigation**:
- Overlay permission validation (SYSTEM_ALERT_WINDOW detection)
- Click-through CSS detection (pointer-events: none)
- Invisible overlay detection (opacity: 0)
- High z-index validation
- Touch event interception detection

**Code Location**: `app/security_utils.py::check_tapjacking_risk()`, `validate_overlay_permissions()`, `SUSPICIOUS_OVERLAY_PATTERNS`

---

### Pass 112-113: PWA Security
**CVEs**:
- CVE-2026-30240: Budibase PWA ZIP processing path traversal (CVSS 9.6)
- CVE-2026-28355: Canarytokens PWA XSS

**Vulnerability**: Path traversal via PWA ZIP processing and XSS through Progressive Web App manifest/service worker manipulation.

**Mitigation**:
- PWA manifest validation (secure start_url, scope path traversal detection)
- Service worker code validation (eval/Function detection)
- Required security header checking
- Display mode security validation

**Code Location**: `app/security_utils.py::validate_pwa_manifest()`, `validate_pwa_service_worker()`, `PWA_REQUIRED_HEADERS`

---

### Pass 114: Form Validation Security
**CVEs**:
- CVE-2026-24576: UX Flat WordPress plugin stored XSS via form input

**Vulnerability**: Client-side form validation bypass leading to XSS and unauthorized data modification via disabled/readonly field manipulation.

**Mitigation**:
- Unexpected form field detection
- Disabled field submission blocking
- Readonly field modification detection
- Field type validation (number, email, etc.)

**Code Location**: `app/security_utils.py::validate_form_data_security()`, `FORM_BYPASS_PATTERNS`

---

### Pass 115: Drag & Drop Security
**Vulnerability**: Malicious data exfiltration and script injection via drag and drop operations with dangerous MIME types.

**Mitigation**:
- Drag/drop MIME type validation
- JavaScript MIME type blocking
- Suspicious content type detection

**Code Location**: `app/security_utils.py::validate_drag_drop_operation()`

---

### Pass 116: Focus Management Security
**Vulnerability**: Focus stealing attacks that redirect user input to malicious UI elements.

**Mitigation**:
- Focus target validation against allowlist
- Unauthorized focus attempt detection
- Focus management audit logging

**Code Location**: `app/security_utils.py::validate_focus_management()`

---

### Pass 117: Notification/Toast Security
**Vulnerability**: XSS via notification content and notification flooding DoS attacks.

**Mitigation**:
- HTML tag stripping from notifications
- Markdown link target removal
- Notification length limiting (200 chars)
- Content sanitization

**Code Location**: `app/security_utils.py::sanitize_notification_content()`, `NOTIFICATION_MAX_LENGTH`

---

### Pass 118: Modal/Dialog Security
**Vulnerability**: Modal/dialog traps that prevent users from escaping malicious UI, or focus management issues enabling clickjacking.

**Mitigation**:
- Focus trapping validation
- Escape key handling verification
- Backdrop click-to-close validation
- Modal accessibility security

**Code Location**: `app/security_utils.py::validate_modal_security()`

---

### Pass 119: File Picker Security
**Vulnerability**: Malicious file uploads via file picker manipulation, type spoofing, and oversized files.

**Mitigation**:
- File type validation against allowlist
- File size limiting
- MIME type verification
- Dangerous file type blocking

**Code Location**: `app/security_utils.py::validate_file_picker_selection()`

---

### Pass 120: Animation/Transition Security
**Vulnerability**: Seizure-inducing rapid animations and performance-degrading infinite animations.

**Mitigation**:
- Animation duration limiting (max 5 seconds)
- Infinite iteration limiting
- Rapid flash protection (seizure prevention)
- Animation configuration sanitization

**Code Location**: `app/security_utils.py::sanitize_animation_config()`

---

### Pass 121: ARIA/Accessibility Security
**Vulnerability**: ARIA attribute manipulation for accessibility attacks and screen reader deception.

**Mitigation**:
- ARIA attribute allowlisting
- Invalid ARIA attribute removal
- ARIA value sanitization (HTML/JS stripping)
- Accessibility API security

**Code Location**: `app/security_utils.py::sanitize_aria_attributes()`

---

## Complete Security Pass Summary (All 121 Passes)

| Pass | Function(s) | Primary Protection |
|------|-------------|-------------------|
| 101 | `sanitize_svg_content()` | SVG XSS prevention |
| 102 | `sanitize_markdown_content()` | Markdown XSS prevention |
| 103 | `validate_scroll_restoration_key()` | ScrollRestoration XSS |
| 104-106 | `deep_prototype_pollution_check()` | Prototype pollution defense |
| 107 | `sanitize_css_content()` | CSS injection prevention |
| 108 | `get_clickjacking_protection_headers()` | Clickjacking prevention |
| 109 | `sanitize_clipboard_content()` | Clipboard security |
| 110-111 | `check_tapjacking_risk()` | Tapjacking prevention |
| 112-113 | `validate_pwa_manifest()` | PWA security |
| 114 | `validate_form_data_security()` | Form validation security |
| 115 | `validate_drag_drop_operation()` | Drag & drop security |
| 116 | `validate_focus_management()` | Focus security |
| 117 | `sanitize_notification_content()` | Notification security |
| 118 | `validate_modal_security()` | Modal/dialog security |
| 119 | `validate_file_picker_selection()` | File picker security |
| 120 | `sanitize_animation_config()` | Animation security |
| 121 | `sanitize_aria_attributes()` | ARIA/accessibility security |

---

## Summary

The NIS2 Field Audit Tool now implements **121 comprehensive security passes** covering:

- **Passes 1-19**: Baseline hardening
- **Passes 20-32**: Extended coverage (supply chain, SSRF, ML security)
- **Passes 33-45**: March 2026 CVE coverage (JWT, SQL, XXE, file uploads, etc.)
- **Passes 46-58**: Application consolidation phase 1 (rate limiting, CSRF, CORS, etc.)
- **Passes 59-79**: Application consolidation phase 2 (middleware, database, jobs, monitoring)
- **Passes 80-100**: Final consolidation phase (supply chain, containers, cloud metadata, credentials)
- **Passes 101-121**: UI/UX security phase (SVG/markdown XSS, prototype pollution, CSS injection, clickjacking, clipboard, PWA, form validation, accessibility)

**Total: 121 security passes** addressing **110+ CVE patterns** from March 2026 research.

**Test Coverage: 475 security tests** (all passing)

---

*Last Updated: March 13, 2026*
*Security Passes 101-121 implemented based on March 2026 web research for UI/UX security hardening*


---

## User Experience Enhancement Phase (Passes 122-142) - March 2026

The following passes focus on making the NIS2 audit tool user-friendly and accessible, especially for users who may not be technical experts. While most NIS2 compliance solutions are enterprise web platforms, this TUI application provides a lightweight, terminal-based alternative that prioritizes accessibility and ease of use.

### Pass 122: User Preference Management
**Feature**: Persistent user preferences for personalized experience

**User Benefits**:
- Theme customization (default, high contrast, colorblind-friendly, monochrome)
- Font size adjustment (small, medium, large)
- Animation and sound preferences
- Auto-save configuration
- Date/time format preferences

**Code Location**: `app/user_experience.py::UserPreferences`, `PreferenceManager`

---

### Pass 123: Accessibility Theme Engine
**Feature**: Color themes designed for accessibility

**Research**: WCAG 2.2 guidelines for color contrast and non-text content

**Available Themes**:
- **Default**: Standard color scheme
- **High Contrast**: Maximum contrast for low vision users (black/white)
- **Colorblind Deuteranopia**: Blue-yellow palette (red-green safe)
- **Colorblind Protanopia**: Avoids red tones
- **Monochrome**: Grayscale only, relies on symbols not colors

**Code Location**: `app/user_experience.py::ThemeMode`, `ThemeEngine`

---

### Pass 124: Contextual Help System
**Feature**: On-screen help relevant to current context

**User Benefits**:
- Help content specific to current screen/function
- Keyboard shortcuts reference
- Tips and best practices
- No need to consult external documentation

**Code Location**: `app/user_experience.py::HelpSystem`

---

### Pass 125: Progress Feedback System
**Feature**: Accessible progress tracking for long operations

**User Benefits**:
- Visual progress bars
- Screen reader announcements ("50% complete, step 5 of 10")
- ETA calculation
- Cancellation support

**Code Location**: `app/user_experience.py::ProgressTracker`

---

### Pass 126: Confirmation Dialog System
**Feature**: Clear confirmation for destructive actions

**User Benefits**:
- Prevents accidental data loss
- Severity-based visual indicators
- Clear action labels (not just "OK/Cancel")
- Bulk operation warnings

**Code Location**: `app/user_experience.py::ConfirmationDialog`

---

### Pass 127: Undo/Redo System
**Feature**: Recover from mistakes with undo/redo

**User Benefits**:
- Undo accidental deletions
- History of recent actions
- Redo accidentally undone actions
- Peace of mind for new users

**Code Location**: `app/user_experience.py::UndoManager`

---

### Pass 128: Auto-Save Functionality
**Feature**: Automatic data protection

**User Benefits**:
- Work is never lost
- Configurable save intervals
- Manual save option
- Clear save status indicators

**Code Location**: `app/user_experience.py::AutoSaveManager`

---

### Pass 129: Search and Filter System
**Feature**: Find data quickly with accessible search

**User Benefits**:
- Search across all fields or specific fields
- Filter by multiple criteria
- Results summary with clear counts
- Search history

**Code Location**: `app/user_experience.py::SearchFilter`

---

### Pass 130: Keyboard Navigation Helper
**Feature**: Multiple keyboard navigation modes

**Modes**:
- **Default**: Arrow keys, Enter, Escape
- **Vim**: H/J/K/L navigation for power users

**User Benefits**:
- Keyboard-only operation (no mouse required)
- Familiar shortcuts for different user backgrounds
- Help reference for shortcuts

**Code Location**: `app/user_experience.py::KeyboardNavigation`

---

### Pass 131: Notification System
**Feature**: User-friendly notifications with accessibility

**User Benefits**:
- Visual and screen reader notifications
- Different levels (info, success, warning, error)
- Symbols not just colors (✓ for success, not just green)
- Dismissible notifications

**Code Location**: `app/user_experience.py::NotificationManager`

---

### Pass 132: User Onboarding Wizard
**Feature**: Guided first-time setup

**Steps**:
1. Welcome introduction
2. Preference configuration
3. First device setup
4. First audit walkthrough
5. Getting started tips

**User Benefits**:
- Reduces learning curve
- No blank screen confusion
- Guided initial configuration
- Skip option for experienced users

**Code Location**: `app/user_experience.py::OnboardingWizard`

---

### Pass 133: Validation Feedback System
**Feature**: Clear form validation messages

**User Benefits**:
- Specific field-level error messages
- Warnings for potentially problematic inputs
- Clear formatting of multiple issues
- Success confirmation

**Code Location**: `app/user_experience.py::ValidationFeedback`

---

### Pass 134: Audit Trail Visualization
**Feature**: Accessible audit history display

**User Benefits**:
- Timeline view of audit events
- Summary statistics
- Who did what and when
- Screen reader friendly format

**Code Location**: `app/user_experience.py::AuditTrailVisualizer`

---

### Pass 135: Export Preview System
**Feature**: Preview exports before saving

**Supported Formats**:
- JSON: Pretty-printed preview
- CSV: Table preview (first 5 rows)
- PDF: Description of what will be generated
- HTML: Description of styled output

**User Benefits**:
- Verify data before export
- Understand what will be included
- Choose right format for needs

**Code Location**: `app/user_experience.py::ExportPreview`

---

### Pass 136: Batch Operation Manager
**Feature**: Perform operations on multiple items

**User Benefits**:
- Progress tracking for bulk operations
- Success/failure summary
- Time estimates
- Cancel capability

**Code Location**: `app/user_experience.py::BatchOperationManager`

---

### Pass 137: Data Backup and Restore
**Feature**: Protect audit data with backups

**User Benefits**:
- Automatic backup creation
- List available backups
- Restore from any backup point
- Data protection against corruption

**Code Location**: `app/user_experience.py::BackupManager`

---

### Pass 138: Error Recovery System
**Feature**: Helpful error messages with recovery steps

**User Benefits**:
- Not just "Error occurred" but "Here's how to fix it"
- Specific guidance for common issues:
  - Connection failures
  - Authentication problems
  - Permission denied
  - Timeouts

**Code Location**: `app/user_experience.py::ErrorRecovery`

---

### Pass 139: Screen Reader Support
**Feature**: Output formatting for assistive technologies

**Features**:
- Heading level announcements
- List position indicators ("1 of 5")
- Table row/column reading
- Dynamic content announcements

**Research**: GitHub CLI accessibility improvements, NVDA/VoiceOver compatibility

**Code Location**: `app/user_experience.py::ScreenReaderSupport`

---

### Pass 140: Configuration Wizard
**Feature**: Interactive initial setup

**Configuration Areas**:
- Company information (name, sector, entity type)
- Audit settings (frequency, auto-reports)
- Compliance framework selection
- Risk threshold configuration

**User Benefits**:
- No manual config file editing
- Guided step-by-step setup
- Progress tracking
- Review before apply

**Code Location**: `app/user_experience.py::ConfigurationWizard`

---

### Pass 141: Quick Action Shortcuts
**Feature**: Function key shortcuts for common actions

**Shortcuts**:
- F1: Help
- F2: Save
- F3: Search
- F4: Filter
- F5: Refresh
- F6: Export
- F7: New Item
- F9: Settings
- Ctrl+Q: Quit
- Ctrl+Z: Undo

**Code Location**: `app/user_experience.py::QuickActions`

---

### Pass 142: User Feedback Collector
**Feature**: Built-in mechanism for user feedback

**User Benefits**:
- Report bugs from within the app
- Suggest features
- Rate usability
- Track feedback history

**Code Location**: `app/user_experience.py::FeedbackCollector`

---

## Complete Feature Summary (All 142 Passes)

| Pass | Category | Feature | User Benefit |
|------|----------|---------|--------------|
| 122 | UX | Preference Management | Personalized experience |
| 123 | Accessibility | Theme Engine | Visual accessibility |
| 124 | UX | Contextual Help | Self-service support |
| 125 | UX | Progress Tracking | Operation visibility |
| 126 | UX | Confirmation Dialogs | Accident prevention |
| 127 | UX | Undo/Redo | Mistake recovery |
| 128 | UX | Auto-Save | Data protection |
| 129 | UX | Search & Filter | Find data quickly |
| 130 | Accessibility | Keyboard Navigation | Mouse-free operation |
| 131 | UX | Notifications | Status awareness |
| 132 | UX | Onboarding Wizard | Reduced learning curve |
| 133 | UX | Validation Feedback | Clear error messages |
| 134 | UX | Audit Trail | Activity visibility |
| 135 | UX | Export Preview | Verify before export |
| 136 | UX | Batch Operations | Efficiency |
| 137 | UX | Backup/Restore | Data safety |
| 138 | UX | Error Recovery | Self-service fixes |
| 139 | Accessibility | Screen Reader Support | Assistive tech compatibility |
| 140 | UX | Configuration Wizard | Easy setup |
| 141 | UX | Quick Actions | Speed |
| 142 | UX | Feedback Collector | User voice |

---

## Final Project Statistics

- **Total Security Passes**: 121 (1-121)
- **Total UX Passes**: 21 (122-142)
- **Total Passes**: 142
- **Security Test Cases**: 475
- **UX Test Cases**: 80
- **Total Test Cases**: 555 (all passing)
- **Lines of Security Code**: ~8,885
- **Lines of UX Code**: ~1,000
- **CVE Patterns Addressed**: 110+
- **Accessibility Standards**: WCAG 2.2 AA alignment

---

## Why TUI for NIS2 Auditing?

While most NIS2 compliance solutions are web-based enterprise platforms (Mindsec, DataGuard, JFrog, Lansweeper, etc.), this TUI application offers unique advantages:

1. **Lightweight**: No web server, database server, or complex infrastructure
2. **Portable**: Runs on any system with Python and terminal access
3. **Secure**: No network exposure, runs locally
4. **Accessible**: Screen reader friendly, keyboard-only operation
5. **Fast**: No browser overhead, instant response
6. **Familiar**: Terminal interface for system administrators
7. **Offline**: Works without internet connectivity
8. **Customizable**: Full source code availability

---

*Last Updated: March 13, 2026*
*Security Passes 1-121: Security hardening based on March 2026 CVE research*
*UX Passes 122-142: User experience and accessibility enhancements*
