import re
from typing import Optional
from twin.graph import HomeoCareDigitalTwin

class AzureResourceMapper:
    """
    Maps raw Azure Resource IDs, operation names, and target URIs to HomeoCare digital twin assets.
    """

    def __init__(self, twin: HomeoCareDigitalTwin):
        self.twin = twin

    def map_to_asset_id(self, resource_id: str, operation_name: str = "") -> Optional[str]:
        if not resource_id and not operation_name:
            return None

        # First check twin's explicit resource IDs
        matched = self.twin.find_asset_by_resource_id(resource_id)
        if matched:
            return matched.id

        text = (resource_id + " " + operation_name).lower()

        # Azure Identity & RBAC operations
        if "roleassignment" in text or "authorization" in text or "signin" in text or "credential" in text:
            return "identity_service"

        # Storage / DB containers
        if "patient-records" in text or "patient_db" in text or "patientdb" in text:
            return "patient_db"
        if "medication-state" in text or "medication_db" in text or "medicationdb" in text:
            return "medication_db"

        # Microservice HTTP paths
        if "device_gateway" in text or "devicegateway" in text or "infusion" in text or "pump" in text:
            return "device_gateway"
        if "pharmacy" in text:
            return "pharmacy_api"
        if "ehr" in text:
            return "ehr_api"
        if "radiology" in text or "pacs" in text:
            return "radiology_api"
        if "portal" in text:
            return "patient_portal"

        # Log & Event pipeline
        if "operationalinsights" in text or "eventgrid" in text or "monitor" in text:
            return "log_pipeline"

        return None
