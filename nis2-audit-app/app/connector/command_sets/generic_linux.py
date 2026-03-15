"""
NIS2 audit commands for Generic Linux servers/firewalls.
"""
from typing import Dict, List, Any


# NIS2-relevant commands for Linux systems
LINUX_COMMANDS = {
    # System Information
    "uname": {
        "command": "uname -a",
        "description": "Kernel version and system info",
        "category": "system",
        "nis2_relevance": "OS version/patch compliance",
    },
    "os_release": {
        "command": "cat /etc/os-release",
        "description": "OS distribution info",
        "category": "system",
        "nis2_relevance": "OS identification",
    },
    "hostnamectl": {
        "command": "hostnamectl",
        "description": "System hostname and chassis info",
        "category": "system",
        "nis2_relevance": "System identification",
    },
    "uptime": {
        "command": "uptime",
        "description": "System uptime and load",
        "category": "system",
        "nis2_relevance": "Availability metrics",
    },
    "date": {
        "command": "date",
        "description": "Current system time",
        "category": "system",
        "nis2_relevance": "Time synchronization check",
    },
    
    # Kernel & Boot
    "kernel_cmdline": {
        "command": "cat /proc/cmdline",
        "description": "Kernel boot parameters",
        "category": "system",
        "nis2_relevance": "Boot security options",
    },
    "sysctl": {
        "command": "sysctl -a",
        "description": "Kernel parameters",
        "category": "security",
        "nis2_relevance": "Security hardening parameters",
    },
    "sysctl_crypto": {
        "command": "sysctl crypto",
        "description": "Crypto-related kernel parameters",
        "category": "security",
        "nis2_relevance": "Cryptographic settings",
    },
    
    # Network - Interfaces
    "ip_addr": {
        "command": "ip addr",
        "description": "Network interface configuration",
        "category": "network",
        "nis2_relevance": "Network interface inventory",
    },
    "ip_link": {
        "command": "ip link",
        "description": "Network interface status",
        "category": "network",
        "nis2_relevance": "Interface state",
    },
    "ip_route": {
        "command": "ip route",
        "description": "Routing table",
        "category": "network",
        "nis2_relevance": "Network topology",
    },
    "ss_listening": {
        "command": "ss -tlnp",
        "description": "Listening TCP sockets with processes",
        "category": "network",
        "nis2_relevance": "Exposed services audit",
    },
    "ss_udp": {
        "command": "ss -ulnp",
        "description": "Listening UDP sockets with processes",
        "category": "network",
        "nis2_relevance": "UDP services audit",
    },
    
    # Firewall
    "iptables": {
        "command": "iptables -L -n -v",
        "description": "IPv4 firewall rules",
        "category": "security",
        "nis2_relevance": "Network access control",
    },
    "ip6tables": {
        "command": "ip6tables -L -n -v",
        "description": "IPv6 firewall rules",
        "category": "security",
        "nis2_relevance": "IPv6 firewall rules",
    },
    "nft_list_ruleset": {
        "command": "nft list ruleset",
        "description": "nftables ruleset",
        "category": "security",
        "nis2_relevance": "Modern firewall rules",
    },
    "firewalld_status": {
        "command": "firewall-cmd --state && firewall-cmd --list-all",
        "description": "Firewalld status and configuration",
        "category": "security",
        "nis2_relevance": "FirewallD configuration",
    },
    "ufw_status": {
        "command": "ufw status verbose",
        "description": "UFW firewall status",
        "category": "security",
        "nis2_relevance": "UFW firewall rules",
    },
    
    # SSH
    "sshd_config": {
        "command": "cat /etc/ssh/sshd_config",
        "description": "SSH server configuration",
        "category": "security",
        "nis2_relevance": "SSH hardening",
    },
    "ssh_config": {
        "command": "cat /etc/ssh/ssh_config",
        "description": "SSH client configuration",
        "category": "security",
        "nis2_relevance": "SSH client settings",
    },
    "sshd_process": {
        "command": "ps aux | grep sshd",
        "description": "SSH daemon process",
        "category": "security",
        "nis2_relevance": "SSH service status",
    },
    
    # Users & Authentication
    "passwd_file": {
        "command": "cat /etc/passwd",
        "description": "User accounts",
        "category": "security",
        "nis2_relevance": "User account inventory",
    },
    "shadow_file": {
        "command": "sudo cat /etc/shadow 2>/dev/null || echo 'Permission denied'",
        "description": "Password hashes (if accessible)",
        "category": "security",
        "nis2_relevance": "Password storage",
    },
    "group_file": {
        "command": "cat /etc/group",
        "description": "Group definitions",
        "category": "security",
        "nis2_relevance": "Group membership",
    },
    "sudoers": {
        "command": "sudo cat /etc/sudoers 2>/dev/null || cat /etc/sudoers.d/* 2>/dev/null || echo 'Permission denied'",
        "description": "Sudo configuration",
        "category": "security",
        "nis2_relevance": "Privilege escalation controls",
    },
    "logged_in_users": {
        "command": "who",
        "description": "Currently logged in users",
        "category": "security",
        "nis2_relevance": "Active sessions",
    },
    "last_logins": {
        "command": "last -20",
        "description": "Recent login history",
        "category": "security",
        "nis2_relevance": "Access audit trail",
    },
    "failed_logins": {
        "command": "lastb -10 2>/dev/null || echo 'No failed login data available'",
        "description": "Failed login attempts",
        "category": "security",
        "nis2_relevance": "Brute force detection",
    },
    
    # Authentication & PAM
    "pam_common_auth": {
        "command": (
            "cat /etc/pam.d/common-auth 2>/dev/null || "
            "cat /etc/pam.d/system-auth 2>/dev/null || "
            "echo 'PAM config not found'"
        ),
        "description": "PAM authentication configuration",
        "category": "security",
        "nis2_relevance": "Authentication policy",
    },
    "login_defs": {
        "command": "cat /etc/login.defs",
        "description": "Login configuration",
        "category": "security",
        "nis2_relevance": "Password policy settings",
    },
    
    # Logging
    "rsyslog_config": {
        "command": "cat /etc/rsyslog.conf",
        "description": "Rsyslog configuration",
        "category": "logging",
        "nis2_relevance": "Logging configuration",
    },
    "rsyslog_d": {
        "command": "ls -la /etc/rsyslog.d/ 2>/dev/null || echo 'No rsyslog.d directory'",
        "description": "Rsyslog additional configs",
        "category": "logging",
        "nis2_relevance": "Additional logging rules",
    },
    "journalctl_disk_usage": {
        "command": "journalctl --disk-usage 2>/dev/null || echo 'journald not available'",
        "description": "Systemd journal size",
        "category": "logging",
        "nis2_relevance": "Log retention",
    },
    "logrotate_config": {
        "command": "cat /etc/logrotate.conf",
        "description": "Log rotation configuration",
        "category": "logging",
        "nis2_relevance": "Log lifecycle management",
    },
    
    # Time Synchronization
    "timedatectl": {
        "command": "timedatectl",
        "description": "Time sync status",
        "category": "logging",
        "nis2_relevance": "NTP configuration",
    },
    "ntp_status": {
        "command": "ntpq -p 2>/dev/null || chronyc sources 2>/dev/null || echo 'NTP client not available'",
        "description": "NTP peer status",
        "category": "logging",
        "nis2_relevance": "Time source verification",
    },
    
    # Services
    "systemctl_list": {
        "command": "systemctl list-unit-files --state=enabled --type=service",
        "description": "Enabled systemd services",
        "category": "system",
        "nis2_relevance": "Running services inventory",
    },
    "systemctl_running": {
        "command": "systemctl --state=running --type=service",
        "description": "Currently running services",
        "category": "system",
        "nis2_relevance": "Active services",
    },
    "inetd_services": {
        "command": "cat /etc/inetd.conf 2>/dev/null || echo 'inetd not in use'",
        "description": "Inetd super-server services",
        "category": "system",
        "nis2_relevance": "Legacy services",
    },
    "xinetd_services": {
        "command": "ls /etc/xinetd.d/ 2>/dev/null || echo 'xinetd not in use'",
        "description": "Xinetd services",
        "category": "system",
        "nis2_relevance": "Legacy services",
    },
    
    # Processes
    "process_list": {
        "command": "ps aux",
        "description": "Running processes",
        "category": "system",
        "nis2_relevance": "Process inventory",
    },
    "top_snapshot": {
        "command": "top -b -n 1 | head -20",
        "description": "Top processes snapshot",
        "category": "system",
        "nis2_relevance": "Resource utilization",
    },
    
    # Storage
    "disk_usage": {
        "command": "df -h",
        "description": "Disk usage",
        "category": "system",
        "nis2_relevance": "Storage capacity for backups",
    },
    "mount_points": {
        "command": "mount | grep -v cgroup",
        "description": "Mount points",
        "category": "system",
        "nis2_relevance": "Filesystem layout",
    },
    "fstab": {
        "command": "cat /etc/fstab",
        "description": "Filesystem table",
        "category": "system",
        "nis2_relevance": "Mount configuration",
    },
    
    # Crypto
    "openssl_version": {
        "command": "openssl version",
        "description": "OpenSSL version",
        "category": "crypto",
        "nis2_relevance": "Cryptographic library version",
    },
    "crypto_policies": {
        "command": "update-crypto-policies --show 2>/dev/null || echo 'Crypto policies not available'",
        "description": "System crypto policy",
        "category": "crypto",
        "nis2_relevance": "Cryptographic policy",
    },
    
    # Certificates
    "ca_bundle": {
        "command": "ls -la /etc/ssl/certs/ | head -20",
        "description": "CA certificates",
        "category": "crypto",
        "nis2_relevance": "Trust store",
    },
    
    # SELinux/AppArmor
    "selinux_status": {
        "command": "sestatus 2>/dev/null || echo 'SELinux not available'",
        "description": "SELinux status",
        "category": "security",
        "nis2_relevance": "Mandatory access control",
    },
    "apparmor_status": {
        "command": "aa-status 2>/dev/null || echo 'AppArmor not available'",
        "description": "AppArmor status",
        "category": "security",
        "nis2_relevance": "Mandatory access control",
    },
    
    # Filesystem Integrity
    "aide_status": {
        "command": "aide --check 2>&1 | head -5 || echo 'AIDE not installed'",
        "description": "AIDE filesystem integrity",
        "category": "security",
        "nis2_relevance": "Integrity checking",
    },
    
    # Audit
    "audit_status": {
        "command": "auditctl -s 2>/dev/null || echo 'Auditd not available'",
        "description": "Audit subsystem status",
        "category": "logging",
        "nis2_relevance": "Kernel auditing",
    },
    "audit_rules": {
        "command": "cat /etc/audit/audit.rules 2>/dev/null || auditctl -l 2>/dev/null || echo 'No audit rules'",
        "description": "Audit rules",
        "category": "logging",
        "nis2_relevance": "Security event auditing",
    },
    
    # Container/Virtualization
    "docker_info": {
        "command": "docker info 2>/dev/null || echo 'Docker not available'",
        "description": "Docker information",
        "category": "system",
        "nis2_relevance": "Container runtime security",
    },
    "docker_ps": {
        "command": "docker ps -a 2>/dev/null || echo 'Docker not available'",
        "description": "Docker containers",
        "category": "system",
        "nis2_relevance": "Container inventory",
    },
    "virsh_list": {
        "command": "virsh list --all 2>/dev/null || echo 'libvirt not available'",
        "description": "KVM/QEMU VMs",
        "category": "system",
        "nis2_relevance": "Virtualization inventory",
    },
}


