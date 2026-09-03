from typing import Dict, List, Optional, Set
from .models import AssetNode, DependencyEdge, AttackPath, ClinicalImpactMetadata

class HomeoCareDigitalTwin:
    """
    In-memory and Azure-synchronized Hospital Digital Twin model for HomeoCare.
    Models canonical assets, network/identity zones, clinical roles, and dependency paths.
    """

    def __init__(self, subscription_id: str = "f282e7fa-8220-48a9-9138-5f1513a1ac14", resource_group: str = "rg-homeocare-sandbox"):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.assets: Dict[str, AssetNode] = {}
        self.edges: List[DependencyEdge] = []
        self._init_canonical_graph()

    def _init_canonical_graph(self):
        rg_prefix = f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}"

        canonical_nodes = [
            AssetNode(
                id="patient_portal",
                name="Patient Portal",
                zone="DMZ",
                criticality=5,
                clinical_role="Patient-facing appointment and status access",
                owner_role="hospital_admin",
                dependencies=["ehr_api"],
                reachable_from=["internet"],
                azure_resource_ids=[f"{rg_prefix}/providers/Microsoft.Web/sites/func-homeocare-api/functions/patient_portal"],
                is_simulated=False,
                clinical_impact=ClinicalImpactMetadata(
                    service="Outpatient Portal",
                    severity="low",
                    affected_workflow="Patient appointment status",
                    downtime_tolerance="high",
                    safe_isolation=True,
                    fallback_workflow="Telephone scheduling",
                ),
            ),
            AssetNode(
                id="identity_service",
                name="Staff Identity Service",
                zone="Identity",
                criticality=9,
                clinical_role="Authentication and authorization for hospital personnel",
                owner_role="hospital_admin",
                dependencies=["ehr_api", "pharmacy_api", "radiology_api"],
                reachable_from=["patient_portal", "dmz"],
                azure_resource_ids=[
                    f"{rg_prefix}/providers/Microsoft.Authorization/roleAssignments",
                    "https://login.microsoftonline.com/homeocare",
                ],
                is_simulated=False,
                clinical_impact=ClinicalImpactMetadata(
                    service="Identity Management",
                    severity="high",
                    affected_workflow="Clinical staff authentication",
                    downtime_tolerance="low",
                    safe_isolation=False,
                    fallback_workflow="Emergency override credentials",
                ),
            ),
            AssetNode(
                id="ehr_api",
                name="EHR API",
                zone="Clinical",
                criticality=10,
                clinical_role="Read/write access to synthetic electronic health records",
                owner_role="doctor",
                dependencies=["patient_db"],
                reachable_from=["identity_service", "patient_portal"],
                azure_resource_ids=[f"{rg_prefix}/providers/Microsoft.Web/sites/func-homeocare-api/functions/ehr_api"],
                is_simulated=False,
                clinical_impact=ClinicalImpactMetadata(
                    service="Electronic Health Records",
                    severity="critical",
                    affected_workflow="Patient medical history and acute orders",
                    downtime_tolerance="low",
                    safe_isolation=False,
                    fallback_workflow="Paper downtime records",
                ),
            ),
            AssetNode(
                id="patient_db",
                name="Patient Database",
                zone="Data",
                criticality=10,
                clinical_role="Synthetic patient records store",
                owner_role="hospital_admin",
                dependencies=[],
                reachable_from=["ehr_api"],
                azure_resource_ids=[
                    f"{rg_prefix}/providers/Microsoft.Storage/storageAccounts/sthomeocare/blobServices/default/containers/patient-records"
                ],
                is_simulated=False,
                clinical_impact=ClinicalImpactMetadata(
                    service="Patient Data Store",
                    severity="critical",
                    affected_workflow="Patient identification and allergy records",
                    downtime_tolerance="low",
                    safe_isolation=False,
                    fallback_workflow="Local cached chart extracts",
                ),
            ),
            AssetNode(
                id="pharmacy_api",
                name="Pharmacy API",
                zone="Clinical",
                criticality=9,
                clinical_role="Medication and pharmacy workflow integration",
                owner_role="pharmacist",
                dependencies=["medication_db", "device_gateway"],
                reachable_from=["identity_service"],
                azure_resource_ids=[f"{rg_prefix}/providers/Microsoft.Web/sites/func-homeocare-api/functions/pharmacy_api"],
                is_simulated=False,
                clinical_impact=ClinicalImpactMetadata(
                    service="Medication Workflow",
                    severity="high",
                    affected_workflow="Medication order synchronization",
                    downtime_tolerance="low",
                    safe_isolation=False,
                    fallback_workflow="Manual verification and emergency dispensing",
                ),
            ),
            AssetNode(
                id="medication_db",
                name="Medication Database",
                zone="Data",
                criticality=9,
                clinical_role="Synthetic prescriptions, orders, and medication state",
                owner_role="pharmacist",
                dependencies=["device_gateway"],
                reachable_from=["pharmacy_api"],
                azure_resource_ids=[
                    f"{rg_prefix}/providers/Microsoft.Storage/storageAccounts/sthomeocare/blobServices/default/containers/medication-state"
                ],
                is_simulated=False,
                clinical_impact=ClinicalImpactMetadata(
                    service="Medication Inventory & Orders",
                    severity="high",
                    affected_workflow="Prescription dispensing validation",
                    downtime_tolerance="low",
                    safe_isolation=True,
                    fallback_workflow="Paper dispensing log",
                ),
            ),
            AssetNode(
                id="radiology_api",
                name="Radiology/PACS API",
                zone="Clinical",
                criticality=8,
                clinical_role="Synthetic imaging workflow",
                owner_role="radiology_technician",
                dependencies=[],
                reachable_from=["identity_service"],
                azure_resource_ids=[f"{rg_prefix}/providers/Microsoft.Web/sites/func-homeocare-api/functions/radiology_api"],
                is_simulated=False,
                clinical_impact=ClinicalImpactMetadata(
                    service="Diagnostic Imaging Workflow",
                    severity="medium",
                    affected_workflow="Radiology order routing",
                    downtime_tolerance="medium",
                    safe_isolation=True,
                    fallback_workflow="Direct modality readout",
                ),
            ),
            AssetNode(
                id="device_gateway",
                name="Medical Device Gateway",
                zone="Device",
                criticality=10,
                clinical_role="Controlled simulation of connected-device gateway",
                owner_role="hospital_admin",
                dependencies=[],
                reachable_from=["pharmacy_api", "medication_db"],
                azure_resource_ids=[f"{rg_prefix}/providers/Microsoft.Web/sites/func-homeocare-api/functions/device_gateway"],
                is_simulated=True,
                clinical_impact=ClinicalImpactMetadata(
                    service="Infusion Pump & Telemetry Gateway",
                    severity="critical",
                    affected_workflow="Bedside medication delivery control plane",
                    downtime_tolerance="low",
                    safe_isolation=False,
                    fallback_workflow="Manual pump programming with dual-nurse sign-off",
                ),
            ),
            AssetNode(
                id="soc_api",
                name="MedShield/SOC API",
                zone="Security",
                criticality=10,
                clinical_role="Receives telemetry and coordinates defensive actions",
                owner_role="security_analyst",
                dependencies=[],
                reachable_from=["log_pipeline"],
                azure_resource_ids=[f"{rg_prefix}/providers/Microsoft.Web/sites/func-homeocare-api/functions/soc_api"],
                is_simulated=False,
                clinical_impact=None,
            ),
            AssetNode(
                id="log_pipeline",
                name="Security Telemetry Pipeline",
                zone="Security",
                criticality=10,
                clinical_role="Central event collection and routing",
                owner_role="security_analyst",
                dependencies=["soc_api"],
                reachable_from=["azure_monitor", "event_grid"],
                azure_resource_ids=[
                    f"{rg_prefix}/providers/Microsoft.OperationalInsights/workspaces/law-homeocare",
                    f"{rg_prefix}/providers/Microsoft.EventGrid/systemTopics/evgt-homeocare",
                ],
                is_simulated=False,
                clinical_impact=None,
            ),
        ]

        for node in canonical_nodes:
            self.assets[node.id] = node

        self.edges = [
            DependencyEdge(
                source="identity_service",
                target="pharmacy_api",
                relationship="authenticated_access",
                required_role="nurse_admin",
                clinical_relevance="high",
                disruption_cost="medium",
            ),
            DependencyEdge(
                source="identity_service",
                target="ehr_api",
                relationship="authenticated_access",
                required_role="doctor",
                clinical_relevance="critical",
                disruption_cost="high",
            ),
            DependencyEdge(
                source="identity_service",
                target="radiology_api",
                relationship="authenticated_access",
                required_role="radiology_technician",
                clinical_relevance="medium",
                disruption_cost="low",
            ),
            DependencyEdge(
                source="ehr_api",
                target="patient_db",
                relationship="database_query",
                required_role="service_principal",
                clinical_relevance="critical",
                disruption_cost="high",
            ),
            DependencyEdge(
                source="pharmacy_api",
                target="medication_db",
                relationship="prescription_order_sync",
                required_role="service_principal",
                clinical_relevance="high",
                disruption_cost="medium",
            ),
            DependencyEdge(
                source="pharmacy_api",
                target="device_gateway",
                relationship="infusion_pump_channel",
                required_role="service_principal",
                clinical_relevance="critical",
                disruption_cost="critical",
            ),
            DependencyEdge(
                source="medication_db",
                target="device_gateway",
                relationship="device_schedule_dispatch",
                required_role="service_principal",
                clinical_relevance="critical",
                disruption_cost="high",
            ),
            DependencyEdge(
                source="patient_portal",
                target="ehr_api",
                relationship="read_only_proxy",
                required_role="patient",
                clinical_relevance="low",
                disruption_cost="low",
            ),
        ]

    def get_asset(self, asset_id: str) -> Optional[AssetNode]:
        return self.assets.get(asset_id)

    def get_all_assets(self) -> List[AssetNode]:
        return list(self.assets.values())

    def find_asset_by_resource_id(self, resource_id: str) -> Optional[AssetNode]:
        res_id_lower = resource_id.lower()
        for asset in self.assets.values():
            for arid in asset.azure_resource_ids:
                if arid.lower() in res_id_lower or res_id_lower in arid.lower():
                    return asset
                
        # Heuristics based on resource naming
        if "patient" in res_id_lower and ("record" in res_id_lower or "blob" in res_id_lower):
            return self.assets.get("patient_db")
        if "medication" in res_id_lower:
            return self.assets.get("medication_db")
        if "pharmacy" in res_id_lower:
            return self.assets.get("pharmacy_api")
        if "device" in res_id_lower or "pump" in res_id_lower:
            return self.assets.get("device_gateway")
        if "ehr" in res_id_lower:
            return self.assets.get("ehr_api")
        if "roleassignment" in res_id_lower or "authorization" in res_id_lower or "entra" in res_id_lower:
            return self.assets.get("identity_service")
        if "portal" in res_id_lower:
            return self.assets.get("patient_portal")
        return None

    def get_dependencies(self, asset_id: str) -> List[str]:
        asset = self.get_asset(asset_id)
        return asset.dependencies if asset else []

    def trace_attack_path(self, source_id: str, target_id: Optional[str] = None) -> Optional[AttackPath]:
        if source_id not in self.assets:
            return None

        # DFS to discover reachable nodes
        visited: Set[str] = set()
        queue: List[List[str]] = [[source_id]]
        found_paths: List[List[str]] = []

        while queue:
            path = queue.pop(0)
            node = path[-1]

            if target_id and node == target_id:
                found_paths.append(path)
                break

            neighbors = [e.target for e in self.edges if e.source == node]
            for neighbor in neighbors:
                if neighbor not in path:
                    new_path = list(path) + [neighbor]
                    queue.append(new_path)
                    found_paths.append(new_path)

        # Select the highest severity path
        chosen_path = max(found_paths, key=lambda p: len(p)) if found_paths else [source_id]

        reachable_clinical = []
        max_crit = 0
        reaches_device = False

        for node_id in chosen_path:
            node = self.assets.get(node_id)
            if node:
                max_crit = max(max_crit, node.criticality)
                if node.clinical_impact:
                    reachable_clinical.append(node.clinical_impact.service)
                if node_id == "device_gateway":
                    reaches_device = True

        return AttackPath(
            source_asset=source_id,
            target_asset=target_id or chosen_path[-1],
            path=chosen_path,
            reachable_clinical_services=reachable_clinical,
            max_criticality=max_crit,
            reaches_device_gateway=reaches_device,
        )

    def update_asset_status(self, asset_id: str, status: str):
        if asset_id in self.assets:
            self.assets[asset_id].security_status = status
