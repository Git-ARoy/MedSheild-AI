# MedShield AI - Technical Decisions

This document records decisions made during the hackathon planning and implementation. Agents should treat these as constraints unless explicitly asked to reconsider them.

## TD-01: Build healthcare cybersecurity instead of a generic medical AI assistant

**Decision:** MedShield AI focuses on healthcare cybersecurity and clinical-operational risk.

**Rejected alternative:** generic healthcare chatbot, diagnosis assistant, or symptom checker.

**Reason:** those concepts are common hackathon patterns and do not exploit the cybersecurity theme strongly enough. The project needs differentiation and a clear reason for Gemini to perform higher-level reasoning.

## TD-02: Use Gemini for structured incident reasoning, not as a chatbot

**Decision:** Gemini receives security events and returns a typed incident assessment.

**Rejected alternative:** a conversational chatbot where users manually ask Gemini what the logs mean.

**Reason:** structured output can directly drive dashboard components such as threat level, scores, attack chain, findings, and actions. It also produces a stronger demonstration of AI functionality.

## TD-03: JSON schema + Pydantic validation

**Decision:** The Gemini response must be JSON and validated against `IncidentAnalysis`.

**Rejected alternative:** free-form model text followed by brittle string parsing.

**Reason:** deterministic field names and constraints are required for reliable UI rendering and demo stability.

## TD-04: Separate cyber risk from clinical risk

**Decision:** expose both `cyber_risk_score` and `clinical_risk_score`, plus a clinical risk level.

**Rejected alternative:** one aggregate security score.

**Reason:** the project's unique value proposition is understanding when a cybersecurity event has clinical implications. A single score hides that distinction.

## TD-05: Use an attack-chain visualization

**Decision:** present the sequence as a causal-looking chain from initial access through medical-device gateway access.

**Rejected alternative:** only showing a table of logs.

**Reason:** a table is useful to analysts but poor for a hackathon demo. The chain lets judges understand the progression immediately.

## TD-06: Use a deterministic hero scenario

**Decision:** maintain a fixed canonical six-event hospital intrusion scenario.

**Rejected alternative:** random/freshly generated attack events for the main demo.

**Reason:** a six-hour hackathon needs reproducibility. The judge must see the intended narrative every time. Randomness can be added later as an optional feature.

## TD-07: Include Gemini fallback behavior

**Decision:** fall back to `demo_analysis()` when `GEMINI_API_KEY` is missing or the SDK is unavailable.

**Rejected alternative:** require Gemini availability for every demo path.

**Reason:** network, credentials, quota, SDK installation, or internet problems should not destroy the core judging workflow.

Important: fallback behavior must not be described to judges as AI reasoning. When Gemini is unavailable, the displayed analysis is deterministic demo data.

## TD-08: Serverless AWS architecture

**Decision:** use API Gateway + Lambda, packaged through AWS SAM.

**Rejected alternative:** a persistent EC2 server or a full Kubernetes deployment.

**Reason:** the implementation time is six hours. Serverless removes operating-system configuration, server management, and unnecessary deployment overhead.

## TD-09: Keep frontend framework-free for MVP

**Decision:** use one static `frontend/index.html` with vanilla JavaScript and Tailwind CDN.

**Rejected alternative:** introducing Next.js/React as a requirement for the hackathon MVP.

**Reason:** the existing product does not require complex routing, component state management, SSR, or a build pipeline. A single static page minimizes dependencies and speeds deployment.

A framework can be introduced later if the UI grows materially.

## TD-10: Do not build a real SIEM

**Decision:** use a curated security-event sequence for the hackathon.

**Rejected alternative:** integrating Splunk, Elastic, OpenSearch, CloudWatch log streams, or a custom event-ingestion pipeline as a prerequisite for the demo.

**Reason:** real telemetry ingestion would consume the six-hour budget without improving the central judging moment proportionally. The project is demonstrating AI incident intelligence, not building a complete SIEM.

## TD-11: Simulated containment rather than real security actions

**Decision:** `/api/contain` returns simulated actions and a simulated incident ID.

**Rejected alternative:** making the prototype actually disable accounts, block IP addresses, isolate network segments, or modify medical-device systems.

**Reason:** real production actions require authentication, authorization, audit controls, rollback behavior, operational integration, and safety review. Direct medical-device control is especially inappropriate for this hackathon prototype.

## TD-12: Human authorization boundary

**Decision:** the system is presented as decision support. Any real containment requires human approval.

**Rejected alternative:** autonomous incident remediation.

**Reason:** the model is not an operational authority. Keeping a human in the loop reduces safety and governance risk and makes the product positioning more credible.

## TD-13: No patient diagnosis functionality

**Decision:** clinical impact means **clinical operational/security risk**, not medical diagnosis.

**Rejected alternative:** asking Gemini to diagnose patients or infer medical treatment from security logs.

**Reason:** it is outside the product scope and introduces unnecessary clinical safety risk. Security events should be mapped to affected systems and potential operational consequences, not to individual patient treatment decisions.

## TD-14: Secrets Manager for AWS Gemini credential

