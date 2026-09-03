from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class Finding(BaseModel):
    name: str
    evidence: str

class RecommendedAction(BaseModel):
    tool: str
    target: str
    expected_cyber_effect: str
    expected_clinical_effect: str

class VerificationReport(BaseModel):
    state: Literal["pending", "contained", "partially_contained", "still_active", "verification_failed"]
    details: str = ""
    before_path: List[str] = Field(default_factory=list)
    after_path: List[str] = Field(default_factory=list)

class IncidentAnalysis(BaseModel):
    incident_id: str
    provider: str = "demo_fallback"
    model: str = "deterministic"
    provider_reason: Optional[str] = None
    status: str = "investigating"
    threat_level: Literal["BENIGN", "SUSPICIOUS", "HIGH", "CRITICAL"] = "CRITICAL"
    cyber_risk_score: int = Field(ge=0, le=100)
    clinical_risk_score: int = Field(ge=0, le=100)
    clinical_risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    attack_stage: str = "lateral_movement"
    attack_type: str
    attack_chain: List[str]
    affected_assets: List[str]
    findings: List[Finding]
    clinical_implications: List[str]
    patient_safety_impact: str
    analyst_summary: str
    recommended_action: RecommendedAction
    recommended_actions: List[str] = Field(default_factory=list)
    candidate_trade_offs: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0, le=1)
    verification: VerificationReport = Field(default_factory=lambda: VerificationReport(state="pending"))
