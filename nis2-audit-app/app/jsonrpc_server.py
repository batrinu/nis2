#!/usr/bin/env python3
"""
JSON-RPC server for NIS2 backend.
Reads JSON requests from stdin, writes JSON responses to stdout.
Designed to be spawned by the React Ink frontend.
"""
import sys
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from .storage.db import AuditStorage
from .audit.classifier import EntityClassifier
from .audit.checklist import get_checklist_sections, ComplianceStatus
from .audit.scorer import ComplianceScorer
from .audit.gap_analyzer import GapAnalyzer
from .audit.finding_generator import FindingGenerator, prioritize_findings
from .models import EntityInput, CrossBorderInfo, AuditSession, DeviceCredentials
from .scanner.network_scanner import NmapScanner
from .scanner.device_fingerprint import DeviceFingerprinter


# Setup logging to stderr (won't interfere with stdout JSON)
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('nis2-jsonrpc')


class JSONRPCError:
    """JSON-RPC error codes."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR = -32000


class NIS2JSONRPCServer:
    """JSON-RPC server for NIS2 backend operations."""
    
    # Security limits
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB max request size
    
    def __init__(self, db_path: str = "./audit_sessions.db") -> None:
        """
        Initialize the JSON-RPC server.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path: str = db_path
        self.storage: AuditStorage = AuditStorage(db_path)
        self.classifier: EntityClassifier = EntityClassifier()
        self.scanner: Optional[NmapScanner] = None
        
        # Method handlers
        self.handlers = {
            # Session management
            "list_sessions": self.handle_list_sessions,
            "get_session": self.handle_get_session,
            "create_session": self.handle_create_session,
            "delete_session": self.handle_delete_session,
            
            # Device operations
            "get_devices": self.handle_get_devices,
            "get_device": self.handle_get_device,
            
            # Network scanning
            "get_subnets": self.handle_get_subnets,
            "scan_network": self.handle_scan_network,
            
            # Compliance
            "get_checklist": self.handle_get_checklist,
            "submit_checklist": self.handle_submit_checklist,
            "calculate_score": self.handle_calculate_score,
            
            # Findings
            "get_findings": self.handle_get_findings,
            
            # Reports
            "generate_report": self.handle_generate_report,
            
            # Utility
            "ping": self.handle_ping,
            "health": self.handle_health,
        }
    
    def run(self) -> None:
        """Run the JSON-RPC server loop."""
        logger.info("NIS2 JSON-RPC Server starting...")
        
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            # Security: Check request size
            if len(line) > self.MAX_REQUEST_SIZE:
                logger.error(f"Request too large: {len(line)} bytes")
                response = self.make_error(
                    None, 
                    JSONRPCError.INVALID_REQUEST, 
                    f"Request exceeds maximum size of {self.MAX_REQUEST_SIZE} bytes"
                )
                print(json.dumps(response), flush=True)
                continue
            
            try:
                request = json.loads(line)
                response = self.handle_request(request)
            except json.JSONDecodeError as e:
                response = self.make_error(None, JSONRPCError.PARSE_ERROR, f"Parse error: {e}")
            except Exception as e:
                logger.exception("Unexpected error handling request")
                response = self.make_error(None, JSONRPCError.INTERNAL_ERROR, str(e))
            
            # Write response
            print(json.dumps(response), flush=True)
    
    def handle_request(self, request: Dict) -> Dict:
        """Handle a single JSON-RPC request."""
        # Validate request
        if request.get("jsonrpc") != "2.0":
            return self.make_error(request.get("id"), JSONRPCError.INVALID_REQUEST, "Invalid JSON-RPC version")
        
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if not method:
            return self.make_error(request_id, JSONRPCError.INVALID_REQUEST, "Method required")
        
        # Find handler
        handler = self.handlers.get(method)
        if not handler:
            return self.make_error(request_id, JSONRPCError.METHOD_NOT_FOUND, f"Method not found: {method}")
        
        # Call handler
        try:
            result = handler(params)
            return self.make_success(request_id, result)
        except Exception as e:
            logger.exception(f"Error handling method {method}")
            return self.make_error(request_id, JSONRPCError.SERVER_ERROR, str(e))
    
    def make_success(self, request_id: Any, result: Any) -> Dict:
        """Create a success response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    
    def make_error(self, request_id: Any, code: int, message: str, data: Any = None) -> Dict:
        """Create an error response."""
        error = {"code": code, "message": message}
        if data:
            error["data"] = data
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error
        }
    
    # --- Handlers ---
    
    def handle_ping(self, params: Dict) -> Dict:
        """Health check."""
        return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
    
    def handle_health(self, params: Dict) -> Dict:
        """Detailed health check."""
        return {
            "status": "healthy",
            "version": "0.2.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def handle_list_sessions(self, params: Dict) -> List[Dict]:
        """List all audit sessions."""
        limit = params.get("limit", 50)
        sessions = self.storage.list_sessions(limit=limit)
        
        return [
            {
                "session_id": s.session_id,
                "entity_name": s.entity_name,
                "entity_sector": s.entity_sector,
                "status": s.status,
                "classification": s.classification,
                "device_count": s.device_count,
                "finding_count": s.finding_count,
                "compliance_score": s.compliance_score,
                "created_at": s.created_at.isoformat(),
            }
            for s in sessions
        ]
    
    def handle_get_session(self, params: Dict) -> Optional[Dict]:
        """Get a specific session."""
        session_id = params.get("session_id")
        if not session_id:
            raise ValueError("session_id required")
        
        session = self.storage.get_session(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "entity": {
                "name": session.entity_input.legal_name,
                "sector": session.entity_input.sector,
                "employees": session.entity_input.employee_count,
                "turnover": session.entity_input.annual_turnover_eur,
            },
            "classification": session.classification.model_dump() if session.classification else None,
            "status": session.status,
            "auditor": session.auditor_name,
            "location": session.audit_location,
            "network_segment": session.network_segment,
            "device_count": session.device_count,
            "finding_count": session.finding_count,
            "compliance_score": session.compliance_score,
            "created_at": session.created_at.isoformat(),
        }
    
    def handle_create_session(self, params: Dict) -> Dict:
        """Create a new audit session."""
        entity_data = params.get("entity", {})
        
        entity_input = EntityInput(
            legal_name=entity_data.get("name", ""),
            sector=entity_data.get("sector", ""),
            employee_count=entity_data.get("employees", 0),
            annual_turnover_eur=entity_data.get("turnover", 0.0),
            balance_sheet_total=entity_data.get("balance"),
            cross_border_operations=CrossBorderInfo(
                operates_cross_border=False,
                main_establishment=entity_data.get("country", "DE"),
            ),
            is_public_admin=entity_data.get("is_public_admin", False),
            is_dns_provider=entity_data.get("is_dns_provider", False),
            is_tld_registry=entity_data.get("is_tld_registry", False),
            is_trust_service_provider=entity_data.get("is_trust_service", False),
        )
        
        classification = self.classifier.classify(entity_input)
        
        session = AuditSession(
            entity_input=entity_input,
            classification=classification,
            status="entity_classified",
            auditor_name=params.get("auditor_name"),
            audit_location=params.get("location"),
            network_segment=params.get("network_segment"),
        )
        
        self.storage.create_session(session)
        
        return {
            "session_id": session.session_id,
            "classification": classification.model_dump(mode='json'),
            "status": session.status,
        }
    
    def handle_delete_session(self, params: Dict) -> Dict:
        """Delete a session."""
        session_id = params.get("session_id")
        if not session_id:
            raise ValueError("session_id required")
        
        success = self.storage.delete_session(session_id)
        return {"deleted": success}
    
    def handle_get_devices(self, params: Dict) -> List[Dict]:
        """Get devices for a session."""
        session_id = params.get("session_id")
        if not session_id:
            raise ValueError("session_id required")
        
        devices = self.storage.get_devices(session_id)
        
        return [
            {
                "device_id": d.device_id,
                "ip_address": d.ip_address,
                "hostname": d.hostname,
                "mac_address": d.mac_address,
                "vendor": d.vendor,
                "device_type": d.device_type,
                "os_version": d.os_version,
                "model": d.model,
                "open_ports": d.open_ports,
                "connection_status": d.connection_status,
                "discovery_method": d.discovery_method,
                "last_seen": d.last_seen.isoformat() if d.last_seen else None,
            }
            for d in devices
        ]
    
    def handle_get_device(self, params: Dict) -> Optional[Dict]:
        """Get a specific device."""
        device_id = params.get("device_id")
        if not device_id:
            raise ValueError("device_id required")
        
        device = self.storage.get_device(device_id)
        if not device:
            return None
        
        return {
            "device_id": device.device_id,
            "ip_address": device.ip_address,
            "hostname": device.hostname,
            "vendor": device.vendor,
            "device_type": device.device_type,
            "os_version": device.os_version,
            "connection_status": device.connection_status,
            "command_count": len(device.command_results),
        }
    
    def handle_get_subnets(self, params: Dict) -> List[str]:
        """Get local network subnets."""
        try:
            scanner = NmapScanner()
            return scanner.get_local_subnets()
        except Exception as e:
            logger.warning(f"Could not detect subnets: {e}")
            return ["192.168.1.0/24"]  # Fallback
    
    def handle_scan_network(self, params: Dict) -> Dict:
        """Scan network for devices."""
        session_id = params.get("session_id")
        target = params.get("target")
        scan_type = params.get("scan_type", "quick")
        
        if not session_id or not target:
            raise ValueError("session_id and target required")
        
        scanner = NmapScanner()
        result = scanner.scan_subnet(target, session_id, scan_type=scan_type)
        
        # Fingerprint and save devices
        devices = []
        for host in result.hosts:
            device = DeviceFingerprinter.fingerprint(host)
            device.session_id = session_id
            self.storage.save_device(device)
            devices.append({
                "device_id": device.device_id,
                "ip_address": device.ip_address,
                "vendor": device.vendor,
                "device_type": device.device_type,
            })
        
        session = self.storage.get_session(session_id)
        if session:
            session.status = "network_scanned"
            session.device_count = len(devices)
            self.storage.update_session(session)
        
        return {
            "scan_id": result.scan_id,
            "target": result.target_network,
            "status": result.status,
            "hosts_up": result.hosts_up,
            "duration_seconds": result.duration_seconds,
            "devices": devices,
        }
    
    def handle_get_checklist(self, params: Dict) -> List[Dict]:
        """Get NIS2 checklist sections."""
        sections = get_checklist_sections()
        
        return [
            {
                "domain": s.domain,
                "title": s.title,
                "description": s.description,
                "weight": s.weight,
                "questions": [
                    {
                        "id": q.id,
                        "question": q.question,
                        "description": q.description,
                        "guidance": q.guidance,
                        "nis2_article": q.nis2_article,
                        "options": [
                            {"value": opt.value, "label": opt.label, "score": opt.compliance_score}
                            for opt in q.options
                        ],
                    }
                    for q in s.questions
                ],
            }
            for s in sections
        ]
    
    def handle_submit_checklist(self, params: Dict) -> Dict:
        """Submit checklist responses and calculate score."""
        session_id = params.get("session_id")
        responses = params.get("responses", {})
        
        if not session_id:
            raise ValueError("session_id required")
        
        # Get checklist
        sections = get_checklist_sections()
        
        # Apply responses
        for section in sections:
            for question in section.questions:
                if question.id in responses:
                    resp = responses[question.id]
                    question.status = ComplianceStatus(resp.get("status", "not_started"))
                    question.selected_option = resp.get("option")
                    question.notes = resp.get("notes", "")
        
        # Calculate score
        scorer = ComplianceScorer()
        score = scorer.generate_compliance_score(session_id, sections)
        
        session = self.storage.get_session(session_id)
        if session:
            session.compliance_score = score.overall_score
            session.status = "checklist_completed"
            self.storage.update_session(session)
        
        # Generate and save findings
        # (Simplified - full implementation would analyze devices too)
        
        return {
            "overall_score": score.overall_score,
            "rating": score.rating,
            "domain_scores": {
                "governance": score.governance_score.model_dump(),
                "technical_controls": score.technical_controls_score.model_dump(),
                "incident_response": score.incident_response_score.model_dump(),
                "supply_chain": score.supply_chain_score.model_dump(),
                "documentation": score.documentation_score.model_dump(),
                "management_oversight": score.management_oversight_score.model_dump(),
            },
        }
    
    def handle_calculate_score(self, params: Dict) -> Dict:
        """Calculate compliance score."""
        session_id = params.get("session_id")
        if not session_id:
            raise ValueError("session_id required")
        
        # Get session
        session = self.storage.get_session(session_id)
        if not session or not session.compliance_score:
            return {"error": "No score available"}
        
        return {
            "overall_score": session.compliance_score,
        }
    
    def handle_get_findings(self, params: Dict) -> List[Dict]:
        """Get findings for a session."""
        session_id = params.get("session_id")
        if not session_id:
            raise ValueError("session_id required")
        
        findings = self.storage.get_findings(session_id)
        
        return [
            {
                "finding_id": f.finding_id,
                "title": f.title,
                "description": f.description,
                "severity": f.severity,
                "nis2_article": f.nis2_article,
                "nis2_domain": f.nis2_domain,
                "recommendation": f.recommendation,
                "estimated_effort": f.estimated_effort,
                "status": f.status,
            }
            for f in findings
        ]
    
    def handle_generate_report(self, params: Dict) -> Dict:
        """Generate audit report."""
        session_id = params.get("session_id")
        format_type = params.get("format", "markdown")
        
        if not session_id:
            raise ValueError("session_id required")
        
        # Get data
        session = self.storage.get_session(session_id)
        devices = self.storage.get_devices(session_id)
        findings = self.storage.get_findings(session_id)
        
        if not session:
            raise ValueError("Session not found")
        
        # Generate report (simplified - returns basic info)
        # Full implementation would use ReportGenerator
        
        return {
            "session_id": session_id,
            "entity_name": session.entity_input.legal_name,
            "format": format_type,
            "device_count": len(devices),
            "finding_count": len(findings),
            "compliance_score": session.compliance_score,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


def main() -> None:
    """Entry point for JSON-RPC server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="NIS2 JSON-RPC Server")
    parser.add_argument("--db", default="./audit_sessions.db", help="Database path")
    args = parser.parse_args()
    
    server = NIS2JSONRPCServer(db_path=args.db)
    server.run()


if __name__ == "__main__":
    main()
