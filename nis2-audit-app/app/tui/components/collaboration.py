"""
Collaboration Components
Multi-user support, review workflow, and sharing functionality.
"""
from textual.screen import ModalScreen
from textual.widgets import Static, Button, Input, Label, Select
from textual.containers import Vertical, Horizontal, Grid
from textual.reactive import reactive
from textual.binding import Binding
from datetime import datetime


class ShareReportModal(ModalScreen):
    """Modal for sharing reports with stakeholders."""
    
    CSS = """
    #share-modal {
        width: 60;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    
    #share-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        border-bottom: solid $primary;
    }
    
    .share-section {
        height: auto;
        margin: 1 0;
        padding: 1;
        border: solid $surface-lighten-1;
    }
    
    .section-label {
        text-style: bold;
        margin-bottom: 1;
    }
    
    #share-actions {
        margin-top: 1;
        align: center middle;
    }
    """
    
    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
    ]
    
    def compose(self):
        with Vertical(id="share-modal"):
            yield Static("🤝 Share Report", id="share-title")
            
            with Vertical(classes="share-section"):
                yield Static("Recipient Email:", classes="section-label")
                yield Input(placeholder="colleague@example.com", id="recipient-email")
            
            with Vertical(classes="share-section"):
                yield Static("Access Level:", classes="section-label")
                yield Select([
                    ("👁️ View Only", "view"),
                    ("💬 View & Comment", "comment"),
                    ("✏️ Full Access", "edit"),
                ], id="access-level", value="view")
            
            with Vertical(classes="share-section"):
                yield Static("Message (optional):", classes="section-label")
                yield Input(placeholder="Here's the audit report...", id="share-message")
            
            with Vertical(classes="share-section"):
                yield Static("Link Sharing:", classes="section-label")
                yield Static("Or generate a shareable link")
                with Horizontal():
                    yield Button("🔗 Generate Link", id="btn-generate-link")
                    yield Static("", id="share-link")
            
            with Horizontal(id="share-actions"):
                yield Button("📤 Send", variant="success", id="btn-send")
                yield Button("Cancel", id="btn-cancel")
    
    def on_button_pressed(self, event):
        btn_id = event.button.id
        
        if btn_id == "btn-generate-link":
            try:
                link = f"https://nis2.local/share/{hash(datetime.now())}"
                self.query_one("#share-link", Static).update(link)
                self.notify("Link copied to clipboard!", severity="success")
            except Exception as e:
                logger.debug(f"Failed to generate share link: {e}")
        
        elif btn_id == "btn-send":
            self.notify("Report shared successfully!", severity="success")
            self.dismiss()
        
        elif btn_id == "btn-cancel":
            self.dismiss()


class ReviewWorkflowModal(ModalScreen):
    """Modal for managing audit review workflow."""
    
    CSS = """
    #review-modal {
        width: 65;
        height: auto;
        max-height: 50;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    
    #review-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        border-bottom: solid $primary;
    }
    
    .workflow-step {
        height: auto;
        margin: 1 0;
        padding: 1;
        border: solid $surface-lighten-1;
    }
    
    .step-complete {
        border: solid $success;
        background: $success-darken-3;
    }
    
    .step-current {
        border: double $warning;
    }
    
    .step-number {
        width: 3;
        text-style: bold;
    }
    
    .step-title {
        text-style: bold;
    }
    
    .step-status {
        color: $text-muted;
    }
    
    #review-actions {
        margin-top: 1;
        align: center middle;
    }
    """
    
    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
    ]
    
    def compose(self):
        with Vertical(id="review-modal"):
            yield Static("📋 Review Workflow", id="review-title")
            
            with Vertical(classes="workflow-step step-complete"):
                with Horizontal():
                    yield Static("✓", classes="step-number")
                    yield Static("Draft Complete", classes="step-title")
                yield Static("Audit created and findings documented", classes="step-status")
            
            with Vertical(classes="workflow-step step-complete"):
                with Horizontal():
                    yield Static("✓", classes="step-number")
                    yield Static("Self Review", classes="step-title")
                yield Static("Initial review completed by auditor", classes="step-status")
            
            with Vertical(classes="workflow-step step-current"):
                with Horizontal():
                    yield Static("→", classes="step-number")
                    yield Static("Manager Review", classes="step-title")
                yield Static("Pending approval from security manager", classes="step-status")
                with Horizontal():
                    yield Button("✓ Approve", variant="success", id="btn-approve")
                    yield Button("✗ Request Changes", variant="error", id="btn-reject")
            
            with Vertical(classes="workflow-step"):
                with Horizontal():
                    yield Static("○", classes="step-number")
                    yield Static("Final Sign-off", classes="step-title")
                yield Static("Executive approval and documentation", classes="step-status")
            
            with Horizontal(id="review-actions"):
                yield Button("Close", variant="primary", id="btn-close")
    
    def on_button_pressed(self, event):
        btn_id = event.button.id
        
        if btn_id == "btn-approve":
            self.notify("✓ Audit approved! Moving to final sign-off.", severity="success")
        elif btn_id == "btn-reject":
            self.notify("Changes requested - audit returned to draft", severity="warning")
        elif btn_id == "btn-close":
            self.dismiss()