**Decision:** use AWS Secrets Manager with secret name `medshield/gemini` and an `api_key` field.

**Rejected alternative:** hard-coding the Gemini API key in source code or committing it to a `.env` file.

**Reason:** secrets must not be embedded in the repository. The SAM template already anticipates a Secrets Manager dynamic reference.

## TD-15: Defer enterprise infrastructure until the core demo is stable

**Decision:** Cognito, CloudFront, WAF, DynamoDB persistence, richer observability, and other infrastructure are secondary.

**Rejected alternative:** implementing all AWS services before the Gemini workflow is working.

**Reason:** the winning unit is the end-to-end story:

`security events -> Gemini reasoning -> clinical risk -> attack chain -> response playbook`

Infrastructure should support that story, not displace it.

## TD-16: No direct claim of novelty or "first"

**Decision:** do not market MedShield AI as the world's first, first-of-its-kind, or technically novel system without a defensible prior-art review.

**Reason:** the project is a hackathon prototype, and unsupported novelty claims create an avoidable credibility problem. Differentiation should instead be expressed as the product's specific integration of healthcare security telemetry, clinical-operational risk assessment, and Gemini-driven response reasoning.

## TD-17: Hackathon optimization over production completeness

**Decision:** optimize for a convincing, deterministic, visually clear two-minute demonstration within six hours.

**Rejected alternative:** attempting production-grade enterprise completeness during the hackathon.

**Reason:** the time constraint makes breadth counterproductive. The project should have one polished hero workflow before adding secondary features.

## TD-18: Primary judge narrative

**Decision:** start with a normal credential anomaly and escalate the severity only when the sequence reaches medication and medical-device infrastructure.

**Rejected alternative:** opening the demo immediately at CRITICAL severity.

**Reason:** showing the transition makes Gemini's reasoning visible. The judge can understand why the clinical risk score changed rather than seeing an unexplained red alert.


## TD-19: Gemini remains primary; Gemma 4 12B is the model-provider fallback

**Decision:** Gemini API is the primary AI provider because the hackathon explicitly requires Gemini API usage. When Gemini is unavailable, MedShield must attempt a local Google Gemma 4 12B Instruct model before using deterministic demo analysis.

**Rejected alternatives:**

- Gemini-only with no fallback.
- Local Gemma as the default provider, which would weaken the required Gemini integration.
- Immediate deterministic fallback when Gemini fails, which removes the opportunity to demonstrate a second real model path.

**Reason:** The local model makes the system resilient to API outages, credentials problems, quota limits, internet loss, and privacy-sensitive/offline demos while preserving Gemini as the headline integration. Google publishes Gemma 4 12B as an open-weight model that can be run locally, and its instruction-tuned variant is available as `google/gemma-4-12B-it`. citeturn117042search10turn117042search9

## TD-20: Use a provider adapter and one shared IncidentAnalysis schema

**Decision:** Gemini and local Gemma must implement the same conceptual analyzer interface and produce the same Pydantic `IncidentAnalysis` structure. A central `AIProviderRouter` owns fallback policy.

**Rejected alternative:** provider-specific branches inside each API endpoint or UI component.

**Reason:** This prevents the codebase from becoming coupled to Gemini-specific response formats and makes fallback behavior deterministic. It also ensures that the frontend cannot accidentally assume that Gemini was the provider.

## TD-21: Prefer an OpenAI-compatible local inference endpoint

**Decision:** The local Gemma adapter should communicate with a local inference server using an OpenAI-compatible HTTP protocol. The exact runtime remains configurable. A llama.cpp `llama-server`-style runtime is a preferred hackathon option because it exposes an OpenAI-compatible server and current llama.cpp includes native Gemma 4 model support. citeturn821955search0turn821955search1

**Rejected alternative:** loading the 12B model inside the FastAPI process on every request.

**Reason:** Model load time and memory usage would be unacceptable for request latency and would complicate Lambda/AWS deployment. A dedicated local model server keeps model lifecycle separate from the application API.

## TD-22: Never assume the local model exists inside AWS Lambda

**Decision:** The local Gemma path is a local development/demo capability. AWS Lambda should use Gemini when available and deterministic fallback when a local provider cannot be reached.

**Rejected alternative:** packaging Gemma weights inside the Lambda artifact/container.

**Reason:** The current 12B base model repository is roughly 24 GB in safetensors form, which is incompatible with the lightweight six-hour serverless architecture. Quantized local runtimes are therefore the intended execution path outside Lambda. citeturn117042search3

## TD-23: Local Gemma should use an instruction-tuned checkpoint

**Decision:** Use `google/gemma-4-12B-it` rather than the base `google/gemma-4-12B` for incident reasoning.

**Reason:** The application needs instruction-following behavior and structured task execution. The official instruction-tuned model is explicitly available for Gemma 4 12B. citeturn117042search9

## TD-24: Final deterministic fallback remains mandatory

**Decision:** Keep `demo_analysis()` as the third and final provider.

**Reason:** A hackathon demo cannot depend on either cloud connectivity or local model readiness. The deterministic provider guarantees that the judging workflow remains demonstrable while accurately disclosing that no live model produced that particular result.