def get_linux_commands(
    categories: List[str] = None,
    nis2_only: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Get Linux commands filtered by category.
    
    Args:
        categories: List of categories to include (None = all)
        nis2_only: Only return commands with NIS2 relevance
    
    Returns:
        Dict of command definitions
    """
    commands = LINUX_COMMANDS.copy()
    
    if categories:
        commands = {
            k: v for k, v in commands.items()
            if v["category"] in categories
        }
    
    if nis2_only:
        commands = {
            k: v for k, v in commands.items()
            if v.get("nis2_relevance")
        }
    
    return commands


def get_command_list(
    categories: List[str] = None,
    nis2_only: bool = True
) -> List[str]:
    """
    Get list of command strings.
    
    Args:
        categories: Filter by categories
        nis2_only: NIS2 relevant only
    
    Returns:
        List of shell command strings
    """
    commands = get_linux_commands(categories, nis2_only)
    return [cmd["command"] for cmd in commands.values()]


# Quick audit command list
QUICK_AUDIT_COMMANDS = [
    "uname -a",
    "cat /etc/os-release",
    "ip addr",
    "ss -tlnp",
    "iptables -L -n -v",
    "cat /etc/ssh/sshd_config",
    "cat /etc/passwd",
    "cat /etc/sudoers",
    "who",
    "last -20",
    "cat /etc/rsyslog.conf",
    "timedatectl",
    "systemctl list-unit-files --state=enabled --type=service",
    "df -h",
    "openssl version",
]

# Security-focused commands
SECURITY_AUDIT_COMMANDS = [
    "uname -a",
    "sysctl -a",
    "ip addr",
    "iptables -L -n -v",
    "cat /etc/ssh/sshd_config",
    "cat /etc/passwd",
    "cat /etc/group",
    "cat /etc/sudoers",
    "who",
    "last -20",
    "cat /etc/pam.d/common-auth",
    "cat /etc/login.defs",
    "sestatus",
    "aa-status",
    "auditctl -s",
    "auditctl -l",
]
