# MedShield AI - Requirements and Features

## 1. Functional requirements

### FR-01: Health status

The backend must expose a health endpoint that confirms that the API is running and indicates whether a Gemini API key is configured.

Current endpoint:

`GET /health`

Expected fields:

- `status`
- `gemini_configured`

### FR-02: Sample healthcare security telemetry

The system must expose the predefined demo event sequence used by the primary judging scenario.

The six events are:

1. 17 failed logins against `nurse_admin` from one source IP.
2. Successful login after the brute-force burst.
3. Privilege escalation to system administrator.
4. Bulk access to the Patient Database.
5. Enumeration of Medication Service configuration endpoints.
6. Unauthorized session against the Infusion Pump Gateway.

Each event contains:

- timestamp
- user
- source IP
- action
- asset
- severity
- details

### FR-03: Incident analysis

The backend must accept an ordered security-event sequence and return a structured incident analysis.

The analysis must contain:

- `threat_level`: BENIGN, SUSPICIOUS, HIGH, or CRITICAL
- `cyber_risk_score`: integer 0-100
- `clinical_risk_score`: integer 0-100
- `clinical_risk`: LOW, MEDIUM, HIGH, or CRITICAL
- `attack_type`
- `attack_chain`
- `affected_assets`
- `findings`
- `patient_safety_impact`
- `analyst_summary`
- `recommended_actions`
- `confidence`: 0-1

### FR-04: Primary Gemini reasoning

When the Gemini API is configured and reachable, the backend must call Gemini and request JSON output constrained to the application schema.

Gemini must be instructed to:

- analyze the security sequence;
- reconstruct the attack chain;
- assess cyber risk;
- assess clinical-operational risk;
- explain evidence;
- produce a containment-oriented playbook;
- be conservative around medical-device access;
- avoid patient diagnosis;
- avoid instructions for direct modification of real medical devices.

The backend must validate Gemini output using the existing Pydantic `IncidentAnalysis` schema. Invalid model output should be treated as a backend error or handled by a safe fallback strategy, not silently parsed as arbitrary text.

### FR-05: Local Gemma 4 12B fallback

When Gemini cannot be used because credentials are absent, the API is unreachable, the request times out, the provider returns a recoverable service error, or the Gemini SDK is unavailable, the backend must attempt local inference using Google Gemma 4 12B Instruct (`google/gemma-4-12B-it`).

The local model must be accessed through a provider adapter and must return the same validated `IncidentAnalysis` schema used by Gemini. The backend must not expose provider-specific output formats to the frontend.

The preferred local-serving interface is an OpenAI-compatible HTTP API. A local `llama-server`/similar inference server is acceptable. The default development endpoint should be configurable rather than hardcoded into application logic.

### FR-06: Deterministic final fallback

If both Gemini and the local Gemma provider are unavailable, the backend must return the deterministic `demo_analysis()` result. The response must identify that the result came from `demo_fallback` and must not claim that a live model performed the analysis.

This is required because the hackathon demo must remain functional if network access, credentials, quotas, local-model availability, or AI configuration fail.

### FR-07: Attack simulation

The frontend must expose a **Simulate Attack** action.

Simulation must:

1. populate the event stream with the sample events;
2. request AI analysis;
3. update the dashboard with the resulting incident assessment;
4. reset the simulated containment state.

### FR-08: Visual attack chain

The UI must show the returned `attack_chain` as a sequence of numbered nodes/steps.

The intended primary chain is:

`Brute-force burst -> Account takeover -> Privilege escalation -> Patient-data access -> Medication-service access -> Medical-device gateway access`

### FR-09: Clinical impact display

The UI must clearly separate technical cyber severity from clinical-operational risk.

At minimum show:

- cyber risk score;
- clinical risk score;
- clinical risk level;
- patient-safety impact narrative.

### FR-10: Evidence display

The UI must show the AI findings as evidence-backed cards. Each finding must contain a name and supporting evidence.

### FR-11: Response playbook

The UI must show `recommended_actions` as an ordered analyst playbook.

For the demo scenario, expected actions include:

- disable the compromised account;
- block the source IP and revoke sessions;
- isolate the medical-device gateway from the affected segment;
- preserve authentication and endpoint logs;
- escalate to the clinical incident commander and security lead.

### FR-12: Simulated containment

The UI must expose a **Contain Attack** action once an incident has been analyzed.

The current endpoint must return a simulated incident ID and simulated action results. Actions must be explicitly labeled as simulated.

The containment response must include `human_approval_required: true`.

