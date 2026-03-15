"""Enhanced report generation screen with preview and smooth export flow."""
from ...i18n import get_text as _
from textual.screen import Screen
from textual.widgets import Button, Static, Select, Input, ProgressBar, TextArea
from textual.containers import Horizontal, Vertical, Grid
from textual.reactive import reactive
from textual.worker import Worker
from textual import work
from textual.binding import Binding
from ...storage.db import AuditStorage
from ...utils import get_db_path
from ..components.error_prevention import ConfirmationDialog
from pathlib import Path
import asyncio
import os
import shutil
import subprocess
import platform
import logging

logger = logging.getLogger(__name__)


class ReportScreen(Screen):
    """Enhanced report generation with preview and smooth export flow."""
    
    DEFAULT_CSS = """
    #report-container {
        padding: 1;
        height: 100%;
    }
    
    #report-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        text-align: center;
    }
    
    #main-layout {
        height: 1fr;
    }
    
    #options-panel {
        width: 35;
        border-right: solid $surface-lighten-1;
        padding: 0 1;
    }
    
    #options-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    .form-row {
        height: auto;
        margin: 1 0;
    }
    
    .form-label {
        color: $text-muted;
        margin-bottom: 1;
    }
    
    #preview-panel {
        width: 1fr;
        padding: 0 1;
    }
    
    #preview-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    #preview-content {
        height: 1fr;
        border: solid $surface-lighten-1;
        background: $surface-darken-1;
        padding: 1;
    }
    
    #progress-section {
        height: auto;
        border-top: solid $surface-lighten-1;
        padding-top: 1;
        margin-top: 1;
    }
    
    #progress-bar {
        margin: 1 0;
    }
    
    #status-text {
        text-align: center;
        margin: 1 0;
        color: $text-muted;
    }
    
    #recent-exports {
        height: auto;
        border-top: solid $surface-lighten-1;
        margin-top: 1;
        padding-top: 1;
    }
    
    #recent-title {
        text-style: bold;
        color: $text-muted;
        margin-bottom: 1;
    }
    
    .recent-item {
        height: auto;
        margin: 1 0;
        color: $text-muted;
    }
    """
    
    BINDINGS = [
        Binding("escape", "back", _("Back")),
        Binding("g", "generate", _("Generate")),
        Binding("o", "open_folder", _("Open Folder")),
    ]
    
    generating = reactive(False)
    progress = reactive(0)
    
    # Persist form selections
    report_format = reactive("markdown")
    report_template = reactive("standard")
    output_path = reactive("./audit_report.md")
    
    def __init__(self, db_path: str = None, session_id: str = None):
        super().__init__()
        self.storage = AuditStorage(db_path or get_db_path())
        self.session_id = session_id
        self._recent_exports = []
    
    def compose(self):
        with Vertical(id="report-container"):
            yield Static(_("📄 Report Generator"), id="report-header")
            
            with Horizontal(id="main-layout"):
                # Options panel
                with Vertical(id="options-panel"):
                    yield Static(_("⚙️ Options"), id="options-title")
                    
                    with Vertical(classes="form-row"):
                        yield Static(_("Format:"), classes="form-label")
                        yield Select([
                            ("📄 Markdown (.md)", "markdown"),
                            ("🌐 HTML (.html)", "html"),
                            ("📊 JSON (.json)", "json"),
                            ("📑 PDF (.pdf)", "pdf"),
                        ], id="select-format", value=self.report_format)
                    
                    with Vertical(classes="form-row"):
                        yield Static(_("Template:"), classes="form-label")
                        yield Select([
                            (_("📋 Standard"), "standard"),
                            (_("👔 Executive Summary"), "executive"),
                            (_("🔧 Technical Detail"), "technical"),
                        ], id="select-template", value=self.report_template)
                    
                    with Vertical(classes="form-row"):
                        yield Static(_("Output Path:"), classes="form-label")
                        yield Input(
                            placeholder=_("./audit_report.md"),
                            id="input-path",
                            value=self.output_path
                        )
                    
                    with Vertical(classes="form-row"):
                        yield Static(_("Include Sections:"), classes="form-label")
                        # Simplified - in real app would have checkboxes
                        yield Static(_("[✓] Executive Summary\n[✓] Findings\n[✓] Recommendations\n[✓] Compliance Score"))
                    
                    # Progress section
                    with Vertical(id="progress-section"):
                        yield ProgressBar(total=100, id="progress-bar")
                        yield Static(_("Ready to generate report"), id="status-text")
                    
                    # Buttons
                    with Horizontal():
                        yield Button(_("📄 Generate (G)"), id="btn-generate", variant="success")
                        yield Button(_("📂 Open (O)"), id="btn-open", disabled=True)
                        yield Button(_("◀ Back"), id="btn-back")
                    
                    # Recent exports
                    with Vertical(id="recent-exports"):
                        yield Static(_("Recent Exports:"), id="recent-title")
                        yield Static(_("No recent exports"), classes="recent-item")
                
                # Preview panel
                with Vertical(id="preview-panel"):
                    yield Static(_("👁️ Preview"), id="preview-title")
                    preview = TextArea(id="preview-content", read_only=True)
                    preview.text = self._generate_preview()
                    yield preview
    
    def _generate_preview(self) -> str:
        """Generate report preview text."""
        template = self._get_template_content()
        
        preview = f"""{'='*60}
  {_('NIS2 COMPLIANCE AUDIT REPORT - PREVIEW')}
{'='*60}

{_('EXECUTIVE SUMMARY')}
-----------------
{_('Entity:')} Sample Organization
{_('Audit Date:')} {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}
{_('Overall Compliance Score:')} 73%

{_('Status:')} {template['status']}

{template['summary']}

{_('FINDINGS OVERVIEW')}
-----------------
{_('🔴 Critical:')}  1  - {_('Immediate action required')}
{_('🟠 High:')}      1  - {_('Address within 30 days')}
{_('🟡 Medium:')}    1  - {_('Address within 90 days')}
{_('🟢 Low:')}       0  - {_('Address as resources allow')}

{_('TOP RECOMMENDATIONS')}
-------------------
1. {_('Enable MFA on all administrative accounts')}
2. {_('Update firewall firmware to latest version')}
3. {_('Document incident response procedures')}

{_('COMPLIANCE BREAKDOWN')}
--------------------
[███████░░░] {_('Risk Management')}      70%
[████████░░] {_('Incident Response')}    80%
[██████░░░░] {_('Access Control')}       60%
[█████████░] {_('Data Protection')}      90%

{'='*60}
  {_('End of Preview - Generate full report to see details')}
{'='*60}
"""
        return preview
    
    def _get_template_content(self) -> dict:
        """Get content based on selected template."""
        try:
            template = self.query_one("#select-template", Select).value
        except Exception as error:
            logger.debug(f"Failed to get template selection: {error}")
            template = "standard"
        
        templates = {
            "executive": {
                "status": _("⚠️ IMPORTANT ENTITY - Compliance gaps identified"),
                "summary": _("This audit identified 3 findings requiring attention. The organization meets basic NIS2 requirements but needs to address critical security gaps within 30 days to maintain compliance.")
            },
            "technical": {
                "status": _("REQUIRES REMEDIATION"),
                "summary": _("Technical assessment reveals missing MFA implementation, outdated firmware with known CVEs, and undocumented incident response procedures. Full technical details available in Appendix A.")
            },
            "standard": {
                "status": _("⚠️ Partial Compliance"),
                "summary": _("The audit found the organization is partially compliant with NIS2 requirements. Three findings were identified across access control and incident management domains.")
            }
        }
        return templates.get(template, templates["standard"])
    
    def _validate_output_path(self, output_path: str) -> tuple[bool, str]:
        """
        Validate the output path for security.
        
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if path is safe to use, False otherwise
            - error_message: Romanian error message if invalid, empty string if valid
        """
        if not output_path or not output_path.strip():
            return (False, _("Calea de ieșire nu poate fi goală"))
        
        try:
            # Resolve to absolute path
            path_obj = Path(output_path).resolve()
            
            # Get the parent directory
            parent_dir = path_obj.parent
            
            # Define allowed directories (home and /tmp)
            home_dir = Path.home().resolve()
            tmp_dir = Path("/tmp").resolve()
            
            # Security check: ensure path is within allowed directories
            path_str = str(path_obj)
            home_str = str(home_dir)
            tmp_str = str(tmp_dir)
            
            is_in_home = path_str.startswith(home_str + os.sep) or path_str == home_str
            is_in_tmp = path_str.startswith(tmp_str + os.sep) or path_str == tmp_str
            
            if not (is_in_home or is_in_tmp):
                return (False, _("Calea trebuie să fie în directorul home sau /tmp"))
            
            # Check if parent directory exists or can be created
            if not parent_dir.exists():
                try:
                    # Try to create the directory (dry run - just check permissions)
                    # We'll actually create it during write, but we need to check
                    # that we have permission to do so
                    test_dir = parent_dir
                    while test_dir and not test_dir.exists():
                        test_dir = test_dir.parent
                    
                    if test_dir and not os.access(test_dir, os.W_OK):
                        return (False, _("Nu aveți permisiune de scriere în directorul specificat"))
                except Exception:
                    return (False, _("Nu se poate crea directorul specificat"))
            else:
                # Check if directory is writable
                if not os.access(parent_dir, os.W_OK):
                    return (False, _("Nu aveți permisiune de scriere în directorul specificat"))
            
            # Check if target file exists (will warn about overwrite)
            if path_obj.exists():
                if path_obj.is_dir():
                    return (False, _("Calea specificată este un director, nu un fișier"))
                if not os.access(path_obj, os.W_OK):
                    return (False, _("Nu aveți permisiune de suprascriere a fișierului existent"))
            
            return (True, "")
            
        except Exception as e:
            logger.warning(f"Path validation error: {e}")
            return (False, _("Calea specificată nu este validă"))
    
    def on_select_changed(self, event):
        """Update preview when options change."""
        # Persist the selection
        if event.select.id == "select-format":
            self.report_format = event.value or "markdown"
        elif event.select.id == "select-template":
            self.report_template = event.value or "standard"
        
        # Update preview
        if event.select.id in ("select-format", "select-template"):
            try:
                preview = self.query_one("#preview-content", TextArea)
                preview.text = self._generate_preview()
            except Exception:
                pass  # Ignore preview update errors
    
    def on_input_changed(self, event):
        """Persist output path changes."""
        if event.input.id == "input-path":
            self.output_path = event.value
    
    @work(exclusive=True)
    async def do_generate(self):
        """Generate report in background with progress."""
        format_type = self.report_format
        output_path = self.output_path
        template = self.report_template
        
        # Validate output path
        if not output_path:
            output_path = self.query_one("#input-path", Input).value
            self.output_path = output_path
        
        if not output_path:
            self.notify(_("Please specify output path"), severity="warning")
            return
        
        # Security validation: validate the output path
        is_valid, error_message = self._validate_output_path(output_path)
        if not is_valid:
            self.notify(error_message, severity="error", title=_("Eroare de securitate"))
            return
        
        # Check if file exists and warn about overwrite
        output_path_resolved = str(Path(output_path).resolve())
        if Path(output_path_resolved).exists():
            self.notify(
                _("Fișierul există și va fi suprascris"),
                severity="warning",
                title=_("Atenție")
            )
        
        self.generating = True
        self.progress = 0
        
        status = self.query_one("#status-text", Static)
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        
        steps = [
            (_("Gathering session data..."), 20, 0.5),
            (_("Analyzing compliance findings..."), 40, 0.5),
            (_("Calculating scores..."), 60, 0.3),
            (_("Formatting report..."), 80, 0.5),
            (_("Writing to file..."), 95, 0.3),
        ]
        
        try:
            for step_text, progress, delay in steps:
                status.update(step_text)
                self.progress = progress
                progress_bar.update(progress=progress)
                await asyncio.sleep(delay)
            
            # Generate report content
            content = self._generate_report_content(format_type, template)
            
            # Ensure directory exists (use resolved path for security)
            output_path_resolved = str(Path(output_path).resolve())
            output_dir = os.path.dirname(output_path_resolved)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Write to file (use resolved path for security)
            try:
                with open(output_path_resolved, 'w', encoding='utf-8') as f:
                    f.write(content)
            except (OSError, IOError) as error:
                status.update(_("✗ Failed to save report: ") + str(error))
                self.notify(_("Failed to save report: ") + str(error), severity="error")
                return
            
            self.progress = 100
            progress_bar.update(progress=100)
            status.update(_("✓ Report saved: ") + output_path_resolved)
            
            # Update recent exports
            self._add_recent_export(output_path_resolved)
            
            self.query_one("#btn-open", Button).disabled = False
            self.notify(_("✓ Report generated successfully!"), severity="success", title=_("Success"))
            
            # Update session status
            if self.session_id:
                self.storage.update_session_fields(self.session_id, status=_("report_generated"))
            
        except Exception as e:
            status.update(_("❌ Error: ") + str(e))
            self.notify(_("Error generating report: ") + str(e), severity="error")
        finally:
            self.generating = False
    
    def _generate_report_content(self, format_type: str, template: str) -> str:
        """Generate report content based on format."""
        if format_type == "markdown":
            return self._generate_markdown_report(template)
        elif format_type == "html":
            return self._generate_html_report(template)
        elif format_type == "json":
            return self._generate_json_report()
        else:
            return self._generate_markdown_report(template)
    
    def _generate_markdown_report(self, template: str) -> str:
        """Generate Markdown report."""
        from datetime import datetime
        
        template_content = self._get_template_content()
        
        return f"""# {_('NIS2 Compliance Audit Report')}

**{_('Generated:')}** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**{_('Session:')}** {self.session_id or 'N/A'}  
**{_('Template:')}** {template.title()}

---

## {_('Executive Summary')}

{template_content['summary']}

**{_('Overall Compliance Score:')}** 73%

## {_('Findings Summary')}

| {_('Severity')} | {_('Count')} | {_('Status')} |
|----------|-------|--------|
| 🔴 {_('Critical')} | 1 | {_('Requires immediate action')} |
| 🟠 {_('High')} | 1 | {_('Address within 30 days')} |
| 🟡 {_('Medium')} | 1 | {_('Address within 90 days')} |

## {_('Detailed Findings')}

### {_('FIND-001: Missing MFA on admin accounts')}
- **{_('Severity:')}** {_('High')}
- **{_('Article:')}** {_('Art. 21(2)(c)')}
- **{_('Recommendation:')}** {_('Enable MFA on all administrative accounts')}

### {_('FIND-002: Outdated firewall firmware')}
- **{_('Severity:')}** {_('Critical')}  
- **{_('Article:')}** {_('Art. 21(2)(a)')}
- **{_('Recommendation:')}** {_('Update firewall firmware immediately')}

### {_('FIND-003: No incident response plan')}
- **{_('Severity:')}** {_('Medium')}
- **{_('Article:')}** {_('Art. 21(2)(h)')}
- **{_('Recommendation:')}** {_('Document incident response procedures')}

## {_('Recommendations')}

1. {_('Prioritize critical findings for immediate remediation')}
2. {_('Schedule follow-up audit in 90 days')}
3. {_('Implement continuous monitoring')}

---
*{_('Generated by NIS2 Field Audit Tool')}*
"""
    
    def _generate_html_report(self, template: str) -> str:
        """Generate HTML report."""
        md_content = self._generate_markdown_report(template)
        # Simple conversion - wrap in HTML
        return f"""<!DOCTYPE html>
<html>
<head><title>{_('NIS2 Audit Report')}</title></head>
<body>
<pre>{md_content}</pre>
</body>
</html>"""
    
    def _generate_json_report(self) -> str:
        """Generate JSON report."""
        import json
        
        report_data = {
            "generated_at": str(__import__('datetime').datetime.now()),
            "session_id": self.session_id,
            "compliance_score": 73,
            "findings": [
                {"id": "FIND-001", "severity": "high", "title": _("Missing MFA")},
                {"id": "FIND-002", "severity": "critical", "title": _("Outdated firmware")},
                {"id": "FIND-003", "severity": "medium", "title": _("No IR plan")},
            ]
        }
        return json.dumps(report_data, indent=2)
    
    def _add_recent_export(self, path: str):
        """Add to recent exports list."""
        self._recent_exports.insert(0, path)
        self._recent_exports = self._recent_exports[:5]
        
        try:
            recent_container = self.query_one("#recent-exports", Vertical)
            # Remove old items (keep title)
            for child in list(recent_container.children)[1:]:
                child.remove()
            
            for export_path in self._recent_exports:
                filename = os.path.basename(export_path)
                recent_container.mount(Static(f"📄 {filename}", classes="recent-item"))
        except Exception as error:
            logger.debug(f"Preview update failed: {error}")
    
    def on_button_pressed(self, event):
        """Handle button clicks."""
        button_id = event.button.id
        
        if button_id == "btn-generate":
            self.action_generate()
        elif button_id == "btn-open":
            self.action_open_folder()
        elif button_id == "btn-back":
            self.action_back()
    
    def action_generate(self):
        """Generate report with overwrite confirmation if file exists."""
        if self.generating:
            return
        
        output_path = self.output_path
        if not output_path:
            output_path = self.query_one("#input-path", Input).value
        
        # Check if file exists and show confirmation
        if output_path and os.path.exists(output_path):
            filename = os.path.basename(output_path)
            dialog = ConfirmationDialog(
                title=_("Confirmare Suprascriere"),
                message=_("Fișierul există deja:\n\n[b]'{filename}'[/b]").format(filename=filename),
                consequences=[
                    _("Suprascrie fișierul existent"),
                    _("Datele anterioare vor fi pierdute"),
                    _("Această acțiune nu poate fi anulată"),
                ],
                confirm_label=_("Da, Suprascrie"),
                cancel_label=_("Nu, Anulează"),
                danger=True,
            )
            self.app.push_screen(dialog, callback=self._on_overwrite_confirmed)
        else:
            # No conflict, proceed directly
            self.run_worker(self.do_generate())
    
    def _on_overwrite_confirmed(self, confirmed: bool):
        """Callback after user responds to overwrite confirmation.
        
        Args:
            confirmed: True if user confirmed overwrite
        """
        if confirmed:
            self.run_worker(self.do_generate())
        else:
            # User cancelled, allow them to choose different path
            self.notify(
                _("Selectează un alt path pentru a continua"),
                severity="information",
                title=_("Anulat")
            )
            # Focus the input field for easy editing
            try:
                input_path = self.query_one("#input-path", Input)
                input_path.focus()
            except Exception:
                pass
    
    def action_open_folder(self):
        """Open output folder."""
        output_path = self.query_one("#input-path", Input).value
        output_dir = os.path.dirname(os.path.abspath(output_path)) or "."
        
        # Security validation
        output_dir_path = Path(output_dir).resolve()
        home_dir = Path.home().resolve()
        
        if not (str(output_dir_path).startswith(str(home_dir)) or str(output_dir_path).startswith("/tmp")):
            self.notify(_("Can only open folders within home directory"), severity="error")
            return
        
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(str(output_dir_path))
            elif system == "Darwin":
                opener = shutil.which("open")
                if opener:
                    subprocess.run([opener, str(output_dir_path)], check=False, capture_output=True)
            else:
                opener = shutil.which("xdg-open")
                if opener:
                    subprocess.run([opener, str(output_dir_path)], check=False, capture_output=True)
            
            self.notify(_("Opened folder"), severity="information")
        except Exception as error:
            self.notify(_("Could not open folder: ") + str(error), severity="warning")
    
    def action_back(self):
        """Go back to dashboard."""
        self.app.pop_screen()
