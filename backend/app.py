import json, os, uuid, subprocess
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure local module imports work
import sys
sys.path.insert(0, os.path.dirname(__file__))

# Load .env if present
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k not in os.environ:
                    os.environ[k] = v

from twin.graph import HomeoCareDigitalTwin
from twin.models import AssetNode
from azure.resource_mapper import AzureResourceMapper
from azure.defense_tools import AzureDefenseTools, DefenseResult
from detection.normalizer import EventNormalizer, NormalizedSecurityEvent
from detection.correlator import IncidentCorrelator, CandidateIncident
from ai.schemas import IncidentAnalysis, Finding, RecommendedAction, VerificationReport
from ai.router import AIProviderRouter
from agent.orchestrator import MedShieldOrchestrator
from agent.state_machine import AgentState

app = FastAPI(title="MedShield AI - Defensive Agent for HomeoCare", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Services
twin = HomeoCareDigitalTwin()
mapper = AzureResourceMapper(twin)
correlator = IncidentCorrelator(twin, mapper)
defense_tools = AzureDefenseTools()
ai_router = AIProviderRouter()
orchestrator = MedShieldOrchestrator(twin, correlator, defense_tools, ai_router)

# Request Models
class IngestTelemetryRequest(BaseModel):
    timestamp: Optional[str] = None
    user: Optional[str] = None
    caller: Optional[str] = None
    source_ip: Optional[str] = "185.91.22.14"
    action: Optional[str] = None
    operation: Optional[str] = None
    asset: Optional[str] = None
    resource_id: Optional[str] = None
    severity: str = "medium"
    details: str = ""
    source: str = "azure_activity_log"

class ResponseActionRequest(BaseModel):
    action: str  # revoke_identity_access, isolate_homeocare_asset, block_source_ip, etc.
    target: str
    mode: str = "sandbox_execute"  # sandbox_execute or azure_live

class RedTeamDetonateRequest(BaseModel):
    scenario: Literal["A", "B", "C"] = "A"

# 1. Health Endpoint
@app.get("/health")
def health():
    gemini_key = os.getenv("GEMINI_API_KEY", ai_router.gemini_api_key)
    gemini_configured = bool(gemini_key)
    local_gemma_configured = bool(os.getenv("LOCAL_GEMMA_BASE_URL", "http://localhost:11434/v1"))
    
    pref = os.getenv("AI_PROVIDER", "auto").lower()
    active_provider = "gemini" if gemini_configured else "local_gemma"
    if pref in ["gemini", "local_gemma", "demo"]:
        active_provider = pref

    return {
        "status": "ok",
        "cloud": "azure",
        "environment": "HomeoCare-Sandbox",
        "resource_group": "rg-homeocare-sandbox",
        "gemini_configured": gemini_configured,
        "local_gemma_configured": local_gemma_configured,
        "active_provider": active_provider,
        "model": ai_router.local_gemma_model,
        "agent_state": orchestrator.state_machine.current_state.value,
        "active_containments": len(defense_tools.get_active_containments()),
    }

# 2. Digital Twin Asset Endpoints
@app.get("/api/assets")
def get_assets():
    return {"assets": [a.model_dump() for a in twin.get_all_assets()]}

@app.get("/api/assets/{asset_id}")
def get_asset(asset_id: str):
    asset = twin.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found in HomeoCare twin")
    return asset.model_dump()

# 3. Incident Endpoints
@app.get("/api/incidents")
def get_incidents():
    return {
        "incidents": [
            {
                "incident_id": inc.incident_id,
                "primary_actor": inc.primary_actor,
                "source_ip": inc.source_ip,
                "affected_assets": inc.affected_assets,
                "attack_chain_steps": len(inc.attack_chain),
                "created_at": inc.created_at,
                "status": inc.status,
            }
            for inc in correlator.active_incidents.values()
        ]
    }

@app.get("/api/incidents/{incident_id}")
def get_incident_details(incident_id: str):
    inc = correlator.get_incident(incident_id)
    if not inc:
        # Fallback to creating a candidate if query by demo
        inc = CandidateIncident(
            incident_id=incident_id,
            primary_actor="nurse_admin",
            source_ip="185.91.22.14",
            events=[],
            affected_assets=["identity_service", "pharmacy_api", "device_gateway"],
            attack_chain=["Credential Compromise", "Pharmacy Traversal", "Device Gateway Session"],
        )
    return inc.model_dump()

@app.get("/api/incidents/{incident_id}/events")
def get_incident_events(incident_id: str):
    inc = correlator.get_incident(incident_id)
    if not inc:
        return {"events": []}
    return {"events": [e.model_dump() for e in inc.events]}

@app.get("/api/incidents/{incident_id}/attack-path")
def get_incident_attack_path(incident_id: str):
    inc = correlator.get_incident(incident_id)
    src = inc.affected_assets[0] if (inc and inc.affected_assets) else "identity_service"
    tgt = inc.affected_assets[-1] if (inc and len(inc.affected_assets) > 1) else "device_gateway"
    path = twin.trace_attack_path(src, tgt)
    return path.model_dump() if path else {"path": [src, tgt]}

@app.get("/api/incidents/{incident_id}/analysis")
def get_incident_analysis(incident_id: str):
    if incident_id in orchestrator.active_analyses:
        return orchestrator.active_analyses[incident_id].model_dump()
    # Trigger auto-investigation if not yet analyzed
    analysis = orchestrator.investigate_incident(incident_id)
    return analysis.model_dump()

@app.get("/api/incidents/{incident_id}/actions")
def get_incident_candidate_actions(incident_id: str):
    analysis = orchestrator.active_analyses.get(incident_id)
    if not analysis:
        analysis = orchestrator.investigate_incident(incident_id)
    return {
        "recommended_action": analysis.recommended_action.model_dump(),
        "candidate_trade_offs": analysis.candidate_trade_offs,
    }

# 4. Agent Operations
@app.post("/api/incidents/{incident_id}/investigate")
def investigate_incident(incident_id: str):
    analysis = orchestrator.investigate_incident(incident_id)
    return analysis.model_dump()

@app.post("/api/incidents/{incident_id}/respond")
def respond_to_incident(incident_id: str, req: ResponseActionRequest):
    live = (req.mode == "azure_live")
    result = orchestrator.execute_defense_action(incident_id, req.action, req.target, live=live)
    return result

@app.post("/api/incidents/{incident_id}/verify")
def verify_incident(incident_id: str):
    analysis = orchestrator.active_analyses.get(incident_id)
    if not analysis:
        return {"verification": {"state": "still_active", "details": "No analysis on record to verify."}}
    return {"verification": analysis.verification.model_dump()}

# 5. Telemetry Pipeline
@app.get("/api/telemetry/stream")
def get_telemetry_stream():
    return {
        "stream": [e.model_dump() for e in correlator.get_recent_events(30)],
        "agent_status": orchestrator.get_agent_status(),
    }

@app.post("/api/telemetry/ingest")
def ingest_telemetry(req: IngestTelemetryRequest):
    event_dict = req.model_dump()
    mapped = mapper.map_to_asset_id(req.resource_id or req.asset or "", req.operation or req.action or "")
    normalized = EventNormalizer.normalize_generic_event(event_dict, mapped_asset=mapped)
    incident = orchestrator.process_incoming_event(normalized)
    return {
        "status": "ingested",
        "event_id": normalized.event_id,
        "mapped_asset": normalized.asset_id,
        "incident_id": incident.incident_id if incident else None,
    }

# 6. Red Team Adversary Emulation Endpoints
@app.post("/api/redteam/detonate")
def detonate_redteam_scenario(req: RedTeamDetonateRequest):
    scenario = req.scenario.upper()
    script_map = {
        "A": "redteam/scenario_a_identity_clinical.sh",
        "B": "redteam/scenario_b_control_plane.sh",
        "C": "redteam/scenario_c_data_exfiltration.sh",
    }
    script = script_map.get(scenario, script_map["A"])
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), script)

    if os.path.exists(script_path):
        # Run asynchronous detonation via bash script
        subprocess.Popen(["bash", script_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        # Native Python detonation fallback for cloud environment
        now_str = datetime.now(timezone.utc).strftime("%H:%M:%S")
        if scenario == "A":
            events = [
                {"user": "nurse_admin", "source_ip": "185.91.22.14", "action": "FAILED_LOGIN_BURST", "asset": "Identity Gateway", "severity": "medium", "details": "17 failed logins in 31s"},
                {"user": "nurse_admin", "source_ip": "185.91.22.14", "action": "LOGIN_SUCCESS", "asset": "Identity Gateway", "severity": "high", "details": "Successful login after anomaly"},
                {"user": "nurse_admin", "source_ip": "185.91.22.14", "action": "ROLE_ASSIGNMENT_ESCALATE", "asset": "Identity Gateway", "severity": "high", "details": "Elevated to admin role"},
                {"user": "nurse_admin", "source_ip": "185.91.22.14", "action": "DATA_QUERY_BULK", "asset": "Patient Database", "severity": "high", "details": "Bulk synthetic patient record query"},
                {"user": "nurse_admin", "source_ip": "185.91.22.14", "action": "API_ENUMERATION", "asset": "Medication Service", "severity": "high", "details": "Pharmacy endpoints enumerated"},
                {"user": "nurse_admin", "source_ip": "185.91.22.14", "action": "DEVICE_SESSION_ESTABLISH", "asset": "Infusion Pump Gateway", "severity": "critical", "details": "Unauthorized session on simulated device gateway"},
            ]
        elif scenario == "B":
            events = [
                {"user": "azure_service_operator", "source_ip": "194.26.29.11", "action": "MICROSOFT.AUTHORIZATION/ROLEASSIGNMENTS/WRITE", "asset": "Identity Gateway", "severity": "high", "details": "Unauthorized Contributor role assignment"},
                {"user": "azure_service_operator", "source_ip": "194.26.29.11", "action": "MICROSOFT.INSIGHTS/DIAGNOSTICSETTINGS/DELETE", "asset": "Security Telemetry Pipeline", "severity": "critical", "details": "Attempt to disable Log Analytics audit trail"},
                {"user": "azure_service_operator", "source_ip": "194.26.29.11", "action": "MICROSOFT.NETWORK/NETWORKSECURITYGROUPS/SECURITYRULES/WRITE", "asset": "EHR Admin API", "severity": "high", "details": "Inbound NSG rule opened from public IP"},
                {"user": "azure_service_operator", "source_ip": "194.26.29.11", "action": "MICROSOFT.STORAGE/STORAGEACCOUNTS/LISTKEYS/ACTION", "asset": "Patient Database", "severity": "high", "details": "Storage account master key retrieved"},
            ]
        else:
            events = [
                {"user": "compromised_billing_agent", "source_ip": "91.240.118.82", "action": "BLOB_SAS_GENERATION", "asset": "Patient Database", "severity": "medium", "details": "Shared Access Signature token generated"},
                {"user": "compromised_billing_agent", "source_ip": "91.240.118.82", "action": "STORAGE_BLOB_LIST", "asset": "Patient Database", "severity": "high", "details": "Enumeration of all synthetic patient record blobs"},
                {"user": "compromised_billing_agent", "source_ip": "91.240.118.82", "action": "STORAGE_BLOB_BULK_READ", "asset": "Patient Database", "severity": "critical", "details": "540 synthetic patient encounter summaries downloaded"},
                {"user": "compromised_billing_agent", "source_ip": "91.240.118.82", "action": "EHR_ARCHIVE_EXPORT", "asset": "EHR Admin API", "severity": "critical", "details": "Direct export requested for restricted charts"},
            ]
        for e in events:
            e["timestamp"] = now_str
            e["source"] = "azure_activity_log"
            mapped = mapper.map_to_asset_id(e.get("asset", ""), e.get("action", ""))
            norm = EventNormalizer.normalize_generic_event(e, mapped_asset=mapped)
            orchestrator.process_incoming_event(norm)

    return {
        "status": "DETONATION_INITIATED",
        "scenario": scenario,
        "script": script,
        "message": f"Scenario {scenario} triggered against HomeoCare sandbox. Security events streaming to MedShield.",
    }

@app.post("/api/redteam/revert")
def revert_sandbox():
    defense_tools.active_containments.clear()
    correlator.active_incidents.clear()
    orchestrator.active_analyses.clear()
    for a in twin.get_all_assets():
        a.security_status = "healthy"
    orchestrator.state_machine.transition_to(AgentState.IDLE, "HomeoCare sandbox restored to clean baseline")
    return {
        "status": "REVERT_COMPLETE",
        "systems_healthy": f"{len(twin.assets)}/{len(twin.assets)}",
        "active_incidents": 0,
        "message": "HomeoCare sandbox restored to clean baseline.",
    }
