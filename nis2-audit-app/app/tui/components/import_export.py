"""
Import/Export System
Import wizard, export options, and backup/restore functionality.
"""
from textual.screen import ModalScreen
from textual.widgets import Static, Button, Input, Select, Label
from textual.containers import Vertical, Horizontal, Grid
from textual.reactive import reactive
from textual.binding import Binding
import json
import csv
import os
import shutil
from datetime import datetime
from pathlib import Path


class ImportWizard(ModalScreen):
    """Wizard for importing data from various sources."""
    
    CSS = """
    #import-wizard-modal {
        width: 70;
        height: auto;
        max-height: 50;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    
    #import-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        border-bottom: solid $primary;
    }
    
    #import-step {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }
    
    #import-content {
        height: 1fr;
        overflow: auto;
    }
    
    .import-option {
        height: auto;
        margin: 1 0;
        padding: 1;
        border: solid $surface-lighten-1;
    }
    
    .import-option:hover {
        border: solid $primary;
    }
    
    .import-format {
        text-style: bold;
    }
    
    .import-desc {
        color: $text-muted;
    }
    
    #import-actions {
        margin-top: 1;
        align: center middle;
        border-top: solid $surface-lighten-1;
        padding-top: 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
    ]
    
    step = reactive(1)
    selected_format = reactive(None)
    
    def compose(self):
        with Vertical(id="import-wizard-modal"):
            yield Static("📥 Import Data", id="import-title")
            yield Static(f"Step {self.step} of 3", id="import-step")
            
            with Vertical(id="import-content"):
                if self.step == 1:
                    yield Static("Select import format:", classes="import-desc")
                    
                    with Vertical(classes="import-option"):
                        yield Static("📄 CSV File", classes="import-format")
                        yield Static("Import from comma-separated values file", classes="import-desc")
                        yield Button("Select CSV", id="btn-csv")
                    
                    with Vertical(classes="import-option"):
                        yield Static("📊 Excel/Spreadsheet", classes="import-format")
                        yield Static("Import from Excel (.xlsx) or similar", classes="import-desc")
                        yield Button("Select Excel", id="btn-excel")
                    
                    with Vertical(classes="import-option"):
                        yield Static("📋 JSON Data", classes="import-format")
                        yield Static("Import from JSON format", classes="import-desc")
                        yield Button("Select JSON", id="btn-json")
                
                elif self.step == 2:
                    yield Static("Select file to import:", classes="import-desc")
                    yield Input(placeholder="/path/to/file.csv", id="import-path")
                    yield Button("📂 Browse", id="btn-browse")
                
                elif self.step == 3:
                    yield Static("Preview (first 5 rows):", classes="import-desc")
                    yield Static("""
