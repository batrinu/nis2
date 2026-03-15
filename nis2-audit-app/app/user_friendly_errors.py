"""
User-friendly error translations for the NIS2 Field Audit Tool.

Converts technical error messages into plain English that non-technical
users can understand and act upon.
"""
from typing import Dict, Tuple, Optional


# Error pattern mappings: (technical_pattern, user_friendly_message, suggested_action)
ERROR_TRANSLATIONS: Dict[str, Tuple[str, str]] = {
    # Network/Connection errors
    "connection refused": (
        "Couldn't reach the device",
        "Check if the device is powered on and connected to the network. "
        "Verify the IP address is correct."
    ),
    "connection timed out": (
        "Taking longer than expected to connect",
        "The device might be busy or the network is slow. "
        "Try again in a moment, or check your network connection."
    ),
    "timeout": (
        "This is taking longer than expected",
        "Try again or check your network connection."
    ),
    "no route to host": (
        "Can't find a path to the device",
        "Check if the device is on the same network. "
        "Verify the IP address and network settings."
    ),
    "network is unreachable": (
        "Network connection issue",
        "Check your network connection and try again."
    ),
    
    # Authentication errors
    "authentication failed": (
        "Username or password didn't work",
        "Double-check your username and password. "
        "Make sure Caps Lock is off."
    ),
    "permission denied": (
        "Need different credentials",
        "Check your username and password. "
        "You may need admin or enable credentials for this device."
    ),
    "invalid credentials": (
        "Login information is incorrect",
        "Double-check your username and password and try again."
    ),
    
    # SSH errors
    "ssh": (
        "Secure connection issue",
        "Check if SSH is enabled on the device. "
        "Verify the port number (default is 22)."
    ),
    "host key verification failed": (
        "Device identity couldn't be verified",
        "This might be a security issue. Contact your IT team if you're unsure."
    ),
    
    # Database errors
    "database is locked": (
        "Another operation is in progress",
        "Wait a moment and try again. If this keeps happening, restart the app."
    ),
    "disk full": (
        "Not enough storage space",
        "Free up some disk space and try again. "
        "You can delete old reports or temporary files."
    ),
    
    # Scan errors
    "nmap": (
        "Network scan couldn't complete",
        "Make sure nmap is installed. Try running with fewer devices or a smaller network range."
    ),
    "invalid target": (
        "The network address doesn't look right",
        "Check the IP address or network range. Use format like 192.168.1.0/24"
    ),
    
    # File errors
    "permission denied": (
        "Can't save file to that location",
        "Choose a different folder, like your Documents folder. "
        "Make sure you have permission to write to that location."
    ),
    "file not found": (
        "Couldn't find the file",
        "Check the file path and make sure the file exists."
    ),
    "no such file or directory": (
        "File or folder not found",
        "Check the path and try again."
    ),
    
    # Validation errors
    "invalid ip": (
        "The IP address doesn't look right",
        "Use format like 192.168.1.1 (four numbers separated by dots)"
    ),
    "invalid cidr": (
        "The network range doesn't look right",
        "Use format like 192.168.1.0/24 (IP address with / and a number)"
    ),
    "value error": (
        "Something you entered isn't quite right",
        "Please check your input and try again."
    ),
    
    # Generic errors
    "internal error": (
        "Something unexpected happened",
        "Please try again. If this keeps happening, restart the app or contact support."
    ),
    "not implemented": (
        "This feature isn't available yet",
        "This feature is coming soon! Check for updates."
    ),
}


def translate_error(error_message: str, error_type: Optional[str] = None) -> Dict[str, str]:
    """
    Translate a technical error message into user-friendly language.
    
    Args:
        error_message: The original error message
        error_type: Optional error type/category
        
    Returns:
        Dictionary with:
        - title: Short user-friendly title
        - message: Detailed explanation
        - action: Suggested next steps
        - original: Original error (for debugging)
    """
    error_lower = error_message.lower()
    
    # Try to find a matching pattern
    for pattern, (title, action) in ERROR_TRANSLATIONS.items():
        if pattern in error_lower:
            return {
                "title": title,
                "message": title,  # Title is also the main message
                "action": action,
                "original": error_message,
            }
    
    # Default fallback for unknown errors
    return {
        "title": "Something went wrong",
        "message": "We encountered an unexpected issue",
        "action": (
            "Try again. If this keeps happening, try restarting the app. "
            "You can also check the logs for more details (F1 > Help)."
        ),
        "original": error_message,
    }


def format_error_for_display(error_translation: Dict[str, str]) -> str:
    """
    Format an error translation for display in the TUI.
    
    Args:
        error_translation: Output from translate_error()
        
    Returns:
        Formatted error string with box drawing characters
    """
    title = error_translation.get("title", "Error")
    action = error_translation.get("action", "Please try again.")
    
    lines = [
        "╔" + "═" * 58 + "╗",
        "║" + title.center(58) + "║",
        "╠" + "═" * 58 + "╣",
    ]
    
    # Wrap action text
    words = action.split()
    line = "║ "
    for word in words:
        if len(line) + len(word) + 1 > 57:
            lines.append(line.ljust(57) + " ║")
            line = "║ " + word + " "
        else:
            line += word + " "
    lines.append(line.ljust(57) + " ║")
    
    lines.append("╚" + "═" * 58 + "╝")
    
    return "\n".join(lines)


# Specific error handlers for common operations

class ErrorRecoverySuggestions:
    """Provides recovery suggestions for specific error scenarios."""
    
    @staticmethod
    def for_connection_error(device_ip: str) -> str:
        return (
            f"Couldn't connect to {device_ip}. Try these steps:\n"
            "1. Check if the device is powered on\n"
            "2. Verify the IP address is correct\n"
            "3. Make sure you're on the same network\n"
            "4. Check if SSH/telnet is enabled on the device"
        )
    
    @staticmethod
    def for_scan_error(target: str) -> str:
        return (
            f"Couldn't scan {target}. Try these steps:\n"
            "1. Check if the network range is correct\n"
            "2. Make sure nmap is installed\n"
            "3. Try a smaller range first (e.g., /28 instead of /24)\n"
            "4. Check your firewall settings"
        )
    
    @staticmethod
    def for_export_error(file_path: str) -> str:
        return (
            f"Couldn't save report to {file_path}. Try these steps:\n"
            "1. Choose a different folder (like Documents)\n"
            "2. Check if you have permission to write there\n"
            "3. Make sure the disk isn't full\n"
            "4. Try a different filename"
        )
    
    @staticmethod
    def for_database_error() -> str:
        return (
            "Database issue detected. Try these steps:\n"
            "1. Restart the application\n"
            "2. Check if your disk has free space\n"
            "3. Make sure no other instance is running\n"
            "4. If problems persist, restore from backup"
        )


# Success messages for positive feedback
SUCCESS_MESSAGES = {
    "audit_complete": "🎉 Audit completed successfully!",
    "scan_complete": "✓ Network scan finished",
    "device_connected": "✓ Connected to device",
    "report_exported": "✓ Report saved successfully",
    "session_saved": "✓ Session saved",
    "finding_resolved": "✓ Finding marked as resolved",
    "settings_updated": "✓ Settings updated",
}


def get_success_message(key: str, details: str = "") -> str:
    """Get a success message with optional details."""
    base = SUCCESS_MESSAGES.get(key, "✓ Success!")
    if details:
        return f"{base} {details}"
    return base
