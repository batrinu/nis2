# Security

## Overview

This is a local CLI application for NIS2 compliance assessment. Security considerations:

### Data Storage
- SQLite database with WAL mode enabled
- File permissions set to 0o600 for sensitive files
- Data stored locally on auditor's machine

### Input Validation
- Path traversal protection for file operations
- Input sanitization for user-provided data
- String length limits

### SSH Connections
- Uses Paramiko for SSH connections
- Strict host key verification enabled
- Dangerous commands blocked

### Reporting
No security vulnerabilities expected in normal use.

## Reporting Security Issues

Contact the maintainers directly for security concerns.
