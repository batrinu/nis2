"""
NIS2 audit commands for Cisco IOS/IOS-XE devices.
"""
from typing import Dict, List, Any


# NIS2-relevant show commands for Cisco IOS
CISCO_IOS_COMMANDS = {
    # System Information
    "show_version": {
        "command": "show version",
        "description": "System version, uptime, and hardware info",
        "category": "system",
        "nis2_relevance": "Firmware/patch compliance",
    },
    "show_running_config": {
        "command": "show running-config",
        "description": "Current running configuration",
        "category": "config",
        "nis2_relevance": "Full config review",
    },
    "show_startup_config": {
        "command": "show startup-config",
        "description": "Startup configuration",
        "category": "config",
        "nis2_relevance": "Config persistence check",
    },
    
    # Security - Access Control
    "show_access_lists": {
        "command": "show access-lists",
        "description": "Access control lists",
        "category": "security",
        "nis2_relevance": "Access control measures",
    },
    "show_ip_interface_brief": {
        "command": "show ip interface brief",
        "description": "Interface IP addresses and status",
        "category": "network",
        "nis2_relevance": "Network segmentation",
    },
    "show_vlan_brief": {
        "command": "show vlan brief",
        "description": "VLAN configuration",
        "category": "network",
        "nis2_relevance": "Network segmentation",
    },
    
    # Security - Services
    "show_cdp_neighbors": {
        "command": "show cdp neighbors detail",
        "description": "CDP neighbor information",
        "category": "network",
        "nis2_relevance": "Topology discovery",
    },
    "show_lldp_neighbors": {
        "command": "show lldp neighbors detail",
        "description": "LLDP neighbor information",
        "category": "network",
        "nis2_relevance": "Topology discovery",
    },
    
    # Management - Logging & Time
    "show_logging": {
        "command": "show logging",
        "description": "Syslog configuration",
        "category": "management",
        "nis2_relevance": "Logging for incident detection",
    },
    "show_ntp_status": {
        "command": "show ntp status",
        "description": "NTP synchronization status",
        "category": "management",
        "nis2_relevance": "Time synchronization for logs",
    },
    "show_ntp_associations": {
        "command": "show ntp associations",
        "description": "NTP peer associations",
        "category": "management",
        "nis2_relevance": "Time source verification",
    },
    
    # Security - SNMP
    "show_snmp_community": {
        "command": "show snmp community",
        "description": "SNMP community strings",
        "category": "security",
        "nis2_relevance": "SNMP security (weak communities)",
    },
    "show_snmp_group": {
        "command": "show snmp group",
        "description": "SNMP groups",
        "category": "security",
        "nis2_relevance": "SNMPv3 configuration",
    },
    "show_snmp_user": {
        "command": "show snmp user",
        "description": "SNMP users",
        "category": "security",
        "nis2_relevance": "SNMPv3 users",
    },
    
    # Security - SSH
    "show_ip_ssh": {
        "command": "show ip ssh",
        "description": "SSH server configuration",
        "category": "security",
        "nis2_relevance": "SSH version and settings",
    },
    "show_ssh": {
        "command": "show ssh",
        "description": "Active SSH sessions",
        "category": "security",
        "nis2_relevance": "Active management sessions",
    },
    
    # Security - AAA
    "show_aaa_sessions": {
        "command": "show aaa sessions",
        "description": "AAA sessions",
        "category": "security",
        "nis2_relevance": "Authentication audit",
    },
    "show_privilege": {
        "command": "show privilege",
        "description": "Current privilege level",
        "category": "security",
        "nis2_relevance": "Authorization levels",
    },
    
    # Security - Users
    "show_users": {
        "command": "show users",
        "description": "Logged in users",
        "category": "security",
        "nis2_relevance": "Active sessions monitoring",
    },
    "show_line": {
        "command": "show line",
        "description": "Line (vty, console) configuration",
        "category": "security",
        "nis2_relevance": "Access line security",
    },
    
    # Security - Port Security
    "show_port_security": {
        "command": "show port-security",
        "description": "Port security status",
        "category": "security",
        "nis2_relevance": "Port-level access control",
    },
    "show_port_security_interface": {
        "command": "show port-security interface",
        "description": "Per-interface port security",
        "category": "security",
        "nis2_relevance": "Port security details",
    },
    "show_storm_control": {
        "command": "show storm-control",
        "description": "Storm control configuration",
        "category": "security",
        "nis2_relevance": "DoS protection",
    },
    
    # Network - Routing
    "show_ip_route": {
        "command": "show ip route",
        "description": "IP routing table",
        "category": "network",
        "nis2_relevance": "Network topology",
    },
    "show_ip_protocols": {
        "command": "show ip protocols",
        "description": "Active routing protocols",
        "category": "network",
        "nis2_relevance": "Routing security",
    },
    "show_ip_ospf_neighbor": {
        "command": "show ip ospf neighbor",
        "description": "OSPF neighbors",
        "category": "network",
        "nis2_relevance": "Dynamic routing audit",
    },
    "show_ip_bgp_summary": {
        "command": "show ip bgp summary",
        "description": "BGP peer summary",
        "category": "network",
        "nis2_relevance": "BGP security",
    },
    
    # VPN
    "show_crypto_isakmp_sa": {
        "command": "show crypto isakmp sa",
        "description": "IPsec IKE SAs",
        "category": "vpn",
        "nis2_relevance": "VPN tunnel status",
    },
    "show_crypto_ipsec_sa": {
        "command": "show crypto ipsec sa",
        "description": "IPsec SAs",
        "category": "vpn",
        "nis2_relevance": "VPN encryption status",
    },
    
    # Resilience
    "show_spanning_tree_summary": {
        "command": "show spanning-tree summary",
        "description": "STP status summary",
        "category": "resilience",
        "nis2_relevance": "Network resilience",
    },
    "show_spanning_tree_root": {
        "command": "show spanning-tree root",
        "description": "STP root bridges",
        "category": "resilience",
        "nis2_relevance": "STP topology",
    },
    "show_etherchannel_summary": {
        "command": "show etherchannel summary",
        "description": "EtherChannel status",
        "category": "resilience",
        "nis2_relevance": "Link redundancy",
    },
    "show_vtp_status": {
        "command": "show vtp status",
        "description": "VTP configuration",
        "category": "network",
        "nis2_relevance": "VLAN management security",
    },
    
    # DHCP
    "show_ip_dhcp_snooping": {
        "command": "show ip dhcp snooping",
        "description": "DHCP snooping status",
        "category": "security",
        "nis2_relevance": "DHCP security",
    },
    "show_ip_dhcp_snooping_binding": {
        "command": "show ip dhcp snooping binding",
        "description": "DHCP snooping bindings",
        "category": "security",
        "nis2_relevance": "IP-MAC binding verification",
    },
    
    # ARP inspection
    "show_ip_arp_inspection": {
        "command": "show ip arp inspection",
        "description": "Dynamic ARP inspection",
        "category": "security",
        "nis2_relevance": "ARP spoofing protection",
    },
    
    # IPv6
    "show_ipv6_interface_brief": {
        "command": "show ipv6 interface brief",
        "description": "IPv6 interface status",
        "category": "network",
        "nis2_relevance": "IPv6 deployment status",
    },
    
    # Policy
    "show_policy_map": {
        "command": "show policy-map",
        "description": "QoS policy maps",
        "category": "network",
        "nis2_relevance": "Traffic management",
    },
    "show_class_map": {
        "command": "show class-map",
        "description": "QoS class maps",
        "category": "network",
        "nis2_relevance": "Traffic classification",
    },
}


