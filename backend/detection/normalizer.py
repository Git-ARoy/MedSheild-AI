import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class NormalizedSecurityEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"EVT-{uuid.uuid4().hex[:8].upper()}")
    timestamp: str
    source: str = "azure_activity_log"
    caller: str
    source_ip: str = "127.0.0.1"
    operation: str
    resource_id: str
    asset_id: Optional[str] = None
    severity: str = "medium"
    status: str = "Success"
    details: str = ""
    raw_event: Optional[Dict[str, Any]] = None

class EventNormalizer:
    """
    Normalizes Azure Activity Log, Event Grid, and direct HomeoCare sandbox telemetry.
    """

    @staticmethod
    def normalize_activity_log(record: Dict[str, Any], mapped_asset: Optional[str] = None) -> NormalizedSecurityEvent:
        caller = (
            record.get("caller")
            or record.get("claims", {}).get("name")
            or record.get("claims", {}).get("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn")
            or "unknown_actor"
        )
        op_raw = record.get("operationName")
        if isinstance(op_raw, dict):
            op_name = op_raw.get("localizedValue") or op_raw.get("value") or "AzureOperation"
        else:
            op_name = op_raw or "AzureOperation"

        status_raw = record.get("status")
        if isinstance(status_raw, dict):
            status = status_raw.get("value") or "Success"
        else:
            status = status_raw or record.get("resultType") or "Success"

        res_id = record.get("resourceId") or record.get("resourceUri") or ""
        source_ip = (
            record.get("httpRequest", {}).get("clientIpAddress")
            or record.get("callerIpAddress")
            or "185.91.22.14"
        )
        ts = record.get("eventTimestamp") or record.get("time") or datetime.now(timezone.utc).isoformat()

        # Severity determination
        op_lower = str(op_name).lower()
        if "delete" in op_lower or "roleassignment" in op_lower or "device" in op_lower:
            severity = "critical" if "device" in op_lower else "high"
        elif "write" in op_lower or "put" in op_lower or "post" in op_lower or "elevat" in op_lower:
            severity = "high"
        elif "failed" in str(status).lower():
            severity = "medium"
        else:
            severity = "low"

        return NormalizedSecurityEvent(
            timestamp=ts,
            source="azure_activity_log",
            caller=str(caller),
            source_ip=str(source_ip),
            operation=str(op_name),
            resource_id=str(res_id),
            asset_id=mapped_asset,
            severity=severity,
            status=str(status),
            details=f"Azure operation '{op_name}' performed by {caller} against {res_id or 'HomeoCare sandbox'}",
            raw_event=record,
        )

    @staticmethod
    def normalize_generic_event(event_dict: Dict[str, Any], mapped_asset: Optional[str] = None) -> NormalizedSecurityEvent:
        ts = event_dict.get("timestamp") or datetime.now(timezone.utc).strftime("%H:%M:%S")
        caller = event_dict.get("user") or event_dict.get("caller") or "nurse_admin"
        source_ip = event_dict.get("source_ip") or event_dict.get("ip") or "185.91.22.14"
        op = event_dict.get("action") or event_dict.get("operation") or "API_ACCESS"
        res = event_dict.get("asset") or event_dict.get("resource_id") or ""
        sev = event_dict.get("severity") or "medium"
        details = event_dict.get("details") or f"Event {op} by {caller} on {res}"

        return NormalizedSecurityEvent(
            timestamp=ts,
            source=event_dict.get("source", "homeocare_telemetry"),
            caller=caller,
            source_ip=source_ip,
            operation=op,
            resource_id=res,
            asset_id=mapped_asset or event_dict.get("asset_id"),
            severity=sev,
            status=event_dict.get("status", "Success"),
            details=details,
            raw_event=event_dict,
        )
