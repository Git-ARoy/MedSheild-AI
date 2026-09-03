# MedShield AI
### Autonomous Healthcare Cybersecurity & Hospital Digital Twin Defense

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=flat&logo=google&logoColor=white)](https://ai.google.dev)
[![Gemma 4](https://img.shields.io/badge/Gemma%204-MLX%2FLocal-4285F4?style=flat&logo=google&logoColor=white)](https://github.com/google-deepmind/gemma)
[![Microsoft Azure](https://img.shields.io/badge/Microsoft%20Azure-0078D4?style=flat&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com)
[![AWS SAM](https://img.shields.io/badge/AWS%20SAM-FF9900?style=flat&logo=amazonaws&logoColor=white)](https://aws.amazon.com/serverless/sam/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

---

## 1. Executive Summary

> **"In healthcare, cybersecurity is patient safety."**

Hospital infrastructure is uniquely vulnerable: traditional IT networks are deeply intertwined with electronic health records (EHR), automated pharmacy workflows, and life-critical medical devices (infusion pumps, ventilators, PACS imaging). A technical intrusion (such as credential stuffing or cloud privilege escalation) can rapidly escalate into a direct threat to clinical operations and patient care.

**MedShield AI** is an autonomous defensive cybersecurity decision-support and incident response platform tailored specifically for healthcare. By fusing **real-time security telemetry**, an in-memory **Hospital Digital Twin** graph, and a **multi-tiered AI reasoning engine** (powered by Google Gemini and local Apple Silicon MLX Gemma 4), MedShield AI enables SOC analysts to correlate attack chains, calculate dual cyber and clinical risk, evaluate operational trade-offs, and surgically contain intrusions before they compromise clinical care.

---

## 2. Core Capabilities & Architecture

```
                                  +-------------------------------------------------------+
                                  |            HomeoCare Hospital Telemetry               |
                                  |  (Azure Activity Logs, CloudTrail, Auth, Network NSG)  |
                                  +---------------------------+---------------------------+
                                                              |
                                                              v
+-----------------------------+               +-------------------------------+
|   HomeoCare Digital Twin    | <-----------> |    MedShield Event Ingestion  |
|  (Topology, Criticality,    |               |  (Normalizer & Correlator)    |
|   Clinical Impact Graph)    |               +---------------+---------------+
+--------------+--------------+                               |
               |                                              v
               |                              +-------------------------------+
               |                              |   Autonomous SOC State Machine |
               |                              | (OBSERVE -> CORRELATE -> PLAN)|
               |                              +---------------+---------------+
               |                                              |
               +----------------------+-----------------------+
                                      |
                                      v
                      +-------------------------------+
                      |      AI Provider Router       |
                      +---------------+---------------+
                                      |
            +-------------------------+-------------------------+
            |                         |                         |
            v                         v                         v
   [ Tier 1: Gemini ]      [ Tier 2: Gemma 4 ]       [ Tier 3: Safety Engine ]
  gemini-3.6-flash API     MLX Apple Silicon Local     Deterministic Fallback
            |                         |                         |
            +-------------------------+-------------------------+
                                      |
                                      v
                      +-------------------------------+
                      |    Incident Analysis & Risk   |
                      |   - Cyber Risk (0-100)        |
                      |   - Clinical / Safety Risk    |
                      |   - Containment Trade-Offs    |
                      +---------------+---------------+
                                      |
                                      v
                      +-------------------------------+
                      |  Defensive SOC Operations UI  |
                      |   (Human-in-the-Loop Approval)|
                      +---------------+---------------+
                                      |
                                      v
                      +-------------------------------+
                      |   Surgical Defense & Verify   |
                      | (Revoke IAM / Isolate Assets) |
                      +-------------------------------+
```

### Key Modules:
1. **HomeoCare Hospital Digital Twin (`backend/twin/`)**:
   - In-memory topological graph mapping identities, clinical microservices, databases, and medical device gateways.
   - Contextual nodes: `patient_portal`, `identity_service`, `ehr_api`, `patient_db`, `pharmacy_api`, `medication_db`, `radiology_api`, `device_gateway`.
   - Dynamic clinical criticality scores (1–10) and blast-radius dependency tracing.

2. **Dual-Risk Assessment Engine (`backend/twin/clinical_impact.py`)**:
   - Computes traditional **Cyber Risk Score (0–100)** alongside **Clinical / Patient Safety Risk** (`LOW`, `MODERATE`, `CRITICAL`, `LIFE-THREATENING`).
   - Analyzes potential care disruption (e.g. prescription delays vs. device telemetry tampering).

3. **Multi-Tiered Resilient AI Routing (`backend/ai/router.py`)**:
   - **Tier 1 (Cloud Primary)**: Google Gemini API (`gemini-3.6-flash`) with structured JSON schema outputs and sub-second reasoning.
   - **Tier 2 (Edge/Offline Fallback)**: Local Google Gemma 4 12B Instruct running via Apple Silicon MLX or OpenAI-compatible endpoint. Ensures full air-gapped capability without sending clinical telemetry offsite.
   - **Tier 3 (Deterministic Safety Baseline)**: Hardened rule-based security engine providing a 100% uptime guarantee if no AI endpoint is reachable.

4. **Autonomous SOC State Machine (`backend/agent/state_machine.py`)**:
   - Enforces formal operational phases: `OBSERVING` &rarr; `CORRELATING` &rarr; `INVESTIGATING` &rarr; `ASSESSING_IMPACT` &rarr; `PLANNING_RESPONSE` &rarr; `AWAITING_POLICY_CHECK` &rarr; `EXECUTING_RESPONSE` &rarr; `VERIFYING` &rarr; `CONTAINED`.

5. **Trade-Off Analysis & Surgical Containment (`backend/azure/defense_tools.py`)**:
   - Recommends actionable, granular defense steps (e.g. revoking compromised session tokens or severing specific network edges) while explaining operational trade-offs (e.g. "Isolating `pharmacy_api` prevents device compromise but temporarily delays synthetic EHR order fulfillment").
   - Requires Human-in-the-Loop authorization before taking live cloud actions.

6. **Defensive Operations Dashboard (`frontend/index.html`)**:
   - Dark-mode high-contrast SOC dashboard styled with Tailwind CSS and JetBrains Mono.
   - Live state machine visualizer, interactive digital twin asset grid, dual-risk gauges, attack path before/after containment visualizer, and live telemetry feed.

---

## 3. Repository Structure

```
.
├── Project docs/               # In-depth architectural, API, and clinical specifications
│   ├── API_SPEC.md             # REST API schemas & request/response contracts
│   ├── ARCHITECTURE.md         # Full system architecture & state machine design
│   ├── DESIGN_LANGUAGE.md      # UI design system, color tokens, and layout guidelines
│   ├── Digital_twin.md         # HomeoCare Hospital digital twin specification
│   ├── MedSheild_AI.md         # Project blueprint and technical requirements
│   ├── PROJECT_OVERVIEW.md     # Motivation, persona definition, and threat models
│   ├── REQUIREMENTS.md         # Technical, security, and compliance requirements
│   └── TECH_DECISIONS.md       # Architectural decision records (ADRs)
├── backend/                    # Python / FastAPI core service
│   ├── agent/                  # Orchestrator and finite state machine
│   │   ├── orchestrator.py     # Main event processing loop & SOC controller
│   │   └── state_machine.py    # Agent state transitions & guards
│   ├── ai/                     # Multi-tiered AI routing and structured schemas
│   │   ├── router.py           # Gemini 3.6 Flash / Local Gemma 4 / Deterministic router
│   │   └── schemas.py          # Pydantic models (IncidentAnalysis, Finding, Action)
│   ├── azure/                  # Cloud defense adapters and telemetry mapping
│   │   ├── defense_tools.py    # Simulated and live Azure containment tools
│   │   └── resource_mapper.py  # Maps Azure resource IDs to digital twin assets
│   ├── detection/              # Event ingestion and correlation
│   │   ├── correlator.py       # Multi-event correlation into candidate incidents
│   │   └── normalizer.py       # Standardizes raw security logs
│   ├── twin/                   # In-memory hospital digital twin
│   │   ├── clinical_impact.py  # Patient safety and clinical risk evaluation
│   │   ├── graph.py            # Hospital asset dependency graph & path tracer
│   │   └── models.py           # Asset nodes, edges, and criticality attributes
│   ├── .env.example            # Environment template for API keys & model endpoints
│   ├── app.py                  # FastAPI REST API endpoints
│   ├── lambda_handler.py       # AWS Lambda handler adapter (Mangum)
│   └── requirements.txt        # Python dependencies
├── frontend/                   # Web-based SOC operations interface
│   └── index.html              # Standalone single-page defensive SOC dashboard
├── infra/                      # Infrastructure as Code (Azure Bicep & AWS SAM)
│   ├── azure-deploy.sh         # Shell deployment script for Azure sandbox
│   ├── deploy.sh               # AWS SAM deployment script
│   ├── main.bicep              # Azure Bicep template (Key Vault, Law, Storage, NSG)
│   ├── main.json               # Compiled Azure ARM template
│   └── template.yaml           # AWS SAM Serverless template
└── redteam/                    # Adversary emulation and attack scenario detonators
    ├── revert_azure_sandbox.sh # Resets the sandbox and restores baseline state
    ├── scenario_a_identity_clinical.sh  # Credential compromise -> Clinical traversal
    ├── scenario_b_control_plane.sh      # Cloud control plane privilege escalation
    └── scenario_c_data_exfiltration.sh  # Bulk synthetic EHR data exfiltration
```

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.12+
- Web browser (Chrome, Edge, Safari, Firefox)
- *(Optional)* Google Gemini API Key
- *(Optional)* Local Gemma 4 12B model running on Apple Silicon (MLX) or Ollama

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/Git-ARoy/MedSheild-AI.git
cd MedSheild-AI/backend

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (Optional: works 100% offline out-of-the-box via deterministic engine)
cp .env.example .env
```

### 2. Configure AI Providers (Optional)
Edit `backend/.env` to configure your preferred inference provider:
```ini
# --- Option A: Google Gemini API (Cloud) ---
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.6-flash
AI_PROVIDER=auto

# --- Option B: Local Gemma 4 12B (Apple Silicon MLX / Ollama) ---
AI_PROVIDER=local_gemma
LOCAL_GEMMA_BASE_URL=http://localhost:11434/v1
LOCAL_GEMMA_MODEL=gemma4:12b-mlx
AI_PROVIDER_TIMEOUT_SECONDS=30
```

### 3. Run the Backend Server
```bash
uvicorn app:app --reload --port 8000
```
Verify the server is running by opening: `http://localhost:8000/health`

### 4. Launch the Defensive SOC Dashboard
Open `frontend/index.html` directly in your browser, or serve it via python:
```bash
cd ../frontend
python3 -m http.server 3000
```
Navigate to `http://localhost:3000` to interact with the dashboard.

---

## 5. Adversary Emulation & Red Team Scenarios

MedShield AI includes three automated adversary emulation scenarios that inject synthetic telemetry into the ingestion pipeline:

| Scenario | Name | Target Vector | Clinical Consequence |
|---|---|---|---|
| **Scenario A** | **Identity Compromise & Clinical Traversal** | `nurse_admin` credential burst &rarr; `identity_service` &rarr; `pharmacy_api` &rarr; `device_gateway` | **Life-Critical**: Unauthorized session established with medical device gateway |
| **Scenario B** | **Control Plane Privilege Escalation** | Azure Contributor role assumption &rarr; Azure Key Vault secret harvest | **High**: Infrastructure-wide secret exposure and clinical database tampering risk |
| **Scenario C** | **Synthetic EHR Data Exfiltration** | Anomalous read burst across synthetic patient blob storage (`sthomeocare`) | **Severe**: HIPAA violation risk and synthetic patient identity leakage |

### Executing Red Team Scenarios:
- **From Dashboard**: Select the scenario from the *Red Team Adversary Emulation* panel and click **Detonate Scenario**.
- **From Terminal**:
  ```bash
  # Trigger Scenario A
  bash redteam/scenario_a_identity_clinical.sh

  # Reset sandbox back to clean baseline
  bash redteam/revert_azure_sandbox.sh
  ```

---

## 6. Cloud Deployment

### Microsoft Azure Sandbox (Bicep)
Deploy the complete HomeoCare hospital synthetic infrastructure:
```bash
cd infra
export GEMINI_API_KEY="your-gemini-key"
export AZURE_LOCATION="eastus"
bash azure-deploy.sh
```
This deploys:
- Log Analytics Workspace (`law-homeocare-...`)
- Azure Key Vault (`kv-homeocare-...`) with RBAC & secret storage
- Azure Storage Account with synthetic patient record containers
- Network Security Groups isolating clinical tiers

### AWS Serverless Deployment (SAM)
Deploy the serverless API Gateway and Lambda backend:
```bash
cd infra
sam build --template-file template.yaml
sam deploy --guided
```
To point the frontend at the AWS Lambda endpoint:
```javascript
localStorage.setItem('MEDSHIELD_API', 'https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com');
```

---

## 7. Key REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service status, active AI provider, and containment counts |
| `GET` | `/api/assets` | Full list of HomeoCare hospital assets and criticality |
| `GET` | `/api/assets/{id}` | Detailed asset topology, dependencies, and health state |
| `POST` | `/api/telemetry/ingest` | Ingest raw cloud or network security events |
| `GET` | `/api/telemetry/stream` | Live stream of normalized events & agent state |
| `GET` | `/api/incidents/{id}/analysis` | AI incident investigation, risk scores, and evidence |
| `GET` | `/api/incidents/{id}/attack-path` | Traced lateral traversal path through digital twin |
| `POST` | `/api/incidents/{id}/respond` | Execute surgical containment action (simulated or live) |
| `POST` | `/api/incidents/{id}/verify` | Post-defense verification that attack path was severed |
| `POST` | `/api/redteam/detonate` | Trigger automated adversary scenario (A, B, or C) |
| `POST` | `/api/redteam/revert` | Restore digital twin and sandbox to baseline |

---

## 8. Responsible AI & Healthcare Safety Guardrails

- **Decision-Support Only**: MedShield AI is strictly a cybersecurity decision-support and threat-emulation system. It does not provide medical diagnoses, treatment plans, or clinical recommendations.
- **Human-in-the-Loop Authorization**: No disruptive containment action (e.g. isolating clinical systems or revoking enterprise identity tokens) can execute against live infrastructure without human operator review and sign-off.
- **100% Synthetic Data**: All patient names, medical record numbers, prescription orders, and telemetry events are entirely synthetic. No real protected health information (PHI) or personally identifiable information (PII) is ever ingested or stored.
- **Device Control Boundary**: MedShield AI does not interface directly with physical medical hardware. Containment is applied strictly at the network, identity, and cloud control-plane layers.

---

## 9. License

This project is licensed under the [Apache License 2.0](LICENSE).