### FR-13: AWS deployment

The backend must be deployable to AWS using the included SAM template.

Target architecture:

`API Gateway HTTP API -> AWS Lambda -> FastAPI/Mangum -> Gemini API`

The Gemini API key should be supplied through AWS Secrets Manager using the secret name:

`medshield/gemini`

with JSON containing:

`{"api_key": "..."}`

### FR-14: Frontend API configurability

The frontend must support an API base URL stored in browser local storage under:

`MEDSHIELD_API`

Default local value:

`http://localhost:8000`

The deployed frontend should be able to point to the API Gateway URL without rebuilding the application.

## 2. User stories

### US-01: SOC analyst triage

As a hospital SOC analyst, I want to submit a sequence of security events and receive a prioritized threat assessment so I can triage the incident quickly.

### US-02: Clinical risk awareness

As a security analyst, I want the system to distinguish cyber risk from clinical-operational risk so that attacks involving medication or medical-device infrastructure are escalated appropriately.

### US-03: Attack reconstruction

As an incident responder, I want an automatically reconstructed attack chain so that I can understand how the incident progressed without manually correlating every event.

### US-04: Evidence-backed explanation

As a security lead, I want the AI to explain why it classified an incident as severe so that the decision is auditable to a human reviewer.

### US-05: Response planning

As an incident commander, I want a concise response playbook so that the next containment and escalation steps are visible immediately.

### US-06: Safe containment demo

As a security analyst, I want to preview containment actions through a simulation so that the workflow can be demonstrated without affecting real infrastructure.

### US-07: Judge demonstration

As a hackathon judge, I should be able to trigger one obvious attack scenario and see the system move from raw telemetry to a critical incident assessment and response plan in a few seconds.

## 3. Primary demo scenario requirements

The hero scenario must demonstrate a transition from ordinary cyber anomaly to potential patient-safety-sensitive incident.

Expected narrative:

```text
17 failed logins
    -> successful login
    -> privilege escalation
    -> patient database access
    -> medication service access
    -> infusion pump gateway access
    -> CRITICAL / HIGH clinical risk
```

The judge-facing UI should make this transition visually obvious.

## 4. Constraints

### Time

The implementation target is **six hours**. Features must be prioritized by demo impact and implementation risk.

### Budget

The project should minimize paid infrastructure and avoid unnecessary managed services. AWS serverless components are preferred because they reduce setup and operational burden during the hackathon.

### Platform

- Gemini API is mandatory as the primary cloud AI path.
- A local Gemma 4 12B Instruct fallback is mandatory for model-provider resilience.
- AWS deployment is mandatory.
- Backend is currently Python/FastAPI.
- Frontend is currently a static HTML/JavaScript page using Tailwind via CDN.

### Reliability

The system must still demonstrate the complete workflow without Gemini credentials through the local Gemma 4 12B fallback; deterministic analysis is the final fallback when neither model provider is available.

### Safety

The application must not be presented as a system that autonomously controls medical devices or makes patient-care decisions.

## 5. Deferred features

These can be considered only after the core demo is stable:

- Cognito-based authentication;
- CloudFront;
- AWS WAF;
- persistent incident history in DynamoDB;
- multiple attack scenarios;
- richer SIEM ingestion;
- real log-stream processing;
- notification workflows;
- role-specific dashboards;
- compliance reporting;
- analyst feedback/feedback loops;
- production observability.

Do not allow deferred infrastructure features to delay the end-to-end Gemini demo.


## 6. AI provider configuration requirements

The provider layer must support an `auto` routing mode by default. Recommended environment variables are:

```text
AI_PROVIDER=auto
GEMINI_API_KEY=...
GEMINI_MODEL=<configured Gemini model>
LOCAL_GEMMA_BASE_URL=http://127.0.0.1:8080/v1
LOCAL_GEMMA_MODEL=gemma-4-12b-it
LOCAL_GEMMA_API_KEY=local
AI_PROVIDER_TIMEOUT_SECONDS=20
```

`LOCAL_GEMMA_BASE_URL` and `LOCAL_GEMMA_MODEL` are configurable because the project must not assume a single local runtime. The intended default protocol is OpenAI-compatible chat completions.

Provider status must be visible in the UI. Example:

```text
AI ENGINE
Gemini      CONNECTED
Local Gemma READY
Active      Gemini
```

When Gemini becomes unavailable during a request, the UI should show a non-alarming provider transition such as `Gemini unavailable - switched to Local Gemma 4 12B`, while preserving the incident workflow.
