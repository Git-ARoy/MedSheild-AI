# MedShield AI - API Specification

## 1. API conventions

Base URL locally:

`http://localhost:8000`

Base URL in AWS:

`https://<api-id>.execute-api.<region>.amazonaws.com`

Content type for JSON requests/responses:

`application/json`

The current MVP does **not** require user authentication. This is acceptable only for the hackathon prototype. Any production deployment must add authentication and authorization before exposing incident or containment operations.

## 2. Data models

### SecurityEvent

```json
{
  "timestamp": "12:41:08",
  "user": "nurse_admin",
  "source_ip": "185.91.22.14",
  "action": "FAILED_LOGIN",
  "asset": "Identity Gateway",
  "severity": "medium",
  "details": "17 failed logins in 31 seconds"
}
```

Fields:

| Field | Type | Required | Notes |
|---|---|---:|---|
| timestamp | string | yes | Event timestamp; current demo uses `HH:MM:SS`. |
| user | string | yes | Account involved in the event. |
| source_ip | string | yes | Source address associated with event. |
| action | string | yes | Event/action name. |
| asset | string | yes | Hospital asset affected. |
| severity | string | no | Defaults to `medium`. |
| details | string | no | Free-text event context. |

### IncidentRequest

```json
{
  "events": [
    {
      "timestamp": "12:41:08",
      "user": "nurse_admin",
      "source_ip": "185.91.22.14",
      "action": "FAILED_LOGIN",
      "asset": "Identity Gateway",
      "severity": "medium",
      "details": "17 failed logins in 31 seconds"
    }
  ],
  "scenario": "healthcare_intrusion"
}
```

`scenario` defaults to `healthcare_intrusion` in the current backend.

### Finding

```json
{
  "name": "Credential anomaly",
  "evidence": "17 failed logins followed by a successful session from the same source IP."
}
```

### IncidentAnalysis

```json
{
  "threat_level": "CRITICAL",
  "cyber_risk_score": 94,
  "clinical_risk_score": 91,
  "clinical_risk": "HIGH",
  "attack_type": "Credential compromise with privilege escalation and lateral movement",
  "attack_chain": [
    "Brute-force burst",
    "Account takeover",
    "Privilege escalation",
    "Patient-data access",
    "Medication-service access",
    "Medical-device gateway access"
  ],
  "affected_assets": [
    "Identity Gateway",
    "EHR Admin API",
    "Patient Database",
    "Medication Service",
    "Infusion Pump Gateway"
  ],
  "findings": [
    {
      "name": "Credential anomaly",
      "evidence": "17 failed logins followed by a successful session from the same source IP."
    }
  ],
  "patient_safety_impact": "The intrusion has crossed from information-system compromise into systems that could affect clinical operations.",
  "analyst_summary": "The event sequence is consistent with a compromised privileged account progressing laterally through hospital infrastructure.",
  "recommended_actions": [
    "Disable the compromised account",
    "Block the source IP and revoke active sessions"
  ],
  "confidence": 0.96,
  "provider": "gemini",
  "model": "<configured Gemini model>"
}
```

Constraints enforced by Pydantic:

- `threat_level`: one of `BENIGN`, `SUSPICIOUS`, `HIGH`, `CRITICAL`;
- `cyber_risk_score`: 0-100;
- `clinical_risk_score`: 0-100;
- `clinical_risk`: one of `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`;
- `confidence`: 0-1.

## 3. AI provider routing

The analysis API uses the following provider order when `AI_PROVIDER=auto`:

```text
1. Gemini API
2. Local Gemma 4 12B Instruct
3. Deterministic demo analysis
```

Gemini is the primary provider because the hackathon requires Gemini API usage. Local Gemma 4 12B exists as the offline/provider-failure path, not as a competing default.

Recommended environment variables:

```text
AI_PROVIDER=auto
GEMINI_API_KEY=...
GEMINI_MODEL=<configured Gemini model>
LOCAL_GEMMA_BASE_URL=http://127.0.0.1:8080/v1
LOCAL_GEMMA_MODEL=gemma-4-12b-it
LOCAL_GEMMA_API_KEY=local
AI_PROVIDER_TIMEOUT_SECONDS=20
```

The local provider is expected to expose an OpenAI-compatible `/chat/completions` endpoint. The exact local runtime is configurable; the recommended hackathon runtime is a local `llama-server`-style process capable of serving Gemma 4 12B.

### Provider metadata

The successful analysis response should include:

```json
{
  "provider": "gemini",
  "model": "<configured Gemini model>"
}
```

Allowed `provider` values:

- `gemini`
- `local_gemma`
- `demo_fallback`

When a provider falls back, the backend should also make the fallback reason available through an optional response field such as `provider_reason`. Do not expose secrets or raw exception traces.

## 4. Endpoints

