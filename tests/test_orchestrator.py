"""
Tests for Core Orchestrator.
"""
import pytest
from core import Orchestrator, AuditState
from shared.data.mock_entities import EE_ENERGY


class TestOrchestrator:
    """Test cases for orchestrator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = Orchestrator()
    
    def test_start_session(self):
        """Test session creation."""
        session_id = self.orchestrator.start_session(EE_ENERGY)
        
        assert session_id is not None
        assert len(session_id) > 0
        
        state = self.orchestrator.get_session_state(session_id)
        assert state["state"] == "init"
    
    def test_classify_entity(self):
        """Test entity classification through orchestrator."""
        session_id = self.orchestrator.start_session(EE_ENERGY)
        result = self.orchestrator.classify_entity(session_id)
        
        assert result["state"] == "classification_complete"
        assert result["eu_classification"]["classification"] == "Essential Entity"
    
    def test_session_state_transitions(self):
        """Test session state transitions."""
        session_id = self.orchestrator.start_session(EE_ENERGY)
        
        # Initial state
        state = self.orchestrator.get_session_state(session_id)
        assert state["state"] == "init"
        
        # After classification
        self.orchestrator.classify_entity(session_id)
        state = self.orchestrator.get_session_state(session_id)
        assert state["has_classification"] is True
    
    def test_evidence_chain(self):
        """Test evidence chain logging."""
        session_id = self.orchestrator.start_session(EE_ENERGY)
        self.orchestrator.classify_entity(session_id)
        
        evidence = self.orchestrator.get_evidence_chain(session_id)
        
        assert len(evidence) > 0
        assert evidence[0]["evidence_type"] == "session"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
