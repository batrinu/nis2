"""Enhanced SSH device connection screen with device cards and bulk operations."""
from textual.screen import Screen, ModalScreen
from textual.widgets import Input, Button, Static, DataTable, Select, Label, Checkbox
from textual.containers import Horizontal, Vertical, Grid, ScrollableContainer
from textual.reactive import reactive
from textual.worker import Worker
from textual import work
from textual.binding import Binding
from ...storage.db import AuditStorage
from ...utils import get_db_path
from ...i18n import get_text as _
import asyncio
import logging

logger = logging.getLogger(__name__)


# Device type icons and colors
DEVICE_ICONS = {
    "router": "🌐",
    "switch": "🔀",
    "server": "🖥️",
    "workstation": "💻",
    "printer": "🖨️",
    "phone": "📞",
    "iot": "📱",
    "firewall": "🛡️",
    "unknown": "❓",
}

DEVICE_COLORS = {
    "router": "#ff8800",
    "switch": "#00aaff",
    "server": "#00ff41",
    "workstation": "#8888ff",
    "printer": "#ff66aa",
    "firewall": "#ff4444",
    "unknown": "#888888",
}


class DeviceDetailModal(ModalScreen):
    """Modal showing detailed device information."""
    
    CSS = """
    #device-modal {
        width: 60;
        height: auto;
        max-height: 40;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    
    #modal-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        border-bottom: solid $primary;
    }
    
    .info-row {
        height: auto;
        margin: 1 0;
    }
    
    .info-label {
        width: 20;
        color: $text-muted;
    }
    
    .info-value {
        width: 1fr;
        color: $text;
    }
    
    #modal-actions {
        margin-top: 2;
        align: center middle;
    }
    """
    
    def __init__(self, device):
        super().__init__()
        self.device = device
    
    def compose(self):
        with Vertical(id="device-modal"):
            icon = DEVICE_ICONS.get(self.device.device_type or "unknown", "❓")
            yield Static(f"{icon} {_('device_details')}", id="modal-title")
            
            with Grid(classes="info-row"):
                yield Label(f"{_('ip_address')}:", classes="info-label")
                yield Label(self.device.ip_address or "Unknown", classes="info-value")
            
            with Grid(classes="info-row"):
                yield Label(f"{_('hostname')}:", classes="info-label")
                yield Label(self.device.hostname or "Unknown", classes="info-value")
            
            with Grid(classes="info-row"):
                yield Label(f"{_('type')}:", classes="info-label")
                yield Label(self.device.device_type or _("unknown"), classes="info-value")
            
            with Grid(classes="info-row"):
                yield Label(f"{_('vendor')}:", classes="info-label")
                yield Label(self.device.vendor or _("unknown"), classes="info-value")
            
            with Grid(classes="info-row"):
                yield Label(f"{_('status')}:", classes="info-label")
                status = self.device.connection_status or "pending"
                status_display = f"{self._status_icon(status)} {status.title()}"
                yield Label(status_display, classes="info-value")
            
            with Grid(classes="info-row"):
                yield Label(f"{_('open_ports')}:", classes="info-label")
                ports = ", ".join(str(p) for p in self.device.open_ports[:10]) \
                    if self.device.open_ports else "None detected"
                yield Label(ports, classes="info-value")
            
            with Horizontal(id="modal-actions"):
                yield Button(_("connect"), variant="success", id="btn-modal-connect")
                yield Button(_("close"), variant="primary", id="btn-modal-close")
    
    def _status_icon(self, status: str) -> str:
        icons = {
            "connected": "✓",
            "failed": "✗",
            "pending": "○",
        }
        return icons.get(status, "○")
    
    def on_button_pressed(self, event):
        if event.button.id == "btn-modal-close":
            self.dismiss()
        elif event.button.id == "btn-modal-connect":
            self.dismiss(self.device)


