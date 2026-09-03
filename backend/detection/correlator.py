import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from .normalizer import NormalizedSecurityEvent
from twin.graph import HomeoCareDigitalTwin
from azure.resource_mapper import AzureResourceMapper

class CandidateIncident(BaseModel):
    incident_id: str = Field(default_factory=lambda: f"INC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}")
    primary_actor: str
    source_ip: str
    events: List[NormalizedSecurityEvent]
    affected_assets: List[str]
    attack_chain: List[str]
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "new"  # new, investigating, contained, resolved

class IncidentCorrelator:
    """
    Correlates streams of normalized security events into coherent incident candidates
    anchored to the HomeoCare digital twin graph.
    """

    def __init__(self, twin: HomeoCareDigitalTwin, mapper: AzureResourceMapper):
        self.twin = twin
        self.mapper = mapper
        self.event_buffer: List[NormalizedSecurityEvent] = []
        self.active_incidents: Dict[str, CandidateIncident] = {}

    def ingest_event(self, event: NormalizedSecurityEvent) -> Optional[CandidateIncident]:
        # Resolve HomeoCare asset if not already set
        if not event.asset_id:
            event.asset_id = self.mapper.map_to_asset_id(event.resource_id, event.operation)

        self.event_buffer.append(event)
        # Keep buffer bounded to recent 100 events
        if len(self.event_buffer) > 100:
            self.event_buffer.pop(0)

        # Correlate into incident
        return self._correlate_event(event)

    def _correlate_event(self, event: NormalizedSecurityEvent) -> CandidateIncident:
        # Find existing incident matching actor or IP
        key = f"{event.caller}@{event.source_ip}"
        
        if key in self.active_incidents:
            incident = self.active_incidents[key]
            incident.events.append(event)
            if event.asset_id and event.asset_id not in incident.affected_assets:
                incident.affected_assets.append(event.asset_id)
            
            step_desc = f"{event.operation} on {event.asset_id or event.resource_id}"
            if step_desc not in incident.attack_chain:
                incident.attack_chain.append(step_desc)
            return incident

        # Create new incident
        affected = [event.asset_id] if event.asset_id else []
        chain = [f"{event.operation} on {event.asset_id or event.resource_id}"]
        new_inc = CandidateIncident(
            primary_actor=event.caller,
            source_ip=event.source_ip,
            events=[event],
            affected_assets=affected,
            attack_chain=chain,
            status="new",
        )
        self.active_incidents[key] = new_inc
        return new_inc

    def get_recent_events(self, limit: int = 20) -> List[NormalizedSecurityEvent]:
        return list(reversed(self.event_buffer[-limit:]))

    def get_incident(self, incident_id: str) -> Optional[CandidateIncident]:
        for inc in self.active_incidents.values():
            if inc.incident_id == incident_id:
                return inc
        return None
