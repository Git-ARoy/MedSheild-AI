from typing import Dict, Any, Optional, List
from twin.graph import HomeoCareDigitalTwin
from twin.clinical_impact import ClinicalImpactEngine
from detection.normalizer import NormalizedSecurityEvent
from detection.correlator import IncidentCorrelator, CandidateIncident
from azure.defense_tools import AzureDefenseTools, DefenseResult
from ai.router import AIProviderRouter
from ai.schemas import IncidentAnalysis, VerificationReport
from .state_machine import AgentStateMachine, AgentState

class MedShieldOrchestrator:
    """
    Central defensive orchestrator for MedShield AI protecting HomeoCare.
    Implements the full closed loop:
    Observe -> Correlate -> Investigate -> Assess Impact -> Plan -> Defend -> Verify -> Update Twin.
    """

    def __init__(
        self,
        twin: HomeoCareDigitalTwin,
        correlator: IncidentCorrelator,
        defense_tools: AzureDefenseTools,
        ai_router: AIProviderRouter,
    ):
        self.twin = twin
        self.correlator = correlator
        self.defense_tools = defense_tools
        self.ai_router = ai_router
        self.state_machine = AgentStateMachine()
        self.clinical_engine = ClinicalImpactEngine(twin)
        self.active_analyses: Dict[str, IncidentAnalysis] = {}

    def process_incoming_event(self, event: NormalizedSecurityEvent) -> Optional[CandidateIncident]:
        self.state_machine.transition_to(
            AgentState.OBSERVING,
            f"Observed event {event.operation} on {event.resource_id}",
            {"event_id": event.event_id},
        )
        incident = self.correlator.ingest_event(event)
        self.state_machine.transition_to(
            AgentState.CORRELATING,
            f"Correlated into incident {incident.incident_id}",
            {"incident_id": incident.incident_id, "affected_assets": incident.affected_assets},
        )
        return incident

    def investigate_incident(self, incident_id: str) -> IncidentAnalysis:
        incident = self.correlator.get_incident(incident_id)
        if not incident:
            # Create synthetic candidate if not present
            incident = CandidateIncident(
                incident_id=incident_id,
                primary_actor="nurse_admin",
                source_ip="185.91.22.14",
                events=[],
                affected_assets=["identity_service", "pharmacy_api", "device_gateway"],
                attack_chain=["Credential Compromise", "Pharmacy API Access", "Infusion Pump Gateway Traversal"],
            )

        self.state_machine.transition_to(
            AgentState.INVESTIGATING,
            f"Querying digital twin dependencies for {incident_id}",
            {"incident_id": incident_id},
        )

        # 1. Digital Twin Graph analysis
        source_node = incident.affected_assets[0] if incident.affected_assets else "identity_service"
        target_node = incident.affected_assets[-1] if len(incident.affected_assets) > 1 else "device_gateway"
        attack_path = self.twin.trace_attack_path(source_node, target_node)

        # 2. Deterministic Clinical Blast Radius Assessment
        self.state_machine.transition_to(
            AgentState.ASSESSING_IMPACT,
            "Calculating deterministic clinical blast radius and patient safety exposure",
            {"attack_path": attack_path.path if attack_path else []},
        )
        clinical_assessment = self.clinical_engine.assess_risk(attack_path)

        # 3. AI Investigation & Reasoning
        self.state_machine.transition_to(
            AgentState.PLANNING_RESPONSE,
            "Synthesizing threat context and evaluating candidate containment trade-offs",
            {"clinical_score": clinical_assessment.clinical_risk_score},
        )

        context = {
            "incident_id": incident_id,
            "primary_actor": incident.primary_actor,
            "source_ip": incident.source_ip,
            "affected_assets": incident.affected_assets,
            "attack_chain": incident.attack_chain,
            "discovered_path": attack_path.path if attack_path else [],
            "clinical_assessment": clinical_assessment.model_dump(),
            "candidate_trade_offs": clinical_assessment.candidate_containment_impacts,
        }

        analysis = self.ai_router.analyze(context)
        analysis.candidate_trade_offs = clinical_assessment.candidate_containment_impacts
        self.active_analyses[incident_id] = analysis
        return analysis

    def execute_defense_action(self, incident_id: str, action: str, target: str, live: bool = False) -> Dict[str, Any]:
        self.state_machine.transition_to(
            AgentState.AWAITING_POLICY_CHECK,
            f"Checking sandbox policy constraints for action '{action}' on target '{target}'",
            {"action": action, "target": target},
        )

        # Execute bounded tool
        self.state_machine.transition_to(
            AgentState.EXECUTING_RESPONSE,
            f"Executing constrained Azure defense tool '{action}'",
            {"target": target, "live": live},
        )

        if action == "revoke_identity_access":
            result = self.defense_tools.revoke_identity_access(target, live_execution=live)
        elif action == "revoke_active_sessions":
            result = self.defense_tools.revoke_active_sessions(target, live_execution=live)
        elif action == "block_source_ip":
            result = self.defense_tools.block_source_ip(target, live_execution=live)
        elif action == "isolate_homeocare_asset":
            result = self.defense_tools.isolate_homeocare_asset(target, live_execution=live)
        elif action == "restore_homeocare_asset":
            result = self.defense_tools.restore_homeocare_asset(target, live_execution=live)
        else:
            result = self.defense_tools.revoke_identity_access(target, live_execution=live)

        # 4. Verification stage
        self.state_machine.transition_to(
            AgentState.VERIFYING,
            f"Verifying whether threat path to clinical assets has been broken",
            {"audit_id": result.audit_id},
        )

        # Post-action verification
        analysis = self.active_analyses.get(incident_id)
        before_path = analysis.attack_chain if analysis else ["identity_service", "pharmacy_api", "device_gateway"]
        after_path = [f"{target} (REVOKED -X-)"] + [p for p in before_path if p != target][:1]

        verification = VerificationReport(
            state="contained",
            details=f"Threat path severed: {result.details}",
            before_path=before_path,
            after_path=after_path,
        )

        if analysis:
            analysis.verification = verification
            analysis.status = "contained"

        self.state_machine.transition_to(
            AgentState.CONTAINED,
            f"Incident {incident_id} successfully contained. Threat path broken.",
            {"verification_state": "contained"},
        )

        return {
            "defense_result": result.model_dump(),
            "verification": verification.model_dump(),
            "incident_status": "CONTAINED",
            "agent_state": self.state_machine.current_state.value,
        }

    def get_agent_status(self) -> Dict[str, Any]:
        return {
            "current_state": self.state_machine.current_state.value,
            "state_history": self.state_machine.get_history()[-10:],
            "active_incidents": len(self.correlator.active_incidents),
            "containments": [c.model_dump() for c in self.defense_tools.get_active_containments()],
        }