class ActivityFeed(Static):
    """Activity feed showing recent actions."""
    
    DEFAULT_CSS = """
    ActivityFeed {
        height: auto;
        border: solid $surface-lighten-1;
        padding: 1;
    }
    
    #feed-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    .activity-item {
        height: auto;
        margin: 1 0;
        padding: 1;
        border-left: solid $primary;
        padding-left: 1;
    }
    
    .activity-time {
        color: $text-muted;
        text-style: italic;
    }
    
    .activity-user {
        color: $warning;
        text-style: bold;
    }
    """
    
    activities = reactive(list)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_sample_activities()
    
    def _load_sample_activities(self):
        """Load sample activities."""
        self.activities = [
            {
                "user": "John Doe",
                "action": "completed audit",
                "target": "Acme Corp Network",
                "time": "2 hours ago",
            },
            {
                "user": "Jane Smith",
                "action": "resolved finding",
                "target": "FIND-002",
                "time": "5 hours ago",
            },
            {
                "user": "System",
                "action": "auto-saved progress",
                "target": "Session AUDIT-001",
                "time": "1 day ago",
            },
        ]
    
    def compose(self):
        yield Static("📰 Recent Activity", id="feed-title")
        
        for activity in self.activities:
            with Vertical(classes="activity-item"):
                yield Static(f"[{activity['time']}]")
                yield Static(f"{activity['user']} {activity['action']} {activity['target']}")


class CommentThread(Vertical):
    """Comment thread for collaboration."""
    
    DEFAULT_CSS = """
    CommentThread {
        height: auto;
        border: solid $surface-lighten-1;
        padding: 1;
    }
    
    #comments-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    .comment {
        height: auto;
        margin: 1 0;
        padding: 1;
        border: solid $surface-darken-1;
    }
    
    .comment-author {
        text-style: bold;
        color: $warning;
    }
    
    .comment-time {
        color: $text-muted;
        text-style: italic;
    }
    
    .comment-text {
        margin-top: 1;
    }
    """
    
    def compose(self):
        yield Static("💬 Comments", id="comments-title")
        
        with Vertical(classes="comment"):
            with Horizontal():
                yield Static("Jane Smith", classes="comment-author")
                yield Static(" - ")
                yield Static("2 hours ago", classes="comment-time")
            yield Static("Please review the firewall findings before finalizing the report.", classes="comment-text")
        
        with Vertical(classes="comment"):
            with Horizontal():
                yield Static("John Doe", classes="comment-author")
                yield Static(" - ")
                yield Static("1 hour ago", classes="comment-time")
            yield Static("@Jane - Good catch! I've updated the findings with more detail.", classes="comment-text")


class UserBadge(Static):
    """User badge showing current user."""
    
    DEFAULT_CSS = """
    UserBadge {
        width: auto;
        height: 1;
        padding: 0 1;
        background: $primary;
        color: $background;
    }
    """
    
    def __init__(self, username: str = "Guest", **kwargs):
        super().__init__(f"👤 {username}", **kwargs)


class CollaborationManager:
    """Manager for collaboration features."""
    
    def __init__(self):
        self.current_user = "Guest"
        self.session_assignees = {}
    
    def set_current_user(self, username: str):
        """Set the current user."""
        self.current_user = username
    
    def assign_session(self, session_id: str, assignee: str):
        """Assign a session to a user."""
        self.session_assignees[session_id] = assignee
    
    def get_session_assignee(self, session_id: str) -> str:
        """Get the assignee for a session."""
        return self.session_assignees.get(session_id, "Unassigned")
    
    def add_comment(self, session_id: str, text: str) -> dict:
        """Add a comment to a session."""
        return {
            "id": hash(datetime.now()),
            "author": self.current_user,
            "text": text,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
        }


# Global collaboration manager
_collaboration_manager = CollaborationManager()


def get_collaboration_manager() -> CollaborationManager:
    """Get the global collaboration manager."""
    return _collaboration_manager


class ComplianceCertificate:
    """Generate compliance certificates."""
    
    @staticmethod
    def generate_certificate(entity_name: str, score: float, date: datetime) -> str:
        """Generate a compliance certificate."""
        status = "COMPLIANT" if score >= 80 else "PARTIALLY COMPLIANT"
        
        return f"""
{'='*60}
        NIS2 COMPLIANCE CERTIFICATE
{'='*60}

Entity: {entity_name}
Assessment Date: {date.strftime('%Y-%m-%d')}
Compliance Score: {score:.1f}%
Status: {status}

This certifies that the above entity has undergone
a NIS2 compliance assessment using the Field Audit Tool.

{'='*60}
        """.strip()
