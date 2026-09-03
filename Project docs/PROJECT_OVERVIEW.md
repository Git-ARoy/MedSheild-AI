# MedShield AI - Project Overview

## 1. Project identity

**Project name:** MedShield AI  
**Version baseline:** 0.1.0 hackathon MVP  
**Primary domain:** Healthcare cybersecurity  
**AI platform:** Gemini API  
**Cloud target:** AWS  
**Delivery context:** 6-hour hackathon prototype

MedShield AI is a healthcare cybersecurity decision-support and simulated incident-response platform. It ingests a sequence of hospital security events, correlates them into an attack narrative, assesses both conventional cyber risk and potential clinical-operational risk, and produces an analyst-ready response playbook using Gemini. When the Gemini API is unavailable, the same analysis contract must be fulfilled by a local Gemma 4 12B Instruct model so the demo remains operational without a cloud-model dependency.

The core thesis is:

> Healthcare cybersecurity is not only about protecting patient data. A cyberattack can progress into systems that support clinical operations, so security teams need a way to understand when a technical intrusion becomes a patient-safety-sensitive incident.

The application is intentionally a **security decision-support and simulation system**, not a clinical diagnosis system and not an autonomous medical-device controller.

## 2. Problem being solved

Hospital environments contain interconnected identity systems, electronic health records, patient databases, medication services, APIs, and medical-device gateways. Security telemetry is typically expressed as low-level events such as failed logins, privilege changes, API calls, or device access.

The difficult operational problem is correlating those events quickly enough to answer four questions:

1. Is this sequence actually an attack, and how severe is it?
2. What attack chain is emerging across hospital systems?
3. Does the affected infrastructure create clinical or patient-safety implications in addition to information-security risk?
4. What should the security team do next?

MedShield AI addresses this by translating technical telemetry into a structured incident assessment that can be consumed directly by an SOC-style dashboard.

## 3. Target users

### Primary user: hospital security operations analyst

The analyst needs rapid incident triage, evidence correlation, understandable explanations, and prioritized response actions.

### Secondary user: hospital security lead / incident commander

The lead needs an executive-readable view of severity, affected systems, clinical impact, and recommended containment.

### Secondary user: clinical operations/security liaison

This role needs to understand why an otherwise technical incident is potentially relevant to clinical operations.

### Hackathon/demo user

Judges should be able to understand the product without domain training. The UI therefore needs a visually obvious attack chain, risk scores, evidence, and response workflow.

## 4. Background and motivation

The original idea was deliberately positioned away from commodity healthcare AI such as generic doctor chatbots, disease diagnosis assistants, or symptom checkers. Those applications are easier to build but have weaker differentiation in a short hackathon.

The project instead combines the requested themes of **healthcare and cybersecurity** and gives Gemini a meaningful reasoning role. Gemini is not merely a chat interface. It converts a structured event sequence into a typed incident assessment containing threat level, cyber score, clinical score, attack chain, affected assets, evidence, patient-safety implications, analyst summary, recommended actions, and confidence.

The initial demo scenario represents a credential-compromise progression:

`Brute-force burst -> account takeover -> privilege escalation -> patient-data access -> medication-service access -> medical-device gateway access`

This scenario was selected because it creates a strong judging moment: the incident begins as an ordinary identity/security anomaly and becomes materially more serious when it reaches systems associated with clinical operations.

## 5. High-level goals

1. Demonstrate a credible healthcare cybersecurity use case within a six-hour implementation window.
2. Make Gemini central to incident reasoning rather than decorative, while preserving the same reasoning workflow with local Gemma 4 12B when Gemini is unavailable.
3. Show a complete path from telemetry -> AI analysis -> visualization -> response playbook.
4. Deploy the backend through AWS serverless infrastructure with a minimal operational footprint.
5. Make the demo resilient to missing or unavailable Gemini credentials/network access through a local Gemma 4 12B fallback, with deterministic demo analysis as the final safety net.
6. Produce an experience that is understandable in a two-minute judge demonstration.
7. Keep the project technically honest by clearly separating simulation/decision support from real-world security or medical-device control.

## 6. Non-goals

The current hackathon version is explicitly **not** intended to:

- diagnose patients;
- provide medical advice;
- make autonomous clinical decisions;
- directly control infusion pumps or other medical devices;
- automatically execute real containment against production hospital infrastructure;
- function as a production SIEM/EDR/NDR replacement;
- ingest real patient-identifiable information;
- build a full enterprise identity-management or SOC platform;
- implement comprehensive compliance/audit functionality;
- build a real ransomware engine or offensive intrusion capability.

Containment in the MVP is simulated. The API returns simulated action results and explicitly marks that human approval would be required for real-world containment.

## 7. Current MVP behavior

The MVP has one primary simulated attack scenario. The frontend can request the sample event sequence and ask the backend to analyze it. The backend uses an AI routing policy: Gemini is preferred when configured and reachable; when Gemini is unavailable, the backend calls the local Gemma 4 12B Instruct model through a local inference adapter; if neither AI path is available, it falls back to deterministic demo analysis. The result is rendered in the dashboard.

The dashboard currently emphasizes:

- Threat level
- Cyber risk score
- Clinical risk score and level
- Live event stream
- Attack-chain visualization
- Clinical impact explanation
- Response playbook
- Analyst summary
- Evidence findings
- Simulated containment

## 8. Product positioning

The strongest product message is:

> **MedShield AI detects when a cyberattack can become a patient-safety-sensitive incident.**

Avoid describing the system as a general-purpose AI security platform or an autonomous hospital-defense agent. Its differentiator is the explicit connection between security telemetry and clinical-operational risk.

## 9. AI provider routing policy

The application must have a single provider-agnostic incident-analysis interface. Provider selection is an implementation detail behind that interface.

Default routing mode: `auto`.

```text
AI analysis request
      |
      v
Try Gemini API
      |
      +-- success ----------------------> return validated IncidentAnalysis
      |
      +-- unavailable/error
      |
      v
Try local Gemma 4 12B Instruct
      |
      +-- success ----------------------> return validated IncidentAnalysis
      |
      +-- unavailable/error
      |
      v
Deterministic demo_analysis()
```

The primary local model identifier is `google/gemma-4-12B-it`. The local model is intended to run on the developer/demo machine or on a dedicated local inference host. The application should not download/load model weights during an incident request. The model server must already be running.

The provider used for each analysis must be exposed in the response/UI as one of:

- `gemini`
- `local_gemma`
- `demo_fallback`

The fallback chain must preserve the exact same `IncidentAnalysis` schema and safety constraints across providers.

## 10. Local privacy rationale

The local Gemma path exists not only for availability, but also to support an offline/privacy-preserving operating mode for security telemetry. Demo telemetry must remain synthetic. No production patient-identifiable information should be sent to either the cloud model or the local model.
