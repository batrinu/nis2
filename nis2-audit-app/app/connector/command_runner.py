"""
Command runner for executing NIS2 audit commands on devices.
"""
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from ..models import NetworkDevice, DeviceCommandResult, DeviceConfig
from .device_manager import DeviceConnector, ConnectionManager
from .command_sets.cisco_ios import get_command_list as get_cisco_commands
from .command_sets.generic_linux import get_command_list as get_linux_commands


class CommandRunner:
    """
    Executes NIS2 audit commands and stores results.
    """
    
    # Map device types to command set functions
    COMMAND_SETS = {
        "cisco_ios": get_cisco_commands,
        "cisco_xe": get_cisco_commands,
        "cisco_asa": get_cisco_commands,
        "cisco_nxos": get_cisco_commands,
        "linux": get_linux_commands,
        "generic_linux": get_linux_commands,
    }
    
    def __init__(self, connection_manager: ConnectionManager):
        self.cm = connection_manager
    
    def get_commands_for_device(self, device: NetworkDevice) -> List[str]:
        """
        Get appropriate NIS2 audit commands for device type.
        
        Args:
            device: NetworkDevice to get commands for
        
        Returns:
            List of command strings
        """
        # Determine device type key
        device_type_key = None
        
        if device.vendor:
            vendor_lower = device.vendor.lower()
            if "cisco" in vendor_lower:
                device_type_key = "cisco_ios"
            elif device.device_type == "server":
                device_type_key = "linux"
        
        if not device_type_key:
            device_type_key = device.device_type or "unknown"
        
        # Get commands
        command_func = self.COMMAND_SETS.get(device_type_key, get_linux_commands)
        return command_func(categories=None, nis2_only=True)
    
    def run_audit_on_device(
        self,
        device: NetworkDevice,
        commands: Optional[List[str]] = None,
        progress_callback: Optional[callable] = None
    ) -> List[DeviceCommandResult]:
        """
        Run audit commands on a connected device.
        
        Args:
            device: Device to audit
            commands: Optional specific commands (auto-detected if None)
            progress_callback: Optional callback(cmd_index, total, command)
        
        Returns:
            List of command results
        """
        connector = self.cm.get_connection(device.device_id)
        if not connector:
            raise RuntimeError(f"Device {device.device_id} not connected")
        
        # Get commands if not provided
        if commands is None:
            commands = self.get_commands_for_device(device)
        
        results = []
        total = len(commands)
        
        for i, command in enumerate(commands):
            if progress_callback:
                progress_callback(i + 1, total, command)
            
            start_time = datetime.now(timezone.utc)
            
            try:
                output = connector.execute_command(command)
                success = True
                error_message = None
            except Exception as e:
                logger.warning(f"Command execution failed: {e}")
                output = ""
                success = False
                error_message = str(e)
            
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            result = DeviceCommandResult(
                command=command,
                raw_output=output,
                success=success,
                error_message=error_message,
                execution_time_ms=duration_ms,
            )
            
            results.append(result)
        
        return results
    
    def run_quick_audit(self, device: NetworkDevice) -> List[DeviceCommandResult]:
        """
        Run quick audit (subset of commands) on device.
        
        Args:
            device: Device to audit
        
        Returns:
            List of command results
        """
        from .command_sets.cisco_ios import QUICK_AUDIT_COMMANDS as CISCO_QUICK
        from .command_sets.generic_linux import QUICK_AUDIT_COMMANDS as LINUX_QUICK
        
        # Determine which quick commands to use
        if device.vendor and "cisco" in device.vendor.lower():
            commands = CISCO_QUICK
        else:
            commands = LINUX_QUICK
        
        return self.run_audit_on_device(device, commands)
    
    def run_security_audit(self, device: NetworkDevice) -> List[DeviceCommandResult]:
        """
        Run security-focused audit on device.
        
        Args:
            device: Device to audit
        
        Returns:
            List of command results
        """
        from .command_sets.cisco_ios import SECURITY_AUDIT_COMMANDS as CISCO_SEC
        from .command_sets.generic_linux import SECURITY_AUDIT_COMMANDS as LINUX_SEC
        
        # Determine which security commands to use
        if device.vendor and "cisco" in device.vendor.lower():
            commands = CISCO_SEC
        else:
            commands = LINUX_SEC
        
        return self.run_audit_on_device(device, commands)