### GET /health

Purpose: verify API availability and expose Gemini configuration status.

Response:

```json
{
  "status": "ok",
  "gemini_configured": true,
  "local_gemma_configured": true,
  "active_provider": "gemini"
}
```

### GET /api/events/sample

Purpose: retrieve the canonical hackathon attack scenario.

Response:

```json
{
  "events": [
    {
      "timestamp": "12:41:08",
      "user": "nurse_admin",
      "source_ip": "185.91.22.14",
      "action": "FAILED_LOGIN",
      "asset": "Identity Gateway",
      "severity": "medium",
      "details": "17 failed logins in 31 seconds"
    }
  ]
}
```

The endpoint returns all six demo events.

### POST /api/analyze

Purpose: analyze a supplied event sequence.

Request body: `IncidentRequest`

Example:

```http
POST /api/analyze
Content-Type: application/json
```

```json
{
  "events": [
    {
      "timestamp": "12:41:08",
      "user": "nurse_admin",
      "source_ip": "185.91.22.14",
      "action": "FAILED_LOGIN",
      "asset": "Identity Gateway",
      "severity": "medium",
      "details": "17 failed logins in 31 seconds"
    }
  ],
  "scenario": "healthcare_intrusion"
}
```

Response: `IncidentAnalysis`

### POST /api/simulate

Purpose: run the canonical demo attack without requiring the frontend to submit the event sequence.

Current request body expectation: empty object or no meaningful fields.

Example:

```http
POST /api/simulate
Content-Type: application/json
```

Response: `IncidentAnalysis`

Internally, this endpoint analyzes `SAMPLE_EVENTS`.

### POST /api/contain

Purpose: demonstrate the response workflow without executing real security controls.

Current request does not require a body.

Response:

```json
{
  "incident_id": "MS-ABC12345",
  "status": "SIMULATED_CONTAINMENT_COMPLETE",
  "actions": [
    "Account disabled (simulated)",
    "Source IP blocked (simulated)",
    "Medical-device gateway isolated (simulated)",
    "Forensic evidence preservation started (simulated)"
  ],
  "timestamp": "2026-09-03T00:00:00+00:00",
  "human_approval_required": true
}
```

## 4. Authentication and authorization

### Current MVP

No authentication is implemented.

CORS currently allows all origins, methods, headers, and credentials in the FastAPI configuration. This is acceptable only for a local/hackathon demonstration and should not be copied unchanged into a production deployment.

### Production direction

A future production architecture should introduce:

```text
User
  ↓
Amazon Cognito
  ↓
API Gateway authorization
  ↓
FastAPI/Lambda
```

Containment operations must have stronger authorization than read-only incident analysis. A human approval mechanism and complete audit trail should be required before any real action is allowed.

## 5. Gemini contract

The backend supplies the event list to Gemini and requests a JSON response matching `IncidentAnalysis`.

The application should preserve the following contract characteristics:

- JSON-only model response;
- schema validation;
- low temperature for repeatable security analysis;
- explicit safety instruction against patient diagnosis and direct real-device control.

Environment variables:

```text
GEMINI_API_KEY=<API key>
GEMINI_MODEL=gemini-3.7-flash
```

## 6. Error behavior

The current MVP relies on FastAPI's normal validation/error handling. A future refinement should standardize API errors into a small schema such as:

```json
{
  "error": "string",
  "code": "string",
  "request_id": "string"
}
```

Do not leak Gemini credentials, stack traces, or other secrets in client-visible errors.


## 5. Local Gemma request contract

The local provider adapter should use an OpenAI-compatible chat completion request conceptually equivalent to:

```json
{
  "model": "gemma-4-12b-it",
  "messages": [
    {
      "role": "system",
      "content": "Return only JSON matching the MedShield IncidentAnalysis schema. Analyze the supplied healthcare cybersecurity events. Do not diagnose patients or provide instructions for direct control of medical devices."
    },
    {
      "role": "user",
      "content": "<serialized SecurityEvent sequence>"
    }
  ],
  "temperature": 0.1
}
```

The adapter may use whatever response-format controls the selected local runtime supports, but the final text must be parsed and validated into `IncidentAnalysis`.

The local adapter must not send patient-identifiable information to the model. The hackathon dataset remains synthetic.

## 6. Failure semantics

- Missing Gemini credentials: immediately attempt local Gemma.
- Gemini timeout/network failure: attempt local Gemma.
- Gemini recoverable HTTP/provider failure: attempt local Gemma.
- Gemini malformed structured output: log the provider failure and attempt local Gemma.
- Local Gemma unavailable: attempt deterministic demo analysis.
- Deterministic analysis used: response must explicitly identify `demo_fallback`.

The frontend should render the provider status but must not block the incident workflow solely because Gemini is unavailable.
