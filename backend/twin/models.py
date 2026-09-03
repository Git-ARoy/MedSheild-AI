from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class ClinicalImpactMetadata(BaseModel):
    service: str
    severity: Literal["low", "medium", "high", "critical"]
    affected_workflow: str
    downtime_tolerance: Literal["low", "medium", "high"]
    safe_isolation: bool
    fallback_workflow: str

class AssetNode(BaseModel):
    id: str
    name: str
    zone: Literal["DMZ", "Application", "Clinical", "Data", "Identity", "Device", "Security"]
    criticality: int = Field(ge=1, le=10)
    clinical_role: str
    security_status: Literal["healthy", "warning", "compromised", "isolated"] = "healthy"
    owner_role: str
    dependencies: List[str] = Field(default_factory=list)
    reachable_from: List[str] = Field(default_factory=list)
    azure_resource_ids: List[str] = Field(default_factory=list)
    is_simulated: bool = False
    clinical_impact: Optional[ClinicalImpactMetadata] = None

class DependencyEdge(BaseModel):
    source: str
    target: str
    relationship: str
    required_role: str
    clinical_relevance: Literal["none", "low", "medium", "high", "critical"]
    disruption_cost: Literal["none", "low", "medium", "high", "critical"]

class AttackPath(BaseModel):
    source_asset: str
    target_asset: str
    path: List[str]
    reachable_clinical_services: List[str]
    max_criticality: int
    reaches_device_gateway: bool

class ClinicalRiskAssessment(BaseModel):
    clinical_risk_score: int = Field(ge=0, le=100)
    clinical_risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    affected_clinical_workflows: List[str]
    patient_safety_impact: str
    device_boundary_breached: bool
    candidate_containment_impacts: Dict[str, Dict[str, Any]]