class ConfigParser:
    """
    Parse device configurations for analysis.
    """
    
    @staticmethod
    def parse_cisco_version(output: str) -> Dict[str, Any]:
        """
        Parse 'show version' output from Cisco IOS.
        
        Args:
            output: Command output
        
        Returns:
            Dict with parsed info
        """
        info = {
            "version": None,
            "image": None,
            "uptime": None,
            "hardware": [],
            "serial": [],
            "config_register": None,
        }
        
        for line in output.split("\n"):
            # Version
            if "Cisco IOS Software" in line or "IOS-XE Software" in line:
                match = re.search(r"Version ([^,]+)", line)
                if match:
                    info["version"] = match.group(1).strip()
            
            # System image
            if "System image file is" in line:
                match = re.search(r'"([^"]+)"', line)
                if match:
                    info["image"] = match.group(1)
            
            # Uptime
            if "uptime is" in line.lower():
                match = re.search(r"uptime is (.+)", line, re.IGNORECASE)
                if match:
                    info["uptime"] = match.group(1).strip()
            
            # Hardware
            if line.startswith("cisco") and "processor" in line.lower():
                info["hardware"].append(line.strip())
            
            # Serial number
            if "Processor board ID" in line:
                match = re.search(r"Processor board ID (\S+)", line)
                if match:
                    info["serial"].append(match.group(1))
            
            # Config register
            if "Configuration register is" in line:
                match = re.search(r"Configuration register is (\S+)", line)
                if match:
                    info["config_register"] = match.group(1)
        
        return info
    
    @staticmethod
    def parse_linux_uname(output: str) -> Dict[str, Any]:
        """
        Parse 'uname -a' output from Linux.
        
        Args:
            output: Command output
        
        Returns:
            Dict with parsed info
        """
        info = {
            "kernel": None,
            "hostname": None,
            "kernel_release": None,
            "kernel_version": None,
            "machine": None,
            "os": None,
        }
        
        parts = output.split()
        if len(parts) >= 2:
            info["kernel"] = parts[0]
            info["hostname"] = parts[1]
        if len(parts) >= 3:
            info["kernel_release"] = parts[2]
        if len(parts) >= 4:
            info["kernel_version"] = parts[3]
        if len(parts) >= 5:
            info["machine"] = parts[4]
        if len(parts) >= 6:
            info["os"] = " ".join(parts[5:])
        
        return info
    
    @classmethod
    def extract_config_info(
        cls,
        command_results: List[DeviceCommandResult],
        vendor: Optional[str] = None
    ) -> DeviceConfig:
        """
        Extract configuration information from command results.
        
        Args:
            command_results: List of command results
            vendor: Optional vendor hint
        
        Returns:
            DeviceConfig with extracted info
        """
        config = DeviceConfig()
        
        # Find running config
        for result in command_results:
            if not result.success:
                continue
            
            cmd = result.command.lower()
            output = result.raw_output
            
            # Running config
            if "show running-config" in cmd or "show run" in cmd:
                config.running_config = output
            
            # Startup config
            if "show startup-config" in cmd or "show start" in cmd:
                config.startup_config = output
            
            # Version
            if "show version" in cmd or cmd.startswith("uname"):
                if vendor and "cisco" in vendor.lower():
                    version_info = cls.parse_cisco_version(output)
                    config.firmware_version = version_info.get("version")
                elif "uname" in cmd:
                    uname_info = cls.parse_linux_uname(output)
                    config.firmware_version = uname_info.get("kernel_release")
            
            # Hostname
            if "hostnamectl" in cmd:
                for line in output.split("\n"):
                    if line.startswith("Static hostname:"):
                        config.hostname = line.split(":", 1)[1].strip()
            
            # NTP
            if "ntp" in cmd:
                config.ntp_servers = cls._extract_ntp_servers(output)
            
            # Syslog
            if "logging" in cmd or "rsyslog" in cmd:
                config.syslog_servers = cls._extract_syslog_servers(output)
            
            # SNMP
            if "snmp" in cmd:
                config.snmp_community = cls._extract_snmp_community(output)
            
            # SSH
            if "ip ssh" in cmd or "sshd_config" in cmd:
                config.ssh_version = cls._extract_ssh_version(output)
        
        return config
    
    @staticmethod
    def _extract_ntp_servers(output: str) -> List[str]:
        """Extract NTP servers from output."""
        servers = []
        for line in output.split("\n"):
            if "ntp server" in line.lower():
                match = re.search(r"ntp server (\S+)", line, re.IGNORECASE)
                if match:
                    servers.append(match.group(1))
            if "server" in line and "." in line:
                # Linux ntp.conf style
                parts = line.split()
                if len(parts) >= 2 and "." in parts[1]:
                    servers.append(parts[1])
        return servers
    
    @staticmethod
    def _extract_syslog_servers(output: str) -> List[str]:
        """Extract syslog servers from output."""
        servers = []
        for line in output.split("\n"):
            if "logging" in line and "." in line:
                match = re.search(r"logging (\d+\.\d+\.\d+\.\d+)", line)
                if match:
                    servers.append(match.group(1))
        return servers
    
    @staticmethod
    def _extract_snmp_community(output: str) -> Optional[str]:
        """Extract SNMP community string (sanitized)."""
        for line in output.split("\n"):
            if "community" in line.lower():
                return "configured"
        return None
    
    @staticmethod
    def _extract_ssh_version(output: str) -> Optional[str]:
        """Extract SSH version."""
        for line in output.split("\n"):
            if "version" in line.lower():
                match = re.search(r"version (\d+)", line, re.IGNORECASE)
                if match:
                    return match.group(1)
        return None


def sanitize_config(config_text: str) -> str:
    """
    Remove sensitive information from configuration.
    
    Args:
        config_text: Raw configuration text
    
    Returns:
        Sanitized configuration
    """
    # Patterns to sanitize
    patterns = [
        (r'(password \S+) \S+', r'\1 <REDACTED>'),
        (r'(secret \S+) \S+', r'\1 <REDACTED>'),
        (r'(snmp-server community) \S+', r'\1 <REDACTED>'),
        (r'(username \S+ password) \S+', r'\1 <REDACTED>'),
        (r'(enable password) \S+', r'\1 <REDACTED>'),
        (r'(enc.*password) .+', r'\1 <REDACTED>'),
        (r'priv-key[\s\S]*?-----END', '<REDACTED>'),
    ]
    
    sanitized = config_text
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    
    return sanitized
