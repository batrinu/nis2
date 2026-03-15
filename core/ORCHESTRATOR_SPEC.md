# Core Orchestrator Specification

## Purpose

Central coordination hub for the NIS2 compliance assessment system. Manages agent routing, context sharing, legal basis validation, evidence chain integrity, and state management across the audit lifecycle.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CORE ORCHESTRATOR                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Agent Router │  │ Context Mgr  │  │ State Machine│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Legal Validator│  │Evidence Chain│  │ Audit Logger │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │ Agent 1 │          │ Agent 2 │          │ Agent N │
   └─────────┘          └─────────┘          └─────────┘
```

---

## 1. Agent Router

### Routing Logic

```python
class AgentRouter:
    """Routes queries to appropriate agents based on mode and context."""
    
    ROUTING_RULES = {
        # Mode-based routing
        "classification": {
            "primary": "entity_classifier",
            "fallback": None,
            "required_context": ["sector", "size_data"]
        },
        "audit": {
            "primary": "audit_assessor",
            "pre_requisites": ["entity_classifier"],
            "required_context": ["entity_classification"]
        },
        "enforcement": {
            "primary": "enforcement_officer",
            "pre_requisites": ["audit_assessor"],
            "required_context": ["audit_result"]
        },
        "gap_analysis": {
            "primary": "gap_analyst",
            "fallback": None,
            "required_context": []
        },
        "reporting": {
            "primary": "report_generator",
            "pre_requisites": ["audit_assessor"],
            "required_context": ["audit_result"]
        },
        "sector_validation": {
            "primary": "sector_specialist",
            "fallback": None,
            "required_context": ["sector"]
        }
    }
    
    def route(
        self,
        query: UserQuery,
        context: AuditContext
    ) -> RoutingDecision:
        """
        Determine which agent(s) should handle the query.
        """
        # Check mode
        mode = query.mode
        rules = self.ROUTING_RULES.get(mode)
        
        if not rules:
            raise UnknownModeError(f"Unknown mode: {mode}")
        
        # Check prerequisites
        for prereq in rules.get("pre_requisites", []):
            if not context.has_completed(prereq):
                return RoutingDecision(
                    action="execute_first",
                    agent=prereq,
                    reason=f"Prerequisite {prereq} must be completed first"
                )
        
        # Check required context
        missing = [
            req for req in rules["required_context"]
            if not context.has_data(req)
        ]
        
        if missing:
            return RoutingDecision(
                action="request_context",
                missing_fields=missing,
                reason=f"Missing required context: {missing}"
            )
        
        return RoutingDecision(
            action="route_to_agent",
            agent=rules["primary"],
            context_injection=self._prepare_context(context, rules["primary"])
        )
```

### Multi-Agent Coordination

For complex workflows requiring multiple agents:

```python
class MultiAgentWorkflow:
    """Coordinate multi-agent workflows."""
    
    WORKFLOWS = {
        "full_audit": [
            ("entity_classifier", {"save_context": True}),
            ("sector_specialist", {"depends_on": ["entity_classifier"]}),
            ("audit_assessor", {"depends_on": ["entity_classifier", "sector_specialist"]}),
            ("report_generator", {"depends_on": ["audit_assessor"], "input": "audit_result"})
        ],
        "enforcement_pipeline": [
            ("audit_assessor", {"save_context": True}),
            ("enforcement_officer", {"depends_on": ["audit_assessor"]}),
            ("report_generator", {"depends_on": ["enforcement_officer"], "template": "enforcement_notice"})
        ],
        "consultation": [
            ("entity_classifier", {"save_context": True}),
            ("gap_analyst", {"depends_on": ["entity_classifier"]}),
            ("report_generator", {"depends_on": ["gap_analyst"], "template": "gap_report"})
        ]
    }
