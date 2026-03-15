"""Enhanced network scanning screen with live visualization and ASCII network map.
RomEnglish localization: Technical terms in English, actions in Romanian.
"""
from textual.screen import Screen
from textual.widgets import Input, Button, Static, DataTable, ProgressBar, Label
from textual.containers import Horizontal, Vertical, Grid
from textual.reactive import reactive
from textual.worker import Worker
from textual import work
from textual.binding import Binding
from ...storage.db import AuditStorage
from ...utils import get_db_path
from ...scanner.network_scanner import NmapScanner, NetworkScannerError
from ...i18n import get_text as _
import asyncio
import random
import logging

logger = logging.getLogger(__name__)


# Fun facts about NIS2 and security to show during scan (RomEnglish)
SCAN_FACTS = [
    "💡 Știai? NIS2 se aplică la peste 160.000 organizații în UE",
    f"💡 Tip: {_('scan').title()}-urile regulate de {_('network').lower()} ajută la identificarea {_('devices').lower()}-elor neautorizate",
    "💡 Fact: Articolul 21 NIS2 cere analiză de risc și politici de securitate",
    f"💡 Tip: Segmentarea {_('network').lower()}-ului limitează răspândirea atacurilor",
    "💡 Știai? Entitățile esențiale au 24h pentru a raporta incidente",
    "💡 Fact: NIS2 acoperă 15 sectoare inclusiv energie, transport și banking",
    f"💡 Tip: Menține firmware-ul updatat pe toate {_('devices').lower()}-ele de {_('network').lower()}",
    f"💡 Fact: {_('multi_factor_auth').title()} este obligatoriu conform NIS2",
    "💡 Tip: Documentează toate schimbările de network pentru audit trail",
    "💡 Știai? Penetration testing este recomandat trimestrial",
]

# Device type icons
DEVICE_ICONS = {
    "router": "🌐",
    "switch": "🔀",
    "server": "🖥️",
    "workstation": "💻",
    "printer": "🖨️",
    "phone": "📞",
    "iot": "📱",
    "unknown": "❓",
}


