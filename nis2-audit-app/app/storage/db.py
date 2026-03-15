"""
SQLite session storage for the NIS2 Field Audit App.
Handles persistence of audit sessions, devices, and findings.
Includes hardening: WAL mode, integrity checks, and backup functionality.
"""
import os
import sqlite3
import json
import shutil
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List
from contextlib import contextmanager

# Security: SQLite parameter limit protection (CVE-2026-21696 pattern)
# SQLite has max parameter limit of 32766 (or 999 in older versions)
# We keep well under this limit for safety
MAX_SQLITE_PARAMS = 900  # Conservative limit for compatibility
MAX_JSON_FIELD_SIZE = 10 * 1024 * 1024  # 10MB max for JSON fields

from pydantic import ValidationError

from ..models import (
    AuditSession,
    EntityInput,
    EntityClassification,
    NetworkDevice,
    AuditFinding,
    SessionSummary,
)

# Setup logging
logger = logging.getLogger(__name__)

# Database schema version for migrations
CURRENT_SCHEMA_VERSION = 1


class DatabaseError(Exception):
    """Base exception for database operations."""
    pass


class DatabaseCorruptionError(DatabaseError):
    """Raised when database corruption is detected."""
    pass


def _safe_parse_datetime(value: Optional[str], default: Optional[datetime] = None) -> Optional[datetime]:
    """
    Safely parse a datetime from ISO format string.
    
    Args:
        value: ISO format datetime string or None
        default: Default value to return if parsing fails
        
    Returns:
        Parsed datetime or default value
    """
    if not value:
        return default
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse datetime '{value}': {e}")
        return default


# SECURITY: Valid SQL column names to prevent injection
# These must match the actual database schema
VALID_SESSION_COLUMNS = {
    'session_id', 'entity_input', 'classification', 'status',
    'created_at', 'updated_at', 'started_at', 'completed_at',
    'auditor_name', 'auditor_organization', 'audit_location',
    'network_segment', 'device_count', 'finding_count',
    'compliance_score', 'notes'
}

VALID_DEVICE_COLUMNS = {
    'device_id', 'session_id', 'ip_address', 'hostname', 'mac_address', 'vendor',
    'device_type', 'os_version', 'model', 'interfaces', 'open_ports',
    'discovery_method', 'connection_status', 'last_seen',
    'config', 'config_collected_at', 'config_collected_by',
    'command_results', 'credentials_encrypted', 'notes',
    'created_at', 'updated_at'
}

VALID_FINDING_COLUMNS = {
    'finding_id', 'session_id', 'title', 'description', 'severity',
    'nis2_article', 'nis2_domain', 'evidence', 'evidence_collected_at',
    'evidence_collected_by', 'device_ids', 'config_snippets',
    'recommendation', 'remediation_steps', 'estimated_effort',
    'status', 'resolved_at', 'resolved_by', 'remediation_notes',
    'created_at', 'created_by'
}


def _validate_sql_columns(columns: List[str], valid_columns: set) -> None:
    """
    Validate that column names are in the allowed set.
    
    Args:
        columns: List of column names to validate
        valid_columns: Set of valid column names
        
    Raises:
        DatabaseError: If any column name is invalid
    """
    # SECURITY: SQLite doesn't support parameterized column names
    # This validation prevents SQL injection via column names
    invalid = set(columns) - valid_columns
    if invalid:
        raise DatabaseError(f"Invalid column names: {invalid}")