class ConnectScreen(Screen):
    """Enhanced SSH connection interface with device cards and bulk operations."""
    
    DEFAULT_CSS = """
    #connect-container {
        padding: 1;
        height: 100%;
    }
    
    #connect-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        text-align: center;
    }
    
    #bulk-actions {
        height: auto;
        margin-bottom: 1;
        align: center middle;
    }
    
    #device-grid {
        height: 1fr;
        overflow: auto;
    }
    
    .device-card {
        width: 100%;
        height: auto;
        border: solid $surface-lighten-1;
        background: $surface-darken-1;
        padding: 1;
        margin: 1 0;
    }
    
    .device-card.selected {
        border: double $primary;
        background: $primary-darken-3;
    }
    
    .device-card.connected {
        border: solid $success;
    }
    
    .device-header {
        height: auto;
        margin-bottom: 1;
    }
    
    .device-icon {
        width: 3;
        text-style: bold;
    }
    
    .device-name {
        width: 1fr;
        text-style: bold;
    }
    
    .device-status {
        width: auto;
    }
    
    .device-info {
        color: $text-muted;
        height: auto;
    }
    
    .device-actions {
        height: auto;
        margin-top: 1;
    }
    
    #cred-panel {
        height: auto;
        border: solid $surface-lighten-1;
        padding: 1;
        margin-top: 1;
    }
    
    #cred-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    .form-row {
        height: auto;
        margin: 1 0;
    }
    
    .form-label {
        width: 18;
        color: $text-muted;
    }
    
    #selection-info {
        height: auto;
        text-align: center;
        color: $text-muted;
        margin: 1 0;
    }
    
    #empty-state {
        text-align: center;
        color: $text-muted;
        margin-top: 4;
    }
    """
    
    BINDINGS = [
        Binding("escape", "back", _("back")),
        Binding("space", "toggle_select", _("select")),
        Binding("a", "select_all", _("select_all")),
        Binding("c", "connect_selected", _("connect")),
        Binding("r", "refresh", _("refresh")),
    ]
    
    connecting = reactive(False)
    selected_devices = reactive(set)  # Set of device indices
    devices = reactive(list)
    
    # Persist credentials input values
    ssh_username = reactive("")
    ssh_password = reactive("")
    device_type = reactive("auto")
    
    def __init__(self, db_path: str = None, session_id: str = None):
        super().__init__()
        self.storage = AuditStorage(db_path or get_db_path())
        self.session_id = session_id
    
    def compose(self):
        with Vertical(id="connect-container"):
            yield Static(f"🔐 {_('device_connection_manager')}", id="connect-header")
            
            # Bulk actions toolbar
            with Horizontal(id="bulk-actions"):
                yield Button(f"✓ {_('select_all')} (A)", id="btn-select-all", variant="primary")
                yield Button(f"✗ {_('clear_selection')}", id="btn-clear", variant="primary")
                yield Button(f"▶ {_('connect_selected')} (C)", id="btn-connect-all", variant="success")
                yield Button(f"🔄 {_('refresh')} (R)", id="btn-refresh")
            
            # Selection info
            yield Static(_("no_devices_selected"), id="selection-info")
            
            # Device cards container
            with ScrollableContainer(id="device-grid"):
                yield Static(_("loading_devices"), id="empty-state")
            
            # Credentials panel
            with Vertical(id="cred-panel"):
                yield Static(f"🔑 {_('ssh_credentials')}", id="cred-title")
                
                with Grid(classes="form-row"):
                    yield Label(f"{_('username')}:", classes="form-label")
                    yield Input(placeholder="admin", id="input-username", value=self.ssh_username)
                
                with Grid(classes="form-row"):
                    yield Label(f"{_('password')}:", classes="form-label")
                    yield Input(placeholder="••••••", id="input-password", password=True, value=self.ssh_password)
                
                with Grid(classes="form-row"):
                    yield Label(f"{_('device_type')}:", classes="form-label")
                    yield Select([
                        (_("auto_detect"), "auto"),
                        ("Cisco IOS", "cisco_ios"),
                        ("Cisco NX-OS", "cisco_nxos"),
                        ("Juniper JunOS", "juniper_junos"),
                        ("Linux/Unix", "linux"),
                        ("HP Comware", "hp_comware"),
                        (_("generic_ssh"), "generic"),
                    ], id="select-device-type", value=self.device_type)
            
            with Horizontal():
                yield Button(f"◀ {_('back')} (Esc)", id="btn-back")
                yield Button(f"📋 {_('run_assessment')}", id="btn-commands", disabled=True)
    
    def on_mount(self):
        """Load devices for session."""
        self._load_devices()
        # Restore credentials from reactive variables
        self._restore_credentials()
    
    def _load_devices(self):
        """Load devices from storage."""
        if self.session_id:
            self.devices = self.storage.get_devices(self.session_id)
        else:
            self.devices = []
        self._refresh_device_grid()
    
    def _restore_credentials(self):
        """Restore credentials inputs from reactive variables."""
        try:
            username_input = self.query_one("#input-username", Input)
            username_input.value = self.ssh_username
        except Exception:
            pass
        
        try:
            password_input = self.query_one("#input-password", Input)
            password_input.value = self.ssh_password
        except Exception:
            pass
        
        try:
            device_type_select = self.query_one("#select-device-type", Select)
            if self.device_type:
                device_type_select.value = self.device_type
        except Exception:
            pass
    
    def on_input_changed(self, event):
        """Persist credentials input changes."""
        if event.input.id == "input-username":
            self.ssh_username = event.value
        elif event.input.id == "input-password":
            self.ssh_password = event.value
    
    def on_select_changed(self, event):
        """Persist device type selection."""
        if event.select.id == "select-device-type":
            self.device_type = event.value or "auto"
    
    def watch_selected_devices(self, selected):
        """Update UI when selection changes."""
        self._update_selection_info()
        self._refresh_device_grid()
    
    def _update_selection_info(self):
        """Update selection info text."""
        info = self.query_one("#selection-info", Static)
        count = len(self.selected_devices)
        if count == 0:
            info.update(_("no_devices_selected"))
        elif count == 1:
            info.update(_("1_device_selected"))
        else:
            info.update(_("n_devices_selected").format(count=count))
    
    def _refresh_device_grid(self):
        """Refresh the device cards display."""
        grid = self.query_one("#device-grid", ScrollableContainer)
        grid.remove_children()
        
        if not self.devices:
            grid.mount(Static(f"""
📭 {_('no_devices_found_session')}

{_('scan_network_first')}
            """.strip(), id="empty-state"))
            return
        
        for i, device in enumerate(self.devices):
            is_selected = i in self.selected_devices
            card = self._create_device_card(device, i, is_selected)
            grid.mount(card)
    
    def _create_device_card(self, device, index, is_selected):
        """Create a device card widget."""
        icon = DEVICE_ICONS.get(device.device_type or "unknown", "❓")
        status = device.connection_status or "pending"
        status_icon = self._status_icon(status)
        status_color = self._status_color(status)
        
        card_classes = "device-card"
        if is_selected:
            card_classes += " selected"
        if status == "connected":
            card_classes += " connected"
        
        card = Vertical(classes=card_classes, id=f"device-card-{index}")
        
        # Header row with icon, name, status
        header = Horizontal(classes="device-header")
        header.mount(Static(f"{icon}", classes="device-icon"))
        name = device.hostname or device.ip_address or _("unknown")
        header.mount(Static(name, classes="device-name"))
        status_text = f"[{status_color}]{status_icon} {status.title()}[/{status_color}]"
        header.mount(Static(status_text, classes="device-status"))
        card.mount(header)
        
        # Info row
        info_text = (
            f"IP: {device.ip_address or 'N/A'} | "
            f"Type: {device.device_type or 'Unknown'} | "
            f"Vendor: {device.vendor or 'Unknown'}"
        )
        card.mount(Static(info_text, classes="device-info"))
        
        # Actions row
        actions = Horizontal(classes="device-actions")
        actions.mount(Checkbox(_("select"), value=is_selected, id=f"chk-{index}"))
        actions.mount(Button(_("details"), id=f"btn-detail-{index}"))
        if status != "connected":
            actions.mount(Button(_("connect"), variant="success", id=f"btn-connect-{index}"))
        else:
            actions.mount(Button(_("disconnect"), variant="error", id=f"btn-disconnect-{index}"))
        card.mount(actions)
        
        return card
    
    def _status_icon(self, status: str) -> str:
        icons = {
            "connected": "✓",
            "failed": "✗",
            "pending": "○",
        }
        return icons.get(status, "○")
    
    def _status_color(self, status: str) -> str:
        colors = {
            "connected": "green",
            "failed": "red",
            "pending": "yellow",
        }
        return colors.get(status, "white")
    
    def on_checkbox_changed(self, event):
        """Handle device selection checkbox."""
        checkbox_id = event.checkbox.id
        if checkbox_id and checkbox_id.startswith("chk-"):
            try:
                parts = checkbox_id.split("-")
                if len(parts) < 2:
                    return
                index = int(parts[1])
            except (ValueError, IndexError) as e:
                logger.debug(f"Invalid checkbox ID format: {e}")
                return
            if event.value:
                self.selected_devices = self.selected_devices | {index}
            else:
                self.selected_devices = self.selected_devices - {index}
    
    def on_button_pressed(self, event):
        """Handle button clicks."""
        button_id = event.button.id
        
        if button_id == "btn-select-all":
            self.action_select_all()
        
        elif button_id == "btn-clear":
            self.selected_devices = set()
        
        elif button_id == "btn-connect-all":
            self.action_connect_selected()
        
        elif button_id == "btn-refresh":
            self.action_refresh()
        
        elif button_id == "btn-back":
            self.action_back()
        
        elif button_id == "btn-commands":
            self._run_assessment()
        
        elif button_id and button_id.startswith("btn-detail-"):
            try:
                parts = button_id.split("-")
                if len(parts) < 3:
                    return
                index = int(parts[-1])
                self._show_device_detail(index)
            except (ValueError, IndexError) as error:
                logger.debug(f"Invalid button ID format: {error}")
        
        elif button_id and button_id.startswith("btn-connect-"):
            try:
                parts = button_id.split("-")
                if len(parts) < 3:
                    return
                index = int(parts[-1])
                self._connect_single(index)
            except (ValueError, IndexError) as error:
                logger.debug(f"Invalid button ID format: {error}")
        
        elif button_id and button_id.startswith("btn-disconnect-"):
            try:
                parts = button_id.split("-")
                if len(parts) < 3:
                    return
                index = int(parts[-1])
                self._disconnect_single(index)
            except (ValueError, IndexError) as error:
                logger.debug(f"Invalid button ID format: {error}")
    
    def _show_device_detail(self, index: int):
        """Show device detail modal."""
        if 0 <= index < len(self.devices):
            self.push_screen(DeviceDetailModal(self.devices[index]))
    
    def _connect_single(self, index: int):
        """Connect to a single device."""
        if 0 <= index < len(self.devices):
            self.selected_devices = {index}
            self.run_worker(self._do_bulk_connect())
    
    def _disconnect_single(self, index: int):
        """Disconnect a single device."""
        if 0 <= index < len(self.devices):
            device = self.devices[index]
            device.connection_status = "not_attempted"
            self.storage.save_device(device)
            self._load_devices()
            self.notify(f"Deconectat de la {device.ip_address}", severity="information")
    
    @work(exclusive=True)
    async def _do_bulk_connect(self):
        """Connect to all selected devices."""
        if not self.selected_devices:
            self.notify(_("no_devices_selected"), severity="warning")
            return
        
        username = self.query_one("#input-username", Input).value
        password = self.query_one("#input-password", Input).value
        
        if not username or not password:
            self.notify(_("username_password_required"), severity="warning")
            return
        
        self.connecting = True
        success_count = 0
        
        for index in self.selected_devices:
            if index >= len(self.devices):
                continue
            
            device = self.devices[index]
            self.notify(_("connecting_to").format(ip=device.ip_address))
            
            # Simulate connection
            await asyncio.sleep(1)
            
            # Update device status
            device.connection_status = "connected"
            self.storage.save_device(device)
            success_count += 1
        
        self.connecting = False
        self._load_devices()  # Refresh to show updated statuses
        
        self.notify(_("connected_to_n_devices").format(count=success_count), severity="success")
        self.query_one("#btn-commands", Button).disabled = False
    
    def _run_assessment(self):
        """Run assessment commands on connected devices."""
        connected = [d for d in self.devices if d.connection_status == "connected"]
        if not connected:
            self.notify(_("no_connected_devices"), severity="warning")
            return
        
        self.notify(_("running_assessment_on_n_devices").format(count=len(connected)), severity="information")
        
        # Update session status
        if self.session_id:
            self.storage.update_session_fields(self.session_id, status="devices_interrogated")
    
    def action_select_all(self):
        """Select all devices."""
        self.selected_devices = set(range(len(self.devices)))
    
    def action_toggle_select(self):
        """Toggle selection of first device (placeholder for proper focus tracking)."""
        if self.devices:
            if 0 in self.selected_devices:
                self.selected_devices = self.selected_devices - {0}
            else:
                self.selected_devices = self.selected_devices | {0}
    
    def action_connect_selected(self):
        """Connect to selected devices."""
        self.run_worker(self._do_bulk_connect())
    
    def action_refresh(self):
        """Refresh device list."""
        self._load_devices()
        self.notify(_("device_list_refreshed"), severity="information")
    
    def action_back(self):
        """Go back to dashboard."""
        self.app.pop_screen()