def get_cisco_ios_commands(
    categories: List[str] = None,
    nis2_only: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Get Cisco IOS commands filtered by category.
    
    Args:
        categories: List of categories to include (None = all)
        nis2_only: Only return commands with NIS2 relevance
    
    Returns:
        Dict of command definitions
    """
    commands = CISCO_IOS_COMMANDS.copy()
    
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
        List of CLI command strings
    """
    commands = get_cisco_ios_commands(categories, nis2_only)
    return [cmd["command"] for cmd in commands.values()]


# High priority commands for quick audits
QUICK_AUDIT_COMMANDS = [
    "show version",
    "show running-config",
    "show ip interface brief",
    "show access-lists",
    "show logging",
    "show ntp status",
    "show ip ssh",
    "show snmp community",
    "show vlan brief",
    "show users",
]

# Security-focused commands
SECURITY_AUDIT_COMMANDS = [
    "show version",
    "show running-config",
    "show access-lists",
    "show ip ssh",
    "show snmp community",
    "show snmp group",
    "show snmp user",
    "show port-security",
    "show ip dhcp snooping",
    "show ip arp inspection",
    "show line",
    "show logging",
    "show users",
    "show privilege",
]

# Compliance commands for full audit
FULL_COMPLIANCE_COMMANDS = list(CISCO_IOS_COMMANDS.keys())
