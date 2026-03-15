"""
Device inventory table for the TUI.
RomEnglish localization: Technical terms in English, actions in Romanian.
"""
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from ..models import NetworkDevice
from ..i18n import get_text as _


console = Console()


def render_device_table(devices: List[NetworkDevice], title: str = "") -> Table:
    """
    Render a table of network devices.
    
    Args:
        devices: List of NetworkDevice objects
        title: Table title (defaults to localized "Device Inventory")
    
    Returns:
        Rich Table
    """
    if not title:
        title = f"{_('device')} Inventory"
    """
    Render a table of network devices.
    
    Args:
        devices: List of NetworkDevice objects
        title: Table title
    
    Returns:
        Rich Table
    """
    table = Table(
        title=title,
        box=box.ROUNDED,
        show_header=True,
        header_style="bold blue",
        expand=True,
    )
    
    table.add_column("#", style="dim", width=3)
    table.add_column(_("ip_address").title(), style="cyan", width=15)
    table.add_column(_("hostname").title(), style="green", width=20)
    table.add_column("Vendor", style="yellow", width=12)
    table.add_column(_("type").title(), style="magenta", width=12)
    table.add_column("OS/Versiune", style="dim", width=20)
    table.add_column(f"{_('ports').title()} Deschise", style="blue", width=15)
    table.add_column(_("status").title(), width=10)
    
    if not devices:
        table.add_row(
            "-", "-", f"Niciun {_('device').lower()} descoperit", "-",
            "-", "-", "-", "-"
        )
        return table
    
    for i, device in enumerate(devices, 1):
        # Format open ports
        ports_str = ", ".join(str(p) for p in device.open_ports[:5])
        if len(device.open_ports) > 5:
            ports_str += f" (+{len(device.open_ports) - 5})"
        
        # Status indicator
        status = device.connection_status
        status_style = {
            "connected": f"[green]● {_('connected').title()}[/green]",
            "pending": f"[yellow]○ {_('waiting').title()}[/yellow]",
            "failed": f"[red]✗ {_('error').title()}[/red]",
            "not_attempted": f"[dim]- {_('not_available').title()}[/dim]",
        }.get(status, status)
        
        # Vendor badge
        vendor_badge = device.vendor or _("unknown").title()
        if device.vendor == "Cisco":
            vendor_badge = "[blue]Cisco[/blue]"
        elif device.vendor == "Juniper":
            vendor_badge = "[magenta]Juniper[/magenta]"
        elif device.vendor == "MikroTik":
            vendor_badge = "[red]MikroTik[/red]"
        elif device.vendor == "Fortinet":
            vendor_badge = "[yellow]Fortinet[/yellow]"
        
        # Device type emoji
        device_type = device.device_type or "unknown"
        type_emoji = {
            "router": f"[yellow]🌐 {_('router').title()}[/yellow]",
            "switch": f"[blue]🔌 {_('switch').title()}[/blue]",
            "firewall": f"[red]🛡️ {_('firewall').title()}[/red]",
            "server": "[green]🖥️ Server[/green]",
            "workstation": "[dim]💻 Workstation[/dim]",
            "network_device": f"[cyan]📡 {_('network').title()}[/cyan]",
            "unknown": f"[dim]❓ {_('unknown').title()}[/dim]",
        }.get(device_type, device_type)
        
        table.add_row(
            str(i),
            device.ip_address,
            device.hostname or "-",
            vendor_badge,
            type_emoji,
            device.os_version or "-",
            ports_str or "-",
            status_style,
        )
    
    return table


def render_device_summary(devices: List[NetworkDevice]) -> Panel:
    """
    Render a summary panel of device counts.
    
    Args:
        devices: List of NetworkDevice objects
    
    Returns:
        Rich Panel
    """
    # Count by type
    type_counts = {}
    vendor_counts = {}
    connected_count = 0
    pending_count = 0
    failed_count = 0
    
    for device in devices:
        # Type counts
        device_type = device.device_type or "unknown"
        type_counts[device_type] = type_counts.get(device_type, 0) + 1
        
        # Vendor counts
        vendor = device.vendor or "Unknown"
        vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1
        
        # Connection status
        if device.connection_status == "connected":
            connected_count += 1
        elif device.connection_status == "pending":
            pending_count += 1
        elif device.connection_status == "failed":
            failed_count += 1
    
    # Build summary text
    summary = Text()
    
    summary.append(f"Total {_('devices').title()}: ", style="bold")
    summary.append(f"{len(devices)}\n", style="bold white")
    
    # Type breakdown
    if type_counts:
        summary.append(f"\nDupă {_('type').title()}:\n", style="bold blue")
        for dtype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            emoji = {
                "router": "🌐",
                "switch": "🔌",
                "firewall": "🛡️",
                "server": "🖥️",
                "workstation": "💻",
                "network_device": "📡",
                "unknown": "❓",
            }.get(dtype, "•")
            summary.append(f"  {emoji} {dtype.capitalize()}: ", style="dim")
            summary.append(f"{count}\n", style="white")
    
    # Vendor breakdown (top 5)
    if vendor_counts:
        summary.append("\nTop Vendori:\n", style="bold green")
        for vendor, count in sorted(vendor_counts.items(), key=lambda x: -x[1])[:5]:
            summary.append(f"  • {vendor}: ", style="dim")
            summary.append(f"{count}\n", style="white")
    
    # Connection status
    if devices:
        summary.append(f"\n{_('connection').title()} {_('status').title()}:\n", style="bold cyan")
        summary.append(f"  ● {_('connected').title()}: ", style="dim green")
        summary.append(f"{connected_count}\n", style="green")
        summary.append(f"  ○ {_('waiting').title()}: ", style="dim yellow")
        summary.append(f"{pending_count}\n", style="yellow")
        summary.append(f"  ✗ {_('error').title()}: ", style="dim red")
        summary.append(f"{failed_count}\n", style="red")
    
    return Panel(summary, title=_("summary").title(), border_style="blue")


def display_device_inventory(devices: List[NetworkDevice], session_name: str = ""):
    """
    Display full device inventory with table and summary.
    
    Args:
        devices: List of NetworkDevice objects
        session_name: Optional session name for title
    """
    title = f"{_('device')} Inventory{f' - {session_name}' if session_name else ''}"
    
    # Print summary
    console.print()
    console.print(render_device_summary(devices))
    
    # Print table
    console.print()
    console.print(render_device_table(devices, title))
    console.print()