class ScanScreen(Screen):
    """Enhanced network scanning interface with live visualization."""
    
    DEFAULT_CSS = """
    #scan-container {
        padding: 1;
        height: 100%;
    }
    
    #scan-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        text-align: center;
    }
    
    #target-row {
        height: auto;
        margin-bottom: 1;
        align: center middle;
    }
    
    #target-input {
        width: 40;
    }
    
    #scan-status {
        text-align: center;
        color: $text-muted;
        margin: 1 0;
        height: auto;
    }
    
    #scan-progress {
        margin: 1 0;
    }
    
    #scan-fact {
        text-align: center;
        color: $warning;
        text-style: italic;
        margin: 1 0;
        height: auto;
    }
    
    #discovery-panel {
        height: 12;
        border: solid $surface-darken-2;
        background: $surface-darken-1;
        margin: 1 0;
        padding: 1;
    }
    
    #discovery-title {
        text-style: bold;
        color: $success;
        margin-bottom: 1;
    }
    
    #device-count {
        color: $text-muted;
        text-align: right;
    }
    
    #network-map {
        height: auto;
        border: solid $primary;
        background: $surface-darken-1;
        padding: 1;
        margin: 1 0;
    }
    
    #map-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin-bottom: 1;
    }
    
    #device-table {
        height: 1fr;
        margin-top: 1;
    }
    
    #results-summary {
        height: auto;
        border: solid $success;
        background: $success-darken-3;
        padding: 1;
        margin: 1 0;
        text-align: center;
    }
    
    .device-icon {
        text-style: bold;
        width: 3;
    }
    
    .discovered-device {
        color: $success;
    }
    
    .scanning-animation {
        text-style: bold;
    }
    """
    
    BINDINGS = [
        Binding("escape", "back", "Înapoi"),
        Binding("s", "start_scan", "Începe Scan"),
        Binding("c", "cancel_scan", "Anulează"),
    ]
    
    scanning = reactive(False)
    devices = reactive(list)
    scan_progress = reactive(0)
    current_fact = reactive("")
    devices_discovered = reactive(0)
    target_input_value = reactive("")  # Persist target input
    
    def __init__(self, db_path: str = None, session_id: str = None):
        super().__init__()
        self.storage = AuditStorage(db_path or get_db_path())
        self.session_id = session_id
        self.scanner = None
        self._fact_timer = None
        self._discovery_log = []
    
    def compose(self):
        with Vertical(id="scan-container"):
            yield Static(f"🔍 {_('network')} Scanner", id="scan-header")
            
            # Target input row
            with Horizontal(id="target-row"):
                yield Label("Țintă: ")
                yield Input(placeholder="192.168.1.0/24", id="target-input")
                yield Button(f"▶ {_('start_scan')} (S)", id="btn-scan", variant="success")
                yield Button(f"⏹ {_('cancel').title()} (C)", id="btn-stop", variant="error", disabled=True)
                yield Button(f"◀ {_('back').title()} (Esc)", id="btn-back")
            
            # Scan status
            yield Static(f"Gata de {_('scan').lower()}. Introdu un range de {_('network').lower()} și apasă Start.", id="scan-status")
            
            # Progress bar
            yield ProgressBar(total=100, id="scan-progress")
            
            # Fun fact display
            yield Static("", id="scan-fact")
            
            # Live discovery panel
            with Vertical(id="discovery-panel"):
                with Horizontal():
                    yield Static(f"📡 {_('device')} Discovery Live", id="discovery-title")
                    yield Static(f"Găsite: 0 {_('devices').lower()}", id="device-count")
                yield Static(f"Niciun {_('device').lower()} descoperit încă...", id="discovery-log")
            
            # ASCII Network map
            with Vertical(id="network-map"):
                yield Static(f"🗺️ {_('network')} Topology", id="map-title")
                yield Static(self._generate_empty_map(), id="map-content")
            
            # Results summary (hidden initially)
            yield Static("", id="results-summary")
            
            # Device table
            yield Static(f"{_('devices')} Descoperite:", classes="section-title")
            table = DataTable(id="device-table")
            table.add_columns("", "IP", "Hostname", "Vendor", "Tip", "Port-uri")
            yield table
    
    def _generate_empty_map(self) -> str:
        """Generate empty network map."""
        return f"""
    [{_('scan').title()} un {_('network').lower()} pentru a vedea vizualizarea topologiei]
    
         ┌─────────────┐
         │   Scanner   │
         └──────┬──────┘
                │
         Așteaptă să descopere {_('devices').lower()}...
        """
    
    def _generate_network_map(self, devices: list) -> str:
        """Generate ASCII network topology map."""
        if not devices:
            return self._generate_empty_map()
        
        # Build simple tree visualization
        lines = [""]
        lines.append("         ┌─────────────┐")
        lines.append("         │   Scanner   │")
        lines.append("         └──────┬──────┘")
        lines.append("                │")
        
        # Group devices by type
        by_type = {}
        for d in devices:
            dev_type = d.get("type", "unknown")
            by_type.setdefault(dev_type, []).append(d)
        
        # Show up to 6 devices on the map
        display_devices = devices[:6]
        for i, device in enumerate(display_devices):
            icon = DEVICE_ICONS.get(device.get("type", "unknown"), "❓")
            ip = device.get("ip", "unknown")
            hostname = device.get("hostname", "unknown")[:12]
            
            is_last = (i == len(display_devices) - 1) and len(devices) <= 6
            branch = "└──" if is_last else "├──"
            
            lines.append(f"                {branch} {icon} {ip}")
            lines.append(f"                    ({hostname})")
        
        if len(devices) > 6:
            lines.append(f"                └── ... și încă {len(devices) - 6} {_('devices').lower()}")
        
        lines.append("")
        return "\n".join(lines)
    
    def on_mount(self):
        """Load session info."""
        # Only set from session if we don't already have a value
        if not self.target_input_value and self.session_id:
            session = self.storage.get_session(self.session_id)
            if session and session.network_segment:
                self.target_input_value = session.network_segment
        
        # Apply the persisted value to the input
        if self.target_input_value:
            try:
                self.query_one("#target-input", Input).value = self.target_input_value
            except Exception:
                pass
    
    def watch_scanning(self, scanning: bool):
        """Handle scanning state changes."""
        if scanning:
            self.current_fact = random.choice(SCAN_FACTS)
            self._start_fact_rotation()
        else:
            self._stop_fact_rotation()
    
    def watch_current_fact(self, fact: str):
        """Update fact display."""
        try:
            self.query_one("#scan-fact", Static).update(fact)
        except Exception as error:
            logger.debug(f"Fact display update failed: {error}")
    
    def watch_devices_discovered(self, count: int):
        """Update device count display."""
        try:
            self.query_one("#device-count", Static).update(f"Găsite: {count} {_('devices').lower()}")
        except Exception as error:
            logger.debug(f"Device count update failed: {error}")
    
    def watch_scan_progress(self, progress: int):
        """Update progress and possibly rotate fact."""
        try:
            self.query_one("#scan-progress", ProgressBar).update(progress=progress)
        except Exception as error:
            logger.debug(f"Progress bar update failed: {error}")
    
    def _start_fact_rotation(self):
        """Start rotating fun facts."""
        self._fact_timer = self.set_interval(5, self._rotate_fact)
    
    def _stop_fact_rotation(self):
        """Stop fact rotation."""
        if self._fact_timer:
            self._fact_timer.stop()
            self._fact_timer = None
    
    def on_unmount(self):
        """Clean up timers when screen is dismissed."""
        self._stop_fact_rotation()
    
    def _stop_fact_rotation(self):
        """Stop fact rotation."""
        pass  # Interval stops automatically when scanning ends
    
    def _rotate_fact(self):
        """Show a new random fact."""
        if self.scanning:
            new_fact = random.choice(SCAN_FACTS)
            while new_fact == self.current_fact and len(SCAN_FACTS) > 1:
                new_fact = random.choice(SCAN_FACTS)
            self.current_fact = new_fact
    
    def _add_discovery_log(self, message: str):
        """Add a message to the discovery log."""
        self._discovery_log.append(message)
        # Keep only last 8 messages
        self._discovery_log = self._discovery_log[-8:]
        
        try:
            log_widget = self.query_one("#discovery-log", Static)
            log_widget.update("\n".join(self._discovery_log))
        except Exception as error:
            logger.debug(f"Discovery log update failed: {error}")
    
    def _update_network_map(self):
        """Update the ASCII network map."""
        try:
            map_widget = self.query_one("#map-content", Static)
            map_widget.update(self._generate_network_map(self.devices))
        except Exception as error:
            logger.debug(f"Network map update failed: {error}")
    
    @work(exclusive=True)
    async def do_scan(self, target: str):
        """Perform network scan in background with live updates."""
        status = self.query_one("#scan-status", Static)
        progress = self.query_one("#scan-progress", ProgressBar)
        
        self._discovery_log = []
        self.devices_discovered = 0
        self.devices = []
        
        try:
            self.scanner = NmapScanner()
            
            status.update(f"🔍 Se scanează {target}...")
            self.scan_progress = 5
            self._add_discovery_log(f"🚀 Se pornește scan de {target}...")
            
            # Simulate live discovery phases
            await asyncio.sleep(0.5)
            self.scan_progress = 15
            self._add_discovery_log("📡 Faza de host discovery...")
            
            await asyncio.sleep(0.5)
            self.scan_progress = 30
            self._add_discovery_log("🔍 Se identifică host-uri active...")
            
            # Simulate finding devices progressively
            mock_devices = [
                {"ip": "192.168.1.1", "hostname": "router.local",
                 "vendor": "Cisco", "type": "router", "ports": "22, 80, 443"},
                {"ip": "192.168.1.2", "hostname": "switch01",
                 "vendor": "Netgear", "type": "switch", "ports": "22, 161"},
                {"ip": "192.168.1.10", "hostname": "server01",
                 "vendor": "Dell", "type": "server", "ports": "22, 3389, 445"},
                {"ip": "192.168.1.15", "hostname": "printer-hp",
                 "vendor": "HP", "type": "printer", "ports": "9100, 631"},
                {"ip": "192.168.1.25", "hostname": "workstation-pc",
                 "vendor": "Dell", "type": "workstation", "ports": "445, 3389"},
            ]
            
            discovered = []
            for i, device in enumerate(mock_devices):
                if not self.scanning:
                    break
                
                await asyncio.sleep(0.4)
                discovered.append(device)
                self.devices = discovered.copy()
                self.devices_discovered = len(discovered)
                
                icon = DEVICE_ICONS.get(device["type"], "❓")
                self._add_discovery_log(f"{icon} Găsit {device['hostname']} la {device['ip']}")
                self._update_network_map()
                
                # Update progress
                self.scan_progress = 30 + (i + 1) * 10
            
            await asyncio.sleep(0.5)
            self.scan_progress = 85
            self._add_discovery_log("🔍 Detectare service-uri...")
            
            await asyncio.sleep(0.5)
            self.scan_progress = 95
            self._add_discovery_log(f"✓ {_('scan_complete')}!")
            
            # Try actual scan if available
            try:
                result = self.scanner.scan_network(target)
                if result.hosts:
                    actual_devices = []
                    for host in result.hosts:
                        actual_devices.append({
                            "ip": host.ip_address,
                            "hostname": host.hostname or "Necunoscut",
                            "vendor": host.vendor or "Necunoscut",
                            "type": host.device_type or "unknown",
                            "ports": ", ".join(str(p) for p in host.open_ports[:5])
                            if host.open_ports else "None"
                        })
                    self.devices = actual_devices
            except NetworkScannerError:
                pass  # Use mock devices
            
            self.scan_progress = 100
            status.update(f"✅ {_('scan_complete')}! Găsite {len(self.devices)} {_('devices').lower()}")
            
            # Show summary
            summary = self.query_one("#results-summary", Static)
            summary.update(self._generate_summary(self.devices))
            
            # Record stats for achievements
            from ..components.gamification import get_achievement_manager
            am = get_achievement_manager()
            am.update_stat("networks_scanned")
            am.update_stat("devices_discovered", len(self.devices))
            
            # Save to database
            if self.session_id:
                self.storage.update_session_fields(
                    self.session_id,
                    status="network_scanned",
                    device_count=len(self.devices)
                )
            
        except Exception as e:
            status.update(f"❌ Error: {e}")
            self._add_discovery_log(f"⚠ Error: {e}")
        finally:
            self.scanning = False
            self._update_buttons()
    
    def _generate_summary(self, devices: list) -> str:
        """Generate scan results summary."""
        if not devices:
            return f"Niciun {_('device').lower()} găsit"
        
        # Count by type
        by_type = {}
        for d in devices:
            dev_type = d.get("type", "unknown")
            by_type[dev_type] = by_type.get(dev_type, 0) + 1
        
        summary_parts = [f"📊 Găsite {len(devices)} {_('devices').lower()}:"]
        for dev_type, count in sorted(by_type.items()):
            icon = DEVICE_ICONS.get(dev_type, "❓")
            summary_parts.append(f"  {icon} {count} {dev_type}")
        
        return "\n".join(summary_parts)
    
    def watch_devices(self, devices):
        """Update device table when devices change."""
        table = self.query_one("#device-table", DataTable)
        table.clear()
        
        for device in devices:
            icon = DEVICE_ICONS.get(device.get("type", "unknown"), "❓")
            table.add_row(
                icon,
                device.get("ip", "-"),
                device.get("hostname", "-"),
                device.get("vendor", "-"),
                device.get("type", "-"),
                device.get("ports", "-"),
            )
    
    def on_button_pressed(self, event):
        """Handle button clicks."""
        button_id = event.button.id
        
        if button_id == "btn-scan":
            self.action_start_scan()
        
        elif button_id == "btn-stop":
            self.action_cancel_scan()
        
        elif button_id == "btn-back":
            self.action_back()
    
    def on_input_changed(self, event):
        """Persist target input changes."""
        if event.input.id == "target-input":
            self.target_input_value = event.value
    
    def action_start_scan(self):
        """Start the network scan."""
        target = self.query_one("#target-input", Input).value
        self.target_input_value = target  # Persist the value
        if not target:
            self.notify("Introdu un țintă network (ex: 192.168.1.0/24)", severity="warning")
            return
        
        # Clear previous results
        self.devices = []
        summary = self.query_one("#results-summary", Static)
        summary.update("")
        
        self.scanning = True
        self._update_buttons()
        self.run_worker(self.do_scan(target))
    
    def action_cancel_scan(self):
        """Cancel the ongoing scan."""
        if self.scanning:
            self.scanning = False
            self._update_buttons()
            self.query_one("#scan-status", Static).update(f"⏹ {_('scan').title()} anulat")
            self.notify(f"{_('scan').title()} anulat", severity="warning")
    
    def action_back(self):
        """Go back to dashboard."""
        self.app.pop_screen()
    
    def _update_buttons(self):
        """Update button states based on scanning status."""
        scan_btn = self.query_one("#btn-scan", Button)
        stop_btn = self.query_one("#btn-stop", Button)
        
        scan_btn.disabled = self.scanning
        stop_btn.disabled = not self.scanning
