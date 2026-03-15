"""
Command sets for different device types.
"""
from .cisco_ios import (
    get_cisco_ios_commands,
    get_command_list as get_cisco_command_list,
    QUICK_AUDIT_COMMANDS as CISCO_QUICK_COMMANDS,
    SECURITY_AUDIT_COMMANDS as CISCO_SECURITY_COMMANDS,
)
from .generic_linux import (
    get_linux_commands,
    get_command_list as get_linux_command_list,
    QUICK_AUDIT_COMMANDS as LINUX_QUICK_COMMANDS,
    SECURITY_AUDIT_COMMANDS as LINUX_SECURITY_COMMANDS,
)

__all__ = [
    # Cisco
    "get_cisco_ios_commands",
    "get_cisco_command_list",
    "CISCO_QUICK_COMMANDS",
    "CISCO_SECURITY_COMMANDS",
    # Linux
    "get_linux_commands",
    "get_linux_command_list",
    "LINUX_QUICK_COMMANDS",
    "LINUX_SECURITY_COMMANDS",
]