```

---

## 2. Context Sharing

### Shared Memory Structure

```python
class SharedContext:
    """Thread-safe shared memory for agent communication."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.entity_profile: EntityProfile | None = None
        self.audit_history: list[AuditRecord] = []
        self.classification_result: EntityClassification | None = None
        self.audit_result: AuditAssessment | None = None
        self.gap_analysis: GapAnalysisReport | None = None
        self.enforcement_actions: list[EnforcementAction] = []
        self.evidence_registry: EvidenceRegistry = EvidenceRegistry()
        self.decision_log: list[DecisionRecord] = []
        self.metadata: dict = {}
    
    def update(self, key: str, value: Any, agent: str):
        """Update context with audit trail."""
        old_value = getattr(self, key, None)
        setattr(self, key, value)
        
        self.decision_log.append(DecisionRecord(
            timestamp=datetime.utcnow(),
            agent=agent,
            action=f"context_update:{key}",
            old_hash=hash(old_value) if old_value else None,
            new_hash=hash(value)
        ))
    
    def get(self, key: str) -> Any:
        """Retrieve context value."""
        return getattr(self, key, None)
```

### Entity Profile

```python
class EntityProfile(BaseModel):
    """Persistent entity information."""
    
    entity_id: str
    legal_name: str
    trading_names: list[str]
    registration_number: str
    legal_address: Address
    operational_addresses: list[Address]
    
    # Classification
    primary_sector: str
    secondary_sectors: list[str]
    classification: Literal["EE", "IE", "Non-Qualifying"]
    annex: Literal["Annex_I", "Annex_II"]
    
    # Size
    employee_count: int
    annual_turnover_eur: float
    balance_sheet_total: float
    
    # Operations
    member_states: list[str]
    main_establishment: str
    cross_border_operations: bool
    lead_authority: str
    
    # History
    previous_audits: list[AuditHistory]
    compliance_history: ComplianceHistory
    sanctions_history: list[SanctionRecord]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    version: int
```

---

## 3. Legal Basis Validator

### Article Validation

```python
class LegalBasisValidator:
    """Ensures all outputs cite specific NIS2 Articles."""
    
    REQUIRED_ARTICLES = {
        "entity_classification": ["24", "25", "26"],
        "risk_management": ["21(2)(a)"],
        "incident_handling": ["21(2)(b)", "23"],
        "business_continuity": ["21(2)(c)"],
        "supply_chain": ["21(2)(d)", "22"],
        "cryptography": ["21(2)(i)"],
        "access_control": ["21(2)(k)"],
        "enforcement": ["34"],
        "registration": ["24", "25"]
    }
    
    def validate_output(self, output: AgentOutput) -> ValidationResult:
        """
        Validate that output contains proper legal citations.
        """
        findings = output.get_findings()
        
        for finding in findings:
            if not finding.legal_citation:
                return ValidationResult(
                    valid=False,
                    error=f"Finding {finding.id} missing legal citation"
                )
            
            if not self._is_valid_citation(finding.legal_citation):
                return ValidationResult(
                    valid=False,
                    error=f"Invalid citation: {finding.legal_citation}"
                )
        
        return ValidationResult(valid=True)
    
    def _is_valid_citation(self, citation: str) -> bool:
        """Check if citation matches NIS2 format."""
        # Expected formats:
        # "Article 21(2)(a)"
        # "Article 23(3)"
        # "Article 24"
        # "Directive (EU) 2022/2555, Article X"
        patterns = [
            r"Article \d+(\(\d+\))?(\([a-z]\))?",
            r"Directive \(EU\) 2022/2555, Article \d+"
        ]
        return any(re.match(p, citation) for p in patterns)
    
    def suggest_citation(self, finding_type: str) -> str:
        """Suggest appropriate citation for finding type."""
        return self.REQUIRED_ARTICLES.get(finding_type, ["Article 21"])[0]
```

### Citation Enforcement

All agent outputs must pass through:

```python
def validate_and_enhance(
    output: AgentOutput,
    strict: bool = True
) -> AgentOutput:
    """
    Validate citations and suggest additions if missing.
    """
    validator = LegalBasisValidator()
    result = validator.validate_output(output)
    
    if not result.valid:
        if strict:
            raise LegalCitationError(result.error)
        else:
            # Auto-add suggested citation
            for finding in output.findings:
                if not finding.legal_citation:
                    finding.legal_citation = validator.suggest_citation(
                        finding.type
                    )
    
    return output
```

---

## 4. Evidence Chain

### Immutable Evidence Log

```python
class EvidenceChain:
    """Maintains immutable audit trail for regulatory traceability."""
    
    def __init__(self, storage: StorageBackend):
        self.storage = storage
        self.chain: list[EvidenceRecord] = []
        self._load_existing()
    
    def add_evidence(
        self,
        evidence_type: str,
        source: str,
        content_hash: str,
        metadata: dict,
        collected_by: str
    ) -> EvidenceRecord:
        """
        Add evidence to chain with cryptographic linking.
        """
        previous_hash = self.chain[-1].hash if self.chain else "0"
        
        record = EvidenceRecord(
            id=self._generate_id(),
            timestamp=datetime.utcnow(),
            evidence_type=evidence_type,
            source=source,
            content_hash=content_hash,
            previous_hash=previous_hash,
            metadata=metadata,
            collected_by=collected_by
        )
        
        # Calculate hash
        record.hash = self._calculate_hash(record)
        
        self.chain.append(record)
        self.storage.save(record)
        
        return record
    
    def verify_integrity(self) -> IntegrityReport:
        """Verify chain integrity."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            if current.previous_hash != previous.hash:
                return IntegrityReport(
                    valid=False,
                    break_at=i,
                    expected=previous.hash,
                    actual=current.previous_hash
                )
        
        return IntegrityReport(valid=True)
    
    def get_decision_support(self, decision_id: str) -> list[EvidenceRecord]:
        """Retrieve all evidence supporting a specific decision."""
        return [
            r for r in self.chain
            if r.metadata.get("decision_id") == decision_id
        ]