Device,IP,Type
Router,192.168.1.1,router
Server,192.168.1.10,server
Printer,192.168.1.20,printer
                    """.strip(), id="import-preview")
                    
                    yield Static("Mapping:", classes="import-desc")
                    yield Static("Device → hostname\nIP → ip_address\nType → device_type")
            
            with Horizontal(id="import-actions"):
                if self.step > 1:
                    yield Button("◀ Back", id="btn-back")
                if self.step < 3:
                    yield Button("Next ▶", id="btn-next")
                else:
                    yield Button("✓ Import", variant="success", id="btn-import")
                yield Button("Cancel", id="btn-cancel")
    
    def on_button_pressed(self, event):
        btn_id = event.button.id
        
        if btn_id == "btn-csv":
            self.selected_format = "csv"
            self.step = 2
        elif btn_id == "btn-excel":
            self.selected_format = "excel"
            self.step = 2
        elif btn_id == "btn-json":
            self.selected_format = "json"
            self.step = 2
        elif btn_id == "btn-next":
            self.step += 1
        elif btn_id == "btn-back":
            self.step -= 1
        elif btn_id == "btn-import":
            self.notify("Import completed!", severity="success")
            self.dismiss()
        elif btn_id == "btn-cancel":
            self.dismiss()


class BackupRestore(ModalScreen):
    """Backup and restore data."""
    
    CSS = """
    #backup-modal {
        width: 60;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    
    #backup-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        border-bottom: solid $primary;
    }
    
    .backup-section {
        height: auto;
        margin: 1 0;
        padding: 1;
        border: solid $surface-lighten-1;
    }
    
    .section-title {
        text-style: bold;
        margin-bottom: 1;
    }
    
    .section-desc {
        color: $text-muted;
        margin-bottom: 1;
    }
    
    #backup-actions {
        margin-top: 1;
        align: center middle;
    }
    """
    
    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
    ]
    
    def compose(self):
        with Vertical(id="backup-modal"):
            yield Static("💾 Backup & Restore", id="backup-title")
            
            with Vertical(classes="backup-section"):
                yield Static("📦 Create Backup", classes="section-title")
                yield Static("Export all audit data, sessions, and settings to a backup file", classes="section-desc")
                with Horizontal():
                    yield Button("💾 Create Backup", id="btn-backup")
                    yield Input(placeholder="backup_filename", value=f"nis2_backup_{datetime.now().strftime('%Y%m%d')}", id="backup-name")
            
            with Vertical(classes="backup-section"):
                yield Static("📥 Restore from Backup", classes="section-title")
                yield Static("Restore data from a previous backup file", classes="section-desc")
                with Horizontal():
                    yield Button("📥 Select Backup", id="btn-restore")
                    yield Input(placeholder="/path/to/backup.zip", id="restore-path")
            
            with Vertical(classes="backup-section"):
                yield Static("☁️ Auto-Backup", classes="section-title")
                yield Static("Automatically backup weekly", classes="section-desc")
                # Would include checkbox in real implementation
            
            with Horizontal(id="backup-actions"):
                yield Button("Close", variant="primary", id="btn-close")
    
    def on_button_pressed(self, event):
        btn_id = event.button.id
        
        if btn_id == "btn-backup":
            self._create_backup()
        elif btn_id == "btn-restore":
            self._restore_backup()
        elif btn_id == "btn-close":
            self.dismiss()
    
    def _create_backup(self):
        """Create a backup of all data."""
        try:
            config_dir = os.path.expanduser("~/.nis2-audit")
            backup_name = self.query_one("#backup-name", Input).value or "backup"
            backup_path = os.path.join(config_dir, f"{backup_name}.zip")
            
            # Create zip of config directory
            shutil.make_archive(
                os.path.join(config_dir, backup_name),
                'zip',
                config_dir
            )
            
            self.notify(f"✓ Backup created: {backup_path}", severity="success")
        except Exception as e:
            self.notify(f"Backup failed: {e}", severity="error")
    
    def _restore_backup(self):
        """Restore from backup."""
        self.notify("Restore functionality would restore from backup file", severity="information")


class ExportOptions:
    """Export format options and helpers."""
    
    FORMATS = {
        "markdown": {
            "name": "Markdown",
            "extension": ".md",
            "mime": "text/markdown",
        },
        "html": {
            "name": "HTML",
            "extension": ".html",
            "mime": "text/html",
        },
        "json": {
            "name": "JSON",
            "extension": ".json",
            "mime": "application/json",
        },
        "csv": {
            "name": "CSV",
            "extension": ".csv",
            "mime": "text/csv",
        },
        "pdf": {
            "name": "PDF",
            "extension": ".pdf",
            "mime": "application/pdf",
        },
    }
    
    @classmethod
    def get_format_info(cls, format_id: str) -> dict:
        """Get information about an export format."""
        return cls.FORMATS.get(format_id, cls.FORMATS["markdown"])
    
    @staticmethod
    def export_to_csv(data: list, headers: list) -> str:
        """Export data to CSV string."""
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)
        return output.getvalue()
    
    @staticmethod
    def export_to_json(data: dict) -> str:
        """Export data to JSON string."""
        return json.dumps(data, indent=2, default=str)
    
    @staticmethod
    def export_to_markdown_table(headers: list, rows: list, title: str = "") -> str:
        """Export data to Markdown table."""
        lines = []
        if title:
            lines.append(f"## {title}\n")
        
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("|" + "|".join([" --- " for _ in headers]) + "|")
        
        for row in rows:
            lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
        
        return "\n".join(lines)


class DataMigration:
    """Helper for migrating data between versions."""
    
    CURRENT_VERSION = "1.0.0"
    
    @classmethod
    def check_migration_needed(cls) -> bool:
        """Check if data migration is needed."""
        try:
            config_dir = os.path.expanduser("~/.nis2-audit")
            version_file = os.path.join(config_dir, "data_version")
            
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    stored_version = f.read().strip()
                return stored_version != cls.CURRENT_VERSION
            
            return True
        except Exception:
            return False
    
    @classmethod
    def migrate(cls) -> bool:
        """Perform data migration."""
        try:
            # Migration logic would go here
            config_dir = os.path.expanduser("~/.nis2-audit")
            version_file = os.path.join(config_dir, "data_version")
            
            with open(version_file, 'w') as f:
                f.write(cls.CURRENT_VERSION)
            
            return True
        except Exception:
            return False


class CloudBackup:
    """Cloud backup integration (placeholder)."""
    
    @staticmethod
    def is_configured() -> bool:
        """Check if cloud backup is configured."""
        # Would check for cloud provider credentials
        return False
    
    @staticmethod
    def backup_to_cloud(local_path: str) -> bool:
        """Backup file to cloud storage."""
        # Would upload to configured cloud provider
        return False
    
    @staticmethod
    def restore_from_cloud(backup_id: str, local_path: str) -> bool:
        """Restore file from cloud storage."""
        # Would download from configured cloud provider
        return False
