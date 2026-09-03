from typing import Dict, Any, List
from .models import AttackPath, ClinicalRiskAssessment, AssetNode
from .graph import HomeoCareDigitalTwin

class ClinicalImpactEngine:
    """
    Deterministic clinical impact and blast-radius evaluation engine.
    Calculates reproducible risk scores and containment trade-offs from HomeoCare twin metadata.
    """

    def __init__(self, twin: HomeoCareDigitalTwin):
        self.twin = twin

    def assess_risk(self, attack_path: AttackPath) -> ClinicalRiskAssessment:
        path_nodes = attack_path.path
        reaches_device = attack_path.reaches_device_gateway

        # Criticality scoring
        max_crit = attack_path.max_criticality
        clinical_services = list(set(attack_path.reachable_clinical_services))

        # Base clinical score calculation
        base_score = max_crit * 8  # Up to 80 for criticality 10
        if reaches_device:
            base_score = max(base_score, 88)
            base_score += 7  # Cap around 95

        # Path depth factor
        if len(path_nodes) >= 3:
            base_score += 5

        score = min(100, max(10, base_score))

        if score >= 85:
            level = "CRITICAL"
        elif score >= 65:
            level = "HIGH"
        elif score >= 40:
            level = "MEDIUM"
        else:
            level = "LOW"

        if reaches_device:
            safety_impact = (
                "CRITICAL: The attack path reaches the Medical Device Gateway simulation boundary. "
                "Unauthorized commands or session establishment at this layer poses direct potential risk "
                "to connected clinical operational technology (infusion delivery scheduling and telemetry). "
                "Immediate containment required before lateral propagation."
            )
        elif "Electronic Health Records" in clinical_services:
            safety_impact = (
                "HIGH: Threat path encompasses core Electronic Health Records (EHR) and Patient Data Store. "
                "Risk of clinical record tampering, allergy omission, or unauthorized bulk exfiltration."
            )
        elif "Medication Workflow" in clinical_services:
            safety_impact = (
                "HIGH: Threat path touches Medication Pharmacy workflows. Potential disruption to prescription "
                "order synchronization and bedside dispensing validation."
            )
        else:
            safety_impact = (
                "LOW/MEDIUM: Compromise confined to administrative or DMZ tiers. No direct clinical operational "
                "or medical device paths currently exposed."
            )

        # Evaluate candidate containment actions with cyber vs clinical trade-offs
        trade_offs = self._evaluate_candidate_actions(attack_path)

        return ClinicalRiskAssessment(
            clinical_risk_score=score,
            clinical_risk_level=level,
            affected_clinical_workflows=clinical_services,
            patient_safety_impact=safety_impact,
            device_boundary_breached=reaches_device,
            candidate_containment_impacts=trade_offs,
        )

    def _evaluate_candidate_actions(self, attack_path: AttackPath) -> Dict[str, Dict[str, Any]]:
        return {
            "revoke_identity_access": {
                "action": "revoke_identity_access",
                "label": "Revoke Compromised Identity & Sessions",
                "cyber_containment_pct": 94,
                "clinical_disruption": "LOW",
                "description": "Revokes active Entra ID user session tokens and disables credentials. Blocks attacker without taking down clinical microservices.",
                "preferred": True,
                "reversible": True,
            },
            "isolate_homeocare_asset": {
                "action": "isolate_homeocare_asset",
                "label": "Network Isolation of Targeted Service",
                "cyber_containment_pct": 98,
                "clinical_disruption": "HIGH",
                "description": "Applies strict Azure NSG Deny rules isolating the targeted API. Completely halts external attack traffic but temporarily halts clinical staff access.",
                "preferred": False,
                "reversible": True,
            },
            "block_source_ip": {
                "action": "block_source_ip",
                "label": "Block Attacker Source IP at Perimeter",
                "cyber_containment_pct": 65,
                "clinical_disruption": "VERY LOW",
                "description": "Adds inbound Deny rule in Azure NSG for attacker IP. Low disruption, but attacker may rotate IPs or use internal proxies.",
                "preferred": False,
                "reversible": True,
            },
        }