```

### Evidence Types

```python
class EvidenceType(str, Enum):
    DOCUMENT = "document"           # Policy documents, procedures
    TECHNICAL = "technical"         # Scan results, configs
    INTERVIEW = "interview"         # Interview transcripts/notes
    OBSERVATION = "observation"     # Auditor observations
    SYSTEM_GENERATED = "system"     # Logs, automated outputs
    THIRD_PARTY = "third_party"     # External audit reports
    DECLARATION = "declaration"     # Self-declarations
```

---

## 5. State Management

### Audit State Machine

```python
class AuditStateMachine:
    """Manages audit lifecycle states."""
    
    STATES = {
        # Initial states
        "INIT": {"transitions": ["ENTITY_DATA_COLLECTED"]},
        
        # Classification phase
        "ENTITY_DATA_COLLECTED": {
            "transitions": ["CLASSIFICATION_COMPLETE", "CLASSIFICATION_FAILED"]
        },
        "CLASSIFICATION_COMPLETE": {
            "transitions": ["PHASE_1_COMPLETE", "NON_QUALIFYING"]
        },
        "NON_QUALIFYING": {"transitions": ["REPORT_COMPLETE"]},
        
        # Audit phases
        "PHASE_1_COMPLETE": {"transitions": ["PHASE_2_COMPLETE"]},
        "PHASE_2_COMPLETE": {"transitions": ["PHASE_3_COMPLETE"]},
        "PHASE_3_COMPLETE": {"transitions": ["PHASE_4_COMPLETE"]},
        "PHASE_4_COMPLETE": {"transitions": ["PHASE_5_COMPLETE"]},
        "PHASE_5_COMPLETE": {
            "transitions": ["AUDIT_COMPLETE", "ENFORCEMENT_REQUIRED"]
        },
        
        # Outcomes
        "AUDIT_COMPLETE": {"transitions": ["REPORT_COMPLETE"]},
        "ENFORCEMENT_REQUIRED": {
            "transitions": ["ENFORCEMENT_ISSUED", "REMEDIATION_NEGOTIATED"]
        },
        "REMEDIATION_NEGOTIATED": {
            "transitions": ["REMEDIATION_TRACKING", "ENFORCEMENT_ISSUED"]
        },
        "REMEDIATION_TRACKING": {
            "transitions": ["COMPLIANCE_VERIFIED", "ESCALATED_ENFORCEMENT"]
        },
        "ENFORCEMENT_ISSUED": {"transitions": ["APPEAL_RECEIVED", "COMPLIANCE_VERIFIED"]},
        "APPEAL_RECEIVED": {"transitions": ["APPEAL_UPHELD", "APPEAL_REJECTED"]},
        "APPEAL_UPHELD": {"transitions": ["REMEDIATION_NEGOTIATED"]},
        "APPEAL_REJECTED": {"transitions": ["ENFORCEMENT_UPHELD"]},
        
        # Final states
        "REPORT_COMPLETE": {"transitions": []},
        "COMPLIANCE_VERIFIED": {"transitions": []},
        "ENFORCEMENT_UPHELD": {"transitions": []},
        "ESCALATED_ENFORCEMENT": {"transitions": []}
    }
    
    def transition(
        self,
        current_state: str,
        event: str,
        context: dict
    ) -> str:
        """
        Execute state transition.
        """
        state_def = self.STATES.get(current_state)
        if not state_def:
            raise InvalidStateError(f"Unknown state: {current_state}")
        
        if event not in state_def["transitions"]:
            raise InvalidTransitionError(
                f"Cannot transition from {current_state} via {event}"
            )
        
        new_state = self._determine_target_state(event, context)
        
        # Log transition
        self._log_transition(current_state, new_state, event, context)
        
        return new_state
    
    def get_available_actions(self, state: str) -> list[str]:
        """Get available actions from current state."""
        return self.STATES.get(state, {}).get("transitions", [])
