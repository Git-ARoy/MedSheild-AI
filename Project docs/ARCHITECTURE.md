# MedShield AI - Architecture

## 1. Architecture summary

MedShield AI is designed as a lightweight serverless web application for a hackathon demonstration.

The current implementation consists of:

- a static browser frontend;
- a Python FastAPI backend;
- provider-agnostic AI analysis with Gemini as primary and local Gemma 4 12B as fallback;
- AWS Lambda compatibility through Mangum;
- AWS SAM infrastructure definition;
- optional AWS Secrets Manager lookup for the Gemini key.

## 2. Current technology stack

### Frontend

- HTML5
- Vanilla JavaScript
- Tailwind CSS via CDN
- Browser `fetch()` for API calls
- `localStorage` for API base URL configuration

There is intentionally no frontend framework dependency in the MVP. This keeps the six-hour hackathon build fast and eliminates frontend build/deployment complexity.

### Backend

- Python
- FastAPI
- Pydantic
- Mangum for AWS Lambda/ASGI adaptation
- `google-genai` SDK when available

### AI

Primary provider:
- Gemini API
- Configurable model through `GEMINI_MODEL`
- Structured JSON response validated against the Pydantic incident schema

Local fallback provider:
- Google Gemma 4 12B Instruct
- Model ID: `google/gemma-4-12B-it`
- Served by a local inference runtime through an OpenAI-compatible HTTP interface
- Preferred hackathon implementation: a local `llama-server`-style endpoint
- Local model is loaded once by the inference server, not per API request

Final fallback:
- deterministic `demo_analysis()`

Provider routing is `auto` by default: Gemini -> local Gemma 4 12B only on Gemini failure -> deterministic demo analysis only if both AI providers fail.

### AWS

Current SAM template targets:

- AWS Lambda
- API Gateway HTTP API
- AWS Secrets Manager for the Gemini API key
- CloudFormation/SAM as the deployment mechanism

Potential later layers include Cognito, CloudFront, WAF, DynamoDB, and CloudWatch-based telemetry, but those are not prerequisites for the core demo.

## 3. System diagram

```text
                    ┌──────────────────────────┐
                    │        Browser           │
                    │  MedShield AI Dashboard   │
                    └────────────┬─────────────┘
                                 │ HTTP
                                 ▼
                    ┌──────────────────────────┐
                    │   API Gateway HTTP API    │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │       AWS Lambda          │
                    │    Mangum + FastAPI       │
                    └────────────┬─────────────┘
                                 │
                         AI Provider Router
                                 │
                    ┌────────────┼───────────────┐
                    │            │               │
                    ▼            ▼               ▼
          ┌────────────────┐ ┌──────────────┐ ┌──────────────────┐
          │   Gemini API   │ │ Local Gemma  │ │ Demo deterministic│
          │ primary/cloud  │ │   4 12B      │ │ final fallback    │
          └────────────────┘ └──────────────┘ └──────────────────┘

                          Optional secret source
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ AWS Secrets Manager      │
                    │ medshield/gemini         │
                    └──────────────────────────┘
```

## 4. End-to-end data flow

### Local/demo flow

```text
User clicks Simulate Attack
        ↓
Frontend GET /api/events/sample
        ↓
Frontend POST /api/simulate
        ↓
Backend loads SAMPLE_EVENTS
        ↓
Gemini configured/reachable?
   ┌────┴────┐
   │         │
  yes       no/error
   │         │
   ▼         ▼
Gemini    Local Gemma 4 12B available?
             ┌────┴────┐
             │         │
            yes       no/error
             │         │
             ▼         ▼
          Local Gemma  demo_analysis()
             │         │
             └────┬────┘
                  ▼
        Pydantic validation
IncidentAnalysis Pydantic object
        ↓
JSON response
        ↓
Frontend renders threat, scores,
attack chain, clinical impact,
evidence and playbook
```

### AWS flow

```text
Browser
  ↓
API Gateway HTTP API
  ↓
Lambda
  ↓
Mangum
  ↓
FastAPI endpoint
  ↓
Gemini API
  ↓
Pydantic validation
  ↓
HTTP JSON response
```

The Gemini credential is intended to be injected into the Lambda environment from Secrets Manager using the SAM template's dynamic reference. The local Gemma provider is intentionally not a dependency of the AWS Lambda deployment because the local model is expected to run outside AWS on the developer/demo machine.

For local development, the backend should use `LOCAL_GEMMA_BASE_URL` to reach the local inference server. For AWS deployment, provider routing should gracefully use Gemini when available and otherwise fall back to deterministic analysis if no reachable local provider exists. A cloud Lambda function should not attempt to call `127.0.0.1` as a local model endpoint.

## 9. AI provider adapter design

Implement one internal interface conceptually equivalent to:

```text
IncidentAnalyzer.analyze(events) -> IncidentAnalysis + provider metadata
```

Recommended adapters:

```text
GeminiAnalyzer
LocalGemmaAnalyzer
DemoAnalyzer
AIProviderRouter
```

`AIProviderRouter` owns fallback policy. The rest of the application must not contain `if Gemini then ... else Gemma ...` logic scattered across endpoints or UI code.

The local Gemma adapter should send a structured prompt to an OpenAI-compatible local endpoint and validate the returned JSON against the exact same Pydantic schema as Gemini. If the local server does not support native JSON schema enforcement, application-level validation is mandatory.

The provider metadata should record at least:

- provider name;
- model name;
- latency if available;
- fallback reason when a lower-priority provider was used.


## 5. Repository structure

```text
medshield-ai/
├── README.md
├── PROJECT_OVERVIEW.md
├── REQUIREMENTS.md
├── ARCHITECTURE.md
├── API_SPEC.md
├── TECH_DECISIONS.md
├── .gitignore
├── backend/
│   ├── __init__.py
│   ├── .env.example
│   ├── app.py
│   ├── lambda_handler.py
│   └── requirements.txt
├── frontend/
│   └── index.html
└── infra/
    ├── deploy.sh
    └── template.yaml
```

## 6. Backend responsibilities

`backend/app.py` owns:

- API creation;
- CORS;
- request/response models;
- sample event definitions;
- deterministic demo analysis;
- Gemini analysis;
- health endpoint;
- sample event endpoint;
- incident analysis endpoint;
- attack simulation endpoint;
- simulated containment endpoint.

`backend/lambda_handler.py` adapts the FastAPI application to Lambda using Mangum.

## 7. Frontend responsibilities

`frontend/index.html` owns the complete hackathon dashboard.

The current interface includes:

- page header and mode indicator;
- threat level card;
- cyber risk card;
- clinical risk card;
- simulated live event stream;
- Simulate Attack button;
- Contain Attack button;
- attack chain panel;
- clinical impact panel;
- response playbook panel;
- analyst summary;
- evidence findings;
- safety footer.

## 8. Key design principles

### Keep the AI result structured

The frontend should not have to infer security state from natural-language paragraphs. The backend contract is a typed incident object.

### Keep the demo deterministic

The hero scenario should always be reproducible. Avoid introducing random attack generation before the basic scenario works.

### Keep the system serverless

The hackathon has a six-hour limit. Lambda + API Gateway minimizes infrastructure setup and makes AWS deployment demonstrable.

### Keep real-world action behind a human boundary

The containment endpoint is simulated. Any future integration with real security controls must introduce authentication, authorization, audit logging, approvals, and fail-safe behavior.

### Separate technical severity from clinical risk

Do not collapse everything into one score. A technical compromise and a possible clinical impact are related but operationally distinct signals.