class AuditStorage:
    """
    SQLite storage for audit session persistence.
    
    Features:
    - Write-Ahead Logging (WAL) for better concurrency and crash recovery
    - Automatic integrity checks on startup
    - Database backup functionality
    - Schema versioning and migrations
    - Proper transaction handling
    """
    
    def __init__(self, db_path: str = "./audit_sessions.db"):
        """Initialize storage with database path."""
        self.db_path = Path(db_path)
        self._ensure_directory()
        self._init_db()
        self._run_integrity_check()
        self._set_file_permissions()
    
    def _ensure_directory(self) -> None:
        """Ensure the database directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _set_file_permissions(self) -> None:
        """
        Set restrictive file permissions on database files.
        Owner read/write only (0o600) for security.
        """
        try:
            if self.db_path.exists():
                # Set owner read/write only (no group/others access)
                os.chmod(self.db_path, 0o600)
                
            # Also set permissions on WAL and SHM files if they exist
            wal_file = self.db_path.parent / f"{self.db_path.name}-wal"
            shm_file = self.db_path.parent / f"{self.db_path.name}-shm"
            
            for file_path in [wal_file, shm_file]:
                if file_path.exists():
                    os.chmod(file_path, 0o600)
                    
        except OSError as e:
            logger.warning(f"Could not set file permissions: {e}")
    
    @contextmanager
    def _get_connection(self, query_only: bool = False):
        """
        Get a database connection with proper settings.
        
        Args:
            query_only: If True, set connection to read-only mode
            
        Yields:
            sqlite3.Connection: Configured database connection
        """
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        try:
            # Security: Disable extension loading to prevent code injection
            conn.enable_load_extension(False)
            
            # Enable WAL mode for better concurrency and crash recovery
            conn.execute("PRAGMA journal_mode=WAL")
            # Sync at normal level (balance between safety and performance)
            conn.execute("PRAGMA synchronous=NORMAL")
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys=ON")
            # Store temp tables in memory for better performance
            conn.execute("PRAGMA temp_store=MEMORY")
            # Set cache size (negative = kilobytes)
            conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
            # Security: Set busy timeout to handle lock contention gracefully
            conn.execute("PRAGMA busy_timeout = 5000")  # 5 seconds
            # Security: Enable secure delete to overwrite deleted data
            conn.execute("PRAGMA secure_delete = ON")
            
            # Read-only mode for queries if requested
            if query_only:
                conn.execute("PRAGMA query_only = ON")
            
            yield conn
        finally:
            conn.close()
    
    def _init_db(self) -> None:
        """Initialize database schema with versioning."""
        with self._get_connection() as conn:
            # Create schema version table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS _schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
            """)
            
            # Get current schema version
            row = conn.execute(
                "SELECT version FROM _schema_version ORDER BY version DESC LIMIT 1"
            ).fetchone()
            current_version = row[0] if row else 0
            
            # Run migrations if needed
            if current_version < CURRENT_SCHEMA_VERSION:
                self._run_migrations(conn, current_version, CURRENT_SCHEMA_VERSION)
            
            # Sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    entity_input TEXT NOT NULL,  -- JSON
                    classification TEXT,  -- JSON
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    auditor_name TEXT,
                    auditor_organization TEXT,
                    audit_location TEXT,
                    network_segment TEXT,
                    device_count INTEGER DEFAULT 0,
                    finding_count INTEGER DEFAULT 0,
                    compliance_score REAL,
                    notes TEXT DEFAULT ''
                )
            """)
            
            # Devices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    hostname TEXT,
                    mac_address TEXT,
                    vendor TEXT,
                    device_type TEXT,
                    os_version TEXT,
                    model TEXT,
                    interfaces TEXT,  -- JSON
                    open_ports TEXT,  -- JSON
                    discovery_method TEXT DEFAULT 'nmap_scan',
                    connection_status TEXT DEFAULT 'pending',
                    last_seen TEXT,
                    config TEXT,  -- JSON
                    config_collected_at TEXT,
                    config_collected_by TEXT,
                    command_results TEXT,  -- JSON
                    credentials_encrypted TEXT,  -- Encrypted credentials
                    notes TEXT DEFAULT '',
                    created_at TEXT,
                    updated_at TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                )
            """)
            
            # Findings table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS findings (
                    finding_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    nis2_article TEXT,
                    nis2_domain TEXT,
                    evidence TEXT,
                    evidence_collected_at TEXT,
                    evidence_collected_by TEXT,
                    device_ids TEXT,  -- JSON
                    config_snippets TEXT,  -- JSON
                    recommendation TEXT,
                    remediation_steps TEXT,  -- JSON
                    estimated_effort TEXT,
                    status TEXT DEFAULT 'open',
                    resolved_at TEXT,
                    resolved_by TEXT,
                    remediation_notes TEXT,
                    created_at TEXT,
                    created_by TEXT DEFAULT 'system',
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                )
            """)
            
            # Remediation tracking table (new)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS remediation_tracking (
                    tracking_id TEXT PRIMARY KEY,
                    finding_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    assigned_to TEXT,
                    due_date TEXT,
                    completed_at TEXT,
                    completed_by TEXT,
                    notes TEXT,
                    created_at TEXT,
                    created_by TEXT,
                    FOREIGN KEY (finding_id) REFERENCES findings(finding_id) ON DELETE CASCADE
                )
            """)
            
            # Audit log table (new)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    action TEXT NOT NULL,
                    entity_type TEXT,
                    entity_id TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    performed_by TEXT,
                    performed_at TEXT NOT NULL,
                    ip_address TEXT
                )
            """)
            
            # Create indexes for performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_devices_session 
                ON devices(session_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_findings_session 
                ON findings(session_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_findings_status 
                ON findings(status)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_remediation_finding 
                ON remediation_tracking(finding_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_log_session 
                ON audit_log(session_id)
            """)
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    def _run_migrations(self, conn: sqlite3.Connection, from_version: int, to_version: int) -> None:
        """Run database migrations."""
        logger.info(f"Running migrations from version {from_version} to {to_version}")
        
        for version in range(from_version + 1, to_version + 1):
            if version == 1:
                # Migration 1: Add evidence timestamps to findings
                try:
                    conn.execute("""
                        ALTER TABLE findings 
                        ADD COLUMN evidence_collected_at TEXT
                    """)
                    conn.execute("""
                        ALTER TABLE findings 
                        ADD COLUMN evidence_collected_by TEXT
                    """)
                    conn.execute("""
                        ALTER TABLE findings 
                        ADD COLUMN remediation_notes TEXT
                    """)
                except sqlite3.OperationalError:
                    # Columns may already exist
                    pass
            
            # Record migration
            conn.execute(
                "INSERT INTO _schema_version (version, applied_at) VALUES (?, ?)",
                (version, datetime.now(timezone.utc).isoformat())
            )
            logger.info(f"Applied migration version {version}")
        
        conn.commit()
    
    def _run_integrity_check(self) -> None:
        """Run quick integrity check on database."""
        try:
            with self._get_connection() as conn:
                # Quick check (faster than full integrity_check)
                result = conn.execute("PRAGMA quick_check").fetchone()
                if result and result[0] != "ok":
                    logger.error(f"Database integrity check failed: {result[0]}")
                    raise DatabaseCorruptionError(f"Database corruption detected: {result[0]}")
                
                logger.debug("Database integrity check passed")
        except sqlite3.Error as e:
            logger.error(f"Database integrity check error: {e}")
            raise DatabaseError(f"Failed to check database integrity: {e}")
    
    def run_full_integrity_check(self) -> str:
        """
        Run full integrity check (slower but more thorough).
        
        Returns:
            str: "ok" if check passes, or error message
        """
        try:
            with self._get_connection() as conn:
                result = conn.execute("PRAGMA integrity_check").fetchone()
                return result[0] if result else "unknown"
        except sqlite3.Error as e:
            logger.error(f"Full integrity check error: {e}")
            return f"error: {e}"
    
    def backup(self, backup_path: Optional[str] = None) -> str:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path for backup file. If None, uses timestamp.
            
        Returns:
            str: Path to backup file
        """
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = str(self.db_path.parent / f"audit_sessions_backup_{timestamp}.db")
        
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Use SQLite backup API for consistent backup
            with self._get_connection() as source_conn:
                dest_conn = sqlite3.connect(str(backup_path))
                try:
                    source_conn.backup(dest_conn)
                    logger.info(f"Database backed up to {backup_path}")
                    return str(backup_path)
                finally:
                    dest_conn.close()
        except sqlite3.Error as e:
            logger.error(f"Backup failed: {e}")
            raise DatabaseError(f"Failed to create backup: {e}")
    
    def restore(self, backup_path: str) -> None:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
        """
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise DatabaseError(f"Backup file not found: {backup_path}")
        
        try:
            # Verify backup integrity first
            test_conn = sqlite3.connect(str(backup_path))
            try:
                result = test_conn.execute("PRAGMA quick_check").fetchone()
                if not result or result[0] != "ok":
                    raise DatabaseError("Backup file is corrupted")
            finally:
                test_conn.close()
            
            # Create backup of current database before restoring
            if self.db_path.exists():
                self.backup(str(self.db_path.parent / "audit_sessions_pre_restore.db"))
            
            # Copy backup to main database
            shutil.copy2(str(backup_path), str(self.db_path))
            logger.info(f"Database restored from {backup_path}")
        except sqlite3.Error as e:
            logger.error(f"Restore failed: {e}")
            raise DatabaseError(f"Failed to restore backup: {e}")
    
    def vacuum(self) -> None:
        """Optimize database by rebuilding it (reduces size and defragments)."""
        try:
            with self._get_connection() as conn:
                conn.execute("VACUUM")
                logger.info("Database vacuumed")
        except sqlite3.Error as e:
            logger.error(f"Vacuum failed: {e}")
            raise DatabaseError(f"Failed to vacuum database: {e}")
    
    def log_audit_event(
        self,
        action: str,
        session_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        performed_by: Optional[str] = None
    ) -> None:
        """
        Log an audit event.
        
        Args:
            action: The action performed (e.g., "create", "update", "delete")
            session_id: Associated session ID
            entity_type: Type of entity affected
            entity_id: ID of entity affected
            old_value: Previous value (for updates)
            new_value: New value
            performed_by: User/system that performed the action
        """
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO audit_log (
                        session_id, action, entity_type, entity_id,
                        old_value, new_value, performed_by, performed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        action,
                        entity_type,
                        entity_id,
                        old_value,
                        new_value,
                        performed_by,
                        datetime.now(timezone.utc).isoformat()
                    )
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to log audit event: {e}")
            # Don't raise - audit logging should not break operations
    
    # ... rest of the existing methods with added logging and error handling ...
    
    def create_session(self, session: AuditSession) -> str:
        """
        Create a new audit session.
        
        Returns:
            Session ID
        """
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO sessions (
                        session_id, entity_input, classification, status,
                        created_at, updated_at, auditor_name, auditor_organization,
                        audit_location, network_segment, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session.session_id,
                        session.entity_input.model_dump_json(),
                        session.classification.model_dump_json() if session.classification else None,
                        session.status,
                        session.created_at.isoformat(),
                        session.updated_at.isoformat(),
                        session.auditor_name,
                        session.auditor_organization,
                        session.audit_location,
                        session.network_segment,
                        session.notes,
                    )
                )
                conn.commit()
            
            # Log the creation
            self.log_audit_event(
                action="create",
                session_id=session.session_id,
                entity_type="session",
                entity_id=session.session_id,
                new_value=session.entity_input.legal_name,
                performed_by=session.auditor_name
            )
            
            logger.info(f"Created session {session.session_id}")
            return session.session_id
        except sqlite3.Error as e:
            logger.error(f"Failed to create session: {e}")
            raise DatabaseError(f"Failed to create session: {e}")
    
    def get_session(self, session_id: str) -> Optional[AuditSession]:
        """Retrieve a session by ID."""
        try:
            with self._get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM sessions WHERE session_id = ?",
                    (session_id,)
                ).fetchone()
                
                if not row:
                    return None
                
                return self._row_to_session(row)
        except sqlite3.Error as e:
            logger.error(f"Failed to get session: {e}")
            raise DatabaseError(f"Failed to retrieve session: {e}") from e
    
    def update_session(self, session: AuditSession) -> None:
        """Update an existing session."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    UPDATE sessions SET
                        entity_input = ?,
                        classification = ?,
                        status = ?,
                        updated_at = ?,
                        started_at = ?,
                        completed_at = ?,
                        auditor_name = ?,
                        auditor_organization = ?,
                        audit_location = ?,
                        network_segment = ?,
                        device_count = ?,
                        finding_count = ?,
                        compliance_score = ?,
                        notes = ?
                    WHERE session_id = ?
                    """,
                    (
                        session.entity_input.model_dump_json(),
                        session.classification.model_dump_json() if session.classification else None,
                        session.status,
                        datetime.now(timezone.utc).isoformat(),
                        session.started_at.isoformat() if session.started_at else None,
                        session.completed_at.isoformat() if session.completed_at else None,
                        session.auditor_name,
                        session.auditor_organization,
                        session.audit_location,
                        session.network_segment,
                        session.device_count,
                        session.finding_count,
                        session.compliance_score,
                        session.notes,
                        session.session_id,
                    )
                )
                conn.commit()
            
            self.log_audit_event(
                action="update",
                session_id=session.session_id,
                entity_type="session",
                entity_id=session.session_id,
                performed_by=session.auditor_name
            )
            
            logger.info(f"Updated session {session.session_id}")
        except sqlite3.Error as e:
            logger.error(f"Failed to update session: {e}")
            raise DatabaseError(f"Failed to update session: {e}")
    
    def update_session_status(
        self,
        session_id: str,
        status: str,
        started: bool = False,
        completed: bool = False
    ) -> None:
        """Update session status with optional timing."""
        now = datetime.now(timezone.utc).isoformat()
        updates = ["status = ?", "updated_at = ?"]
        params = [status, now]
        
        if started:
            updates.append("started_at = ?")
            params.append(now)
        
        if completed:
            updates.append("completed_at = ?")
            params.append(now)
        
        params.append(session_id)
        
        try:
            with self._get_connection() as conn:
                conn.execute(
                    f"UPDATE sessions SET {', '.join(updates)} WHERE session_id = ?",
                    params
                )
                conn.commit()
            
            self.log_audit_event(
                action="status_change",
                session_id=session_id,
                entity_type="session",
                entity_id=session_id,
                new_value=status
            )
            
            logger.info(f"Updated session {session_id} status to {status}")
        except sqlite3.Error as e:
            logger.error(f"Failed to update session status: {e}")
            raise DatabaseError(f"Failed to update session status: {e}")
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all associated data.
        
        Returns:
            True if deleted, False if not found
        """
        try:
            with self._get_connection() as conn:
                # Get session info for audit log
                row = conn.execute(
                    "SELECT entity_input FROM sessions WHERE session_id = ?",
                    (session_id,)
                ).fetchone()
                
                if not row:
                    return False
                
                # Delete will cascade to devices and findings due to FK constraints
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.commit()
            
            self.log_audit_event(
                action="delete",
                session_id=session_id,
                entity_type="session",
                entity_id=session_id
            )
            
            logger.info(f"Deleted session {session_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to delete session: {e}")
            raise DatabaseError(f"Failed to delete session: {e}")
    
    def list_sessions(self, limit: int = 50) -> list[SessionSummary]:
        """List all sessions with summary info."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """
                    SELECT
                        session_id,
                        entity_input,
                        status,
                        classification,
                        device_count,
                        finding_count,
                        compliance_score,
                        created_at,
                        updated_at
                    FROM sessions
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (limit,)
                ).fetchall()
                
                # Use list comprehension for better performance
                return [self._row_to_summary(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to list sessions: {e}")
            raise DatabaseError(f"Failed to list sessions: {e}")
    
    def _row_to_summary(self, row: sqlite3.Row) -> SessionSummary:
        """Convert a database row to a SessionSummary."""
        entity_input = EntityInput.model_validate_json(row["entity_input"])
        classification = None
        if row["classification"]:
            try:
                ec = EntityClassification.model_validate_json(row["classification"])
                classification = ec.classification
            except (ValidationError, KeyError, json.JSONDecodeError):
                pass
        
        return SessionSummary(
            session_id=row["session_id"],
            entity_name=entity_input.legal_name,
            entity_sector=entity_input.sector,
            status=row["status"],
            classification=classification,
            device_count=row["device_count"],
            finding_count=row["finding_count"],
            compliance_score=row["compliance_score"],
            created_at=_safe_parse_datetime(row["created_at"], datetime.now(timezone.utc)),
            updated_at=_safe_parse_datetime(row["updated_at"], datetime.now(timezone.utc)),
        )
    
    def _row_to_session(self, row: sqlite3.Row) -> AuditSession:
        """Convert a database row to an AuditSession."""
        entity_input = EntityInput.model_validate_json(row["entity_input"])
        classification = None
        if row["classification"]:
            try:
                classification = EntityClassification.model_validate_json(row["classification"])
            except (ValidationError, json.JSONDecodeError):
                pass
        
        return AuditSession(
            session_id=row["session_id"],
            entity_input=entity_input,
            classification=classification,
            status=row["status"],
            created_at=_safe_parse_datetime(row["created_at"], datetime.now(timezone.utc)),
            started_at=_safe_parse_datetime(row["started_at"]),
            completed_at=_safe_parse_datetime(row["completed_at"]),
            auditor_name=row["auditor_name"],
            auditor_organization=row["auditor_organization"],
            audit_location=row["audit_location"],
            network_segment=row["network_segment"],
            device_count=row["device_count"] or 0,
            finding_count=row["finding_count"] or 0,
            compliance_score=row["compliance_score"],
            notes=row["notes"] or "",
        )
    
    # ========================================================================
    # Device Methods
    # ========================================================================
    
    def get_devices(self, session_id: str) -> list[NetworkDevice]:
        """Get all devices for a session."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """
                    SELECT * FROM devices WHERE session_id = ? ORDER BY created_at
                    """,
                    (session_id,)
                ).fetchall()
                
                # Use list comprehension for better performance
                return [self._row_to_device(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to get devices: {e}")
            raise DatabaseError(f"Failed to get devices: {e}")
    
    def get_device(self, device_id: str) -> Optional[NetworkDevice]:
        """Get a device by ID."""
        from ..models import NetworkDevice
        
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    "SELECT * FROM devices WHERE device_id = ?",
                    (device_id,)
                ).fetchone()
                
                if not row:
                    return None
                return self._row_to_device(row)
        except sqlite3.Error as e:
            logger.error(f"Failed to get device: {e}")
            raise DatabaseError(f"Failed to get device: {e}") from e
    
    def _validate_json_size(self, data: Optional[str], field_name: str) -> None:
        """Validate JSON field size to prevent database bloat."""
        if data and len(data) > MAX_JSON_FIELD_SIZE:
            raise DatabaseError(
                f"Field {field_name} exceeds maximum size of {MAX_JSON_FIELD_SIZE} bytes"
            )
    
    def save_device(self, device: NetworkDevice) -> None:
        """Save or update a device."""
        try:
            # Validate JSON field sizes before saving
            interfaces_json = json.dumps([i.model_dump() for i in device.interfaces]) if device.interfaces else None
            self._validate_json_size(interfaces_json, "interfaces")
            
            command_results_json = json.dumps(
                [r.model_dump() for r in device.command_results]
            ) if device.command_results else None
            self._validate_json_size(command_results_json, "command_results")
            
            with self._get_connection() as conn:
                # Check if device exists
                existing = conn.execute(
                    "SELECT 1 FROM devices WHERE device_id = ?",
                    (device.device_id,)
                ).fetchone()
                
                device_data = {
                    "device_id": device.device_id,
                    "session_id": device.session_id,
                    "ip_address": device.ip_address,
                    "hostname": device.hostname,
                    "mac_address": device.mac_address,
                    "vendor": device.vendor,
                    "device_type": device.device_type,
                    "os_version": device.os_version,
                    "model": device.model,
                    "interfaces": interfaces_json,
                    "open_ports": json.dumps(device.open_ports) if device.open_ports else None,
                    "discovery_method": device.discovery_method,
                    "connection_status": device.connection_status,
                    "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                    "config": device.config.model_dump_json() if device.config else None,
                    "config_collected_at": None,
                    "config_collected_by": None,
                    "command_results": command_results_json,
                    # SECURITY: Credentials are NOT stored in database
                    "credentials_encrypted": None,
                    "notes": device.notes,
                    "created_at": device.created_at.isoformat() if device.created_at else datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                
                if existing:
                    # Update
                    update_columns = [k for k in device_data.keys() if k != "device_id"]
                    _validate_sql_columns(update_columns, VALID_DEVICE_COLUMNS)
                    update_fields = ", ".join(f"{k} = ?" for k in update_columns)
                    values = [v for k, v in device_data.items() if k != "device_id"]
                    values.append(device.device_id)
                    
                    conn.execute(
                        f"UPDATE devices SET {update_fields} WHERE device_id = ?",
                        values
                    )
                else:
                    # Insert
                    _validate_sql_columns(list(device_data.keys()), VALID_DEVICE_COLUMNS)
                    fields = ", ".join(device_data.keys())
                    placeholders = ", ".join("?" for _ in device_data)
                    conn.execute(
                        f"INSERT INTO devices ({fields}) VALUES ({placeholders})",
                        list(device_data.values())
                    )
                
                conn.commit()
            
            self.log_audit_event(
                action="save" if existing else "create",
                session_id=device.session_id,
                entity_type="device",
                entity_id=device.device_id
            )
            
            logger.debug(f"Saved device {device.device_id}")
        except sqlite3.Error as e:
            logger.error(f"Failed to save device: {e}")
            raise DatabaseError(f"Failed to save device: {e}")
    
    def _row_to_device(self, row: sqlite3.Row) -> NetworkDevice:
        """Convert a database row to a NetworkDevice."""
        from ..models import NetworkDevice, NetworkInterface, DeviceConfig, DeviceCommandResult
        
        # Parse interfaces - use list comprehension for speed
        interfaces = []
        if row["interfaces"]:
            try:
                interfaces = [
                    NetworkInterface(**iface_data) 
                    for iface_data in json.loads(row["interfaces"])
                ]
            except (json.JSONDecodeError, TypeError, ValidationError):
                pass
        
        # Parse open ports
        open_ports = []
        if row["open_ports"]:
            try:
                open_ports = json.loads(row["open_ports"])
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Parse config
        config = None
        if row["config"]:
            try:
                config = DeviceConfig.model_validate_json(row["config"])
            except (ValidationError, json.JSONDecodeError):
                pass
        
        # Parse command results - use list comprehension for speed
        command_results = []
        if row["command_results"]:
            try:
                command_results = [
                    DeviceCommandResult(**result_data)
                    for result_data in json.loads(row["command_results"])
                ]
            except (json.JSONDecodeError, TypeError, ValidationError):
                pass
        
        return NetworkDevice(
            device_id=row["device_id"],
            session_id=row["session_id"],
            ip_address=row["ip_address"],
            hostname=row["hostname"],
            mac_address=row["mac_address"],
            vendor=row["vendor"],
            device_type=row["device_type"],
            os_version=row["os_version"],
            model=row["model"],
            interfaces=interfaces,
            open_ports=open_ports,
            discovery_method=row["discovery_method"] or "nmap_scan",
            connection_status=row["connection_status"] or "pending",
            last_seen=_safe_parse_datetime(row["last_seen"], datetime.now(timezone.utc)),
            config=config,
            command_results=command_results,
            notes=row["notes"] or "",
            created_at=_safe_parse_datetime(row["created_at"], datetime.now(timezone.utc)),
            updated_at=_safe_parse_datetime(row["updated_at"], datetime.now(timezone.utc)),
        )
    
    def delete_device(self, device_id: str) -> bool:
        """Delete a device."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM devices WHERE device_id = ?", (device_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.log_audit_event(
                        action="delete",
                        entity_type="device",
                        entity_id=device_id
                    )
                    logger.info(f"Deleted device {device_id}")
                    return True
                return False
        except sqlite3.Error as e:
            logger.error(f"Failed to delete device: {e}")
            raise DatabaseError(f"Failed to delete device: {e}")
    
    # ========================================================================
    # Finding Methods
    # ========================================================================
    
    def get_findings(self, session_id: str) -> list[AuditFinding]:
        """Get all findings for a session."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """
                    SELECT * FROM findings WHERE session_id = ? ORDER BY created_at
                    """,
                    (session_id,)
                ).fetchall()
                
                # Use list comprehension for better performance
                return [self._row_to_finding(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to get findings: {e}")
            raise DatabaseError(f"Failed to get findings: {e}")
    
    def get_finding(self, finding_id: str) -> Optional[AuditFinding]:
        """Get a finding by ID."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    "SELECT * FROM findings WHERE finding_id = ?",
                    (finding_id,)
                ).fetchone()
                
                if not row:
                    return None
                return self._row_to_finding(row)
        except sqlite3.Error as e:
            logger.error(f"Failed to get finding: {e}")
            raise DatabaseError(f"Failed to get finding: {e}") from e
    
    def save_finding(self, finding: AuditFinding) -> None:
        """Save or update a finding."""
        try:
            with self._get_connection() as conn:
                # Check if finding exists
                existing = conn.execute(
                    "SELECT 1 FROM findings WHERE finding_id = ?",
                    (finding.finding_id,)
                ).fetchone()
                
                finding_data = {
                    "finding_id": finding.finding_id,
                    "session_id": finding.session_id,
                    "title": finding.title,
                    "description": finding.description,
                    "severity": finding.severity,
                    "nis2_article": finding.nis2_article,
                    "nis2_domain": finding.nis2_domain,
                    "evidence": finding.evidence,
                    "device_ids": json.dumps(finding.device_ids) if finding.device_ids else None,
                    "config_snippets": json.dumps(finding.config_snippets) if finding.config_snippets else None,
                    "recommendation": finding.recommendation,
                    "remediation_steps": json.dumps(finding.remediation_steps) if finding.remediation_steps else None,
                    "estimated_effort": finding.estimated_effort,
                    "status": finding.status,
                    "resolved_at": finding.resolved_at.isoformat() if finding.resolved_at else None,
                    "resolved_by": finding.resolved_by,
                    "created_at": finding.created_at.isoformat() if finding.created_at else datetime.now(timezone.utc).isoformat(),
                    "created_by": finding.created_by,
                }
                
                if existing:
                    # Update
                    update_columns = [k for k in finding_data.keys() if k != "finding_id"]
                    _validate_sql_columns(update_columns, VALID_FINDING_COLUMNS)
                    update_fields = ", ".join(f"{k} = ?" for k in update_columns)
                    values = [v for k, v in finding_data.items() if k != "finding_id"]
                    values.append(finding.finding_id)
                    
                    conn.execute(
                        f"UPDATE findings SET {update_fields} WHERE finding_id = ?",
                        values
                    )
                else:
                    # Insert
                    _validate_sql_columns(list(finding_data.keys()), VALID_FINDING_COLUMNS)
                    fields = ", ".join(finding_data.keys())
                    placeholders = ", ".join("?" for _ in finding_data)
                    conn.execute(
                        f"INSERT INTO findings ({fields}) VALUES ({placeholders})",
                        list(finding_data.values())
                    )
                
                conn.commit()
            
            self.log_audit_event(
                action="save" if existing else "create",
                session_id=finding.session_id,
                entity_type="finding",
                entity_id=finding.finding_id
            )
            
            logger.debug(f"Saved finding {finding.finding_id}")
        except sqlite3.Error as e:
            logger.error(f"Failed to save finding: {e}")
            raise DatabaseError(f"Failed to save finding: {e}")
    
    def _row_to_finding(self, row: sqlite3.Row) -> AuditFinding:
        """Convert a database row to an AuditFinding."""
        # Parse device_ids
        device_ids = []
        if row["device_ids"]:
            try:
                device_ids = json.loads(row["device_ids"])
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Parse config_snippets
        config_snippets = []
        if row["config_snippets"]:
            try:
                config_snippets = json.loads(row["config_snippets"])
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Parse remediation_steps
        remediation_steps = []
        if row["remediation_steps"]:
            try:
                remediation_steps = json.loads(row["remediation_steps"])
            except (json.JSONDecodeError, TypeError):
                pass
        
        return AuditFinding(
            finding_id=row["finding_id"],
            session_id=row["session_id"],
            title=row["title"],
            description=row["description"],
            severity=row["severity"],
            nis2_article=row["nis2_article"],
            nis2_domain=row["nis2_domain"],
            evidence=row["evidence"] or "",
            device_ids=device_ids,
            config_snippets=config_snippets,
            recommendation=row["recommendation"] or "",
            remediation_steps=remediation_steps,
            estimated_effort=row["estimated_effort"],
            status=row["status"] or "open",
            resolved_at=_safe_parse_datetime(row["resolved_at"]),
            resolved_by=row["resolved_by"],
            created_at=_safe_parse_datetime(row["created_at"], datetime.now(timezone.utc)),
            created_by=row["created_by"] or "system",
        )
    
    def delete_finding(self, finding_id: str) -> bool:
        """Delete a finding."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM findings WHERE finding_id = ?", (finding_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.log_audit_event(
                        action="delete",
                        entity_type="finding",
                        entity_id=finding_id
                    )
                    logger.info(f"Deleted finding {finding_id}")
                    return True
                return False
        except sqlite3.Error as e:
            logger.error(f"Failed to delete finding: {e}")
            raise DatabaseError(f"Failed to delete finding: {e}")
    
    # ========================================================================
    # Convenience Methods
    # ========================================================================
    
    def update_session_fields(self, session_id: str, **fields) -> None:
        """
        Update specific fields of a session.
        Used by TUI screens and CLI for partial updates.
        """
        allowed_fields = {
            "status", "auditor_name", "auditor_organization", "audit_location",
            "network_segment", "device_count", "finding_count", "compliance_score", "notes"
        }
        
        # Filter to only allowed fields
        update_fields = {k: v for k, v in fields.items() if k in allowed_fields}
        
        # Always update the updated_at field
        update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        try:
            with self._get_connection() as conn:
                _validate_sql_columns(list(update_fields.keys()), VALID_SESSION_COLUMNS)
                set_clause = ", ".join(f"{k} = ?" for k in update_fields.keys())
                values = list(update_fields.values())
                values.append(session_id)
                
                conn.execute(
                    f"UPDATE sessions SET {set_clause} WHERE session_id = ?",
                    values
                )
                conn.commit()
            
            self.log_audit_event(
                action="update_fields",
                session_id=session_id,
                entity_type="session",
                entity_id=session_id,
                new_value=str(update_fields)
            )
            
            logger.debug(f"Updated session {session_id} fields: {list(update_fields.keys())}")
        except sqlite3.Error as e:
            logger.error(f"Failed to update session fields: {e}")
            raise DatabaseError(f"Failed to update session fields: {e}")