```

### State Persistence

```python
class StatePersistence:
    """Persist audit state to database."""
    
    SCHEMA = """
    CREATE TABLE audit_states (
        session_id TEXT PRIMARY KEY,
        entity_id TEXT NOT NULL,
        current_state TEXT NOT NULL,
        state_history JSON NOT NULL,
        context_snapshot JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE state_transitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        from_state TEXT NOT NULL,
        to_state TEXT NOT NULL,
        event TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        context_diff JSON,
        FOREIGN KEY (session_id) REFERENCES audit_states(session_id)
    );
    """
```

---

## Implementation Contract

```python
class Orchestrator:
    def __init__(
        self,
        config: OrchestratorConfig,
        storage: StorageBackend,
        knowledge_base: NIS2KnowledgeBase
    ):
        """Initialize orchestrator with all agents."""
        self.router = AgentRouter()
        self.context_manager = ContextManager(storage)
        self.legal_validator = LegalBasisValidator()
        self.evidence_chain = EvidenceChain(storage)
        self.state_machine = AuditStateMachine()
        
        # Agent registry
        self.agents: dict[str, BaseAgent] = {
            "entity_classifier": EntityClassifier(),
            "audit_assessor": AuditAssessor(),
            "enforcement_officer": EnforcementOfficer(),
            "gap_analyst": GapAnalyst(),
            "report_generator": ReportGenerator(),
            "sector_specialist": SectorSpecialist()
        }
    
    def start_session(self, entity_data: EntityInput) -> Session:
        """Initialize new audit session."""
        pass
    
    def process_query(
        self,
        session_id: str,
        query: UserQuery
    ) -> AgentResponse:
        """Process user query through appropriate agent(s)."""
        # Get context
        context = self.context_manager.get(session_id)
        
        # Route to agent
        decision = self.router.route(query, context)
        
        # Execute
        if decision.action == "route_to_agent":
            agent = self.agents[decision.agent]
            response = agent.execute(query, decision.context_injection)
            
            # Validate legal citations
            response = self.legal_validator.validate_and_enhance(response)
            
            # Update context
            self.context_manager.update(session_id, response, decision.agent)
            
            return response
        
        elif decision.action == "execute_first":
            return AgentResponse(
                status="prerequisite_required",
                message=f"Please complete {decision.agent} first",
                next_step=decision.agent
            )
        
        elif decision.action == "request_context":
            return AgentResponse(
                status="context_required",
                message="Missing required information",
                missing_fields=decision.missing_fields
            )
    
    def execute_workflow(
        self,
        session_id: str,
        workflow_name: str
    ) -> WorkflowResult:
        """Execute multi-agent workflow."""
        pass
    
    def get_session_state(self, session_id: str) -> SessionState:
        """Get current state of audit session."""
        pass
    
    def add_evidence(
        self,
        session_id: str,
        evidence_type: str,
        content: bytes,
        metadata: dict
    ) -> EvidenceRecord:
        """Add evidence to chain."""
        pass
    
    def generate_evidence_report(
        self,
        session_id: str
    ) -> EvidenceReport:
        """Generate evidence chain report."""
        pass
```

---

## CLI Integration

```python
class OrchestratorCLI:
    """Command-line interface for orchestrator."""
    
    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator
    
    def interactive_mode(self):
        """Run interactive CLI session."""
        console = Console()
        
        # Initialize session
        console.print(Panel("NIS2 Compliance Assessment System"))
        entity_data = self._collect_entity_data()
        session = self.orchestrator.start_session(entity_data)
        
        console.print(f"[green]Session started: {session.id}[/green]")
        
        # Main loop
        while True:
            state = self.orchestrator.get_session_state(session.id)
            
            console.print(f"\n[blue]Current state: {state.current_state}[/blue]")
            console.print(f"Available actions: {', '.join(state.available_actions)}")
            
            command = console.input("\n[bold]Command:[/bold] ")
            
            if command == "exit":
                break
            
            response = self.orchestrator.process_query(
                session.id,
                UserQuery(command=command)
            )
            
            self._display_response(response)
```

---

## Testing Requirements

1. **Router Tests:** All routing rules, edge cases
2. **Context Tests:** Data sharing, persistence
3. **Legal Validator Tests:** Citation validation, enforcement
4. **Evidence Chain Tests:** Integrity, tamper detection
5. **State Machine Tests:** All transitions, invalid paths
6. **Integration Tests:** End-to-end workflows
