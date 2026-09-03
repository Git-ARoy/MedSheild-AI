from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class AgentState(str, Enum):
    IDLE = "IDLE"
    OBSERVING = "OBSERVING"
    CORRELATING = "CORRELATING"
    INVESTIGATING = "INVESTIGATING"
    ASSESSING_IMPACT = "ASSESSING_IMPACT"
    PLANNING_RESPONSE = "PLANNING_RESPONSE"
    AWAITING_POLICY_CHECK = "AWAITING_POLICY_CHECK"
    EXECUTING_RESPONSE = "EXECUTING_RESPONSE"
    VERIFYING = "VERIFYING"
    CONTAINED = "CONTAINED"
    PARTIALLY_CONTAINED = "PARTIALLY_CONTAINED"
    STILL_ACTIVE = "STILL_ACTIVE"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"

class StateTransitionRecord(BaseModel):
    from_state: AgentState
    to_state: AgentState
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reason: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentStateMachine:
    """
    Manages the 10-state lifecycle of MedShield AI during incident triage and containment.
    """

    def __init__(self):
        self.current_state: AgentState = AgentState.IDLE
        self.history: List[StateTransitionRecord] = []

    def transition_to(self, new_state: AgentState, reason: str, metadata: Optional[Dict[str, Any]] = None):
        record = StateTransitionRecord(
            from_state=self.current_state,
            to_state=new_state,
            reason=reason,
            metadata=metadata or {},
        )
        self.history.append(record)
        self.current_state = new_state
        return record

    def get_history(self) -> List[Dict[str, Any]]:
        return [r.model_dump() for r in self.history]
