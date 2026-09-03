# HomeoCare Hospital Digital Twin

## Purpose

This document defines the hospital digital twin that MedShield AI will protect. The digital twin is a deliberately controlled, synthetic representation of a fictional hospital called **HomeoCare**. It is designed for a cybersecurity hackathon, so it must be realistic enough to produce meaningful attack paths and AWS security telemetry, but it must not represent or connect to a real hospital or real patient systems.

The digital twin is not merely a visual diagram. It is a deployable AWS environment plus a machine-readable dependency model that represents HomeoCare's identities, applications, data stores, clinical services, device gateways, network boundaries, and security controls.

The objective is to create an environment in which a controlled adversary-emulation framework such as **Stratus Red Team** can generate genuine AWS activity and telemetry, while MedShield AI consumes that telemetry, reasons over the hospital dependency graph, and performs controlled defensive actions.

## Core design principle

HomeoCare must have two representations that stay synchronized:

1. **AWS runtime representation**: actual sandbox AWS resources that generate CloudTrail/CloudWatch telemetry and have real IAM/network/security relationships.
2. **Digital-twin graph representation**: a structured model of assets and dependencies that allows MedShield to answer questions that raw AWS telemetry cannot answer by itself, such as "What clinical function is reachable from this compromised identity?" and "What services may be disrupted if this asset is isolated?"

The runtime is the source of security events. The graph is the source of business/clinical context.

## 1. HomeoCare fictional hospital profile

**Hospital name:** HomeoCare

**Type:** Fictional multi-department hospital used exclusively for simulation and demonstration.

**Environment objective:** Demonstrate cyberattacks against interconnected hospital infrastructure and the defensive behavior of MedShield AI.

**Data policy:** All patient data, identities, medical records, observations, prescriptions, device readings, and operational records are synthetic. Never load real patient-identifiable information into the project.

### Clinical departments represented

The hackathon twin should model enough clinical context to make cyber impact meaningful without attempting to reproduce every hospital subsystem.

Recommended departments:

- Emergency / acute care
- Pharmacy
- General inpatient care
- Radiology / imaging
- Outpatient services
- Clinical administration

The departments exist primarily as contextual nodes connected to technical systems.

## 2. HomeoCare asset model

Use 8-12 primary assets. Do not create dozens of AWS resources simply for visual complexity. Each asset must support an attack path, defensive decision, or clinical-impact explanation.

Recommended canonical assets:

| ID | Asset | Zone | Criticality | Clinical role |
|---|---|---|---:|---|
| `patient_portal` | Patient Portal | DMZ/Application | 5 | Patient-facing appointment and status access |
| `identity_service` | Staff Identity Service | Identity | 9 | Authentication and authorization for hospital personnel |
| `ehr_api` | EHR API | Clinical | 10 | Read/write access to synthetic electronic health records |
| `patient_db` | Patient Database | Data | 10 | Synthetic patient records |
| `pharmacy_api` | Pharmacy API | Clinical | 9 | Medication and pharmacy workflow integration |
| `medication_db` | Medication Database | Data | 9 | Synthetic prescriptions, orders, and medication state |
| `radiology_api` | Radiology/PACS API | Clinical | 8 | Synthetic imaging workflow |
| `device_gateway` | Medical Device Gateway | Clinical/Device | 10 | Controlled gateway representing connected medical devices |
| `soc_api` | MedShield/SOC API | Security | 10 | Receives telemetry and coordinates defensive actions |
| `log_pipeline` | Security Telemetry Pipeline | Security | 10 | Central event collection and routing |

The **medical device gateway is a simulation boundary**. It must not connect to an actual infusion pump, patient monitor, or any physical clinical device. It represents the security and operational control plane of such a system.

## 3. AWS implementation model

The goal is a small, inexpensive, isolated AWS sandbox rather than a production hospital architecture.

### Recommended AWS services

- **Amazon VPC** for network segmentation.
- **API Gateway** for HTTP-facing APIs.
- **AWS Lambda** for stateless application services and defensive response functions.
- **Amazon DynamoDB** for compact asset/incident state.
- **Amazon S3** for synthetic clinical records, configuration artifacts, and optional audit snapshots.
- **AWS IAM** for synthetic staff/service identities and explicit privilege relationships.
- **Amazon CloudWatch** for application/log observability.
- **AWS CloudTrail** for AWS API activity and identity/resource audit events.
- **Amazon EventBridge** for routing relevant security events to MedShield. CloudTrail events can be delivered to EventBridge, and EventBridge rules can route matching events to targets such as Lambda. citeturn190631search1turn190631search4
- **AWS Secrets Manager** for Gemini API credentials if the application is running in AWS.
- **Optional Amazon SQS** if event buffering becomes necessary. Do not add it unless event volume or reliability requirements justify it.

The AWS stack should remain serverless wherever practical.

## 4. Network topology

Use at least three conceptual network zones:

```text
                         INTERNET
                            |
                            v
                    +----------------+
                    | Public / Edge  |
                    | Patient Portal |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    | Application    |
                    | API Layer      |
                    +---+--------+---+
                        |        |
              +---------+        +------------+
              v                              v
      +---------------+              +---------------+
      | Clinical Zone |              | Identity Zone |
      | EHR           |              | Staff IAM     |
      | Pharmacy      |              | Service IAM   |
      | Radiology     |              +---------------+
      +-------+-------+
              |
              v
      +-------------------+
      | Device Gateway    |
      | Simulated Medical |
      | Device Boundary   |
      +-------------------+
              |
              X
        NO PHYSICAL DEVICES
```

Security controls and telemetry should sit outside the normal clinical paths:

```text
Clinical/Identity activity
        |
        v
   CloudTrail / Logs
        |
        v
   EventBridge rules
        |
        v
  MedShield event intake
```

## 5. Application services inside HomeoCare

The hospital applications should be simple but semantically meaningful.

### Patient Portal

A minimal API or Lambda-backed application representing patient-facing access. It can expose synthetic appointment/status information. It should not be the main target of the demo unless needed for an initial-entry scenario.

### Identity Service

Represents staff authentication and role relationships.

Define synthetic roles such as:

- `nurse`
- `pharmacist`
- `doctor`
- `radiology_technician`
- `hospital_admin`
- `security_analyst`

Define service identities separately from human identities.

The identity graph must specify which roles can access which systems. This is required for blast-radius calculation.

### EHR API

Expose a minimal synthetic record service. Example operations:

- get patient record
- update patient record
- list assigned patients
- retrieve clinical encounter

The API should be deliberately narrow and use synthetic identifiers.

### Pharmacy API

Expose synthetic medication workflow operations:

- list medication orders
- create medication order
- update medication order state
- retrieve pharmacy status

The service should contain enough metadata for the digital twin to say that a compromise could affect medication workflow without claiming that it controls a real medication-delivery device.

### Radiology/PACS API

Provide a small service representing access to imaging metadata. Actual medical imaging files are not required for the hackathon.

### Medical Device Gateway

This is the most important clinical-security boundary.

It must be implemented as a **simulation service** representing communication with connected medical devices. It can expose synthetic commands/events such as:

- `device_status`
- `gateway_status`
- `configuration_read`
- `configuration_update`

Do not create commands that attempt to interact with real devices. The service should make the boundary explicit in metadata and UI.

Example metadata:

```json
{
  "asset_id": "device_gateway",
  "name": "Medical Device Gateway",
  "is_physical_device": false,
  "clinical_role": "Controlled simulation of connected-device gateway",
  "criticality": 10
}
```

## 6. Digital twin graph

The digital twin graph is the central context model.

Every node should have:

- `id`
- `name`
- `type`
- `zone`
- `criticality`
- `clinical_role`
- `security_status`
- `owner_role`
- `dependencies`
- `reachable_from`
- `contained_by`
- `aws_resource_arns`
- `is_simulated`

Every edge should have:

- source asset
- target asset
- relationship type
- direction
- access requirement
- clinical relevance
- disruption cost

Example:

```json
{
  "source": "identity_service",
  "target": "pharmacy_api",
  "relationship": "authenticated_access",
  "required_role": "pharmacist",
  "clinical_relevance": "high",
  "disruption_cost": "high"
}
```

Example dependency chain:

```text
identity_service
      |
      v
pharmacy_api
      |
      v
medication_db
      |
      v
device_gateway
```

This chain is what allows MedShield to distinguish a generic account compromise from an account compromise with a potential patient-safety-sensitive path.

## 7. Clinical impact model

Clinical impact should not be invented by the LLM alone. Store explicit metadata in the twin.

Recommended fields:

```json
{
  "clinical_impact": {
    "service": "Medication Workflow",
    "severity": "high",
    "affected_workflow": "Medication order synchronization",
    "downtime_tolerance": "low",
    "safe_isolation": false,
    "fallback_workflow": "Manual verification"
  }
}
```

The deterministic impact engine should calculate:

- reachable clinical services
- number of affected critical assets
- maximum criticality along the path
- clinical disruption cost of possible containment actions
- whether an asset has a safe isolation boundary

Gemini may interpret these facts and explain them, but should not fabricate clinical dependencies that are absent from the model.

## 8. AWS telemetry architecture

The twin must generate genuine cloud security telemetry.

```text
AWS resource activity
        |
        v
   AWS CloudTrail
        |
        +--------------------+
        |                    |
        v                    v
 CloudWatch Logs       EventBridge
                             |
                             v
                     MedShield Intake
```

AWS documents that CloudTrail records AWS API activity and that CloudTrail events can be delivered to EventBridge. EventBridge rules can route matching events to Lambda targets. citeturn190631search2turn190631search4turn190631search0

Use this event pipeline for the security-relevant attack scenarios rather than fabricating frontend-only logs.

## 9. Stratus Red Team integration boundary

**Stratus Red Team is an external adversary-emulation component operating against a dedicated AWS test environment.** It must never be pointed at production accounts or unrelated infrastructure.

Stratus Red Team describes itself as a cloud attack emulation tool and supports AWS techniques mapped to MITRE ATT&CK. Its workflow includes warming up prerequisites, detonating a technique against a live test environment, reverting side effects, and cleaning up prerequisites. citeturn190631search10turn190631search13

The HomeoCare environment should therefore be intentionally built as a dedicated sandbox account or tightly isolated sandbox stack with explicit cleanup procedures.

Do not give the red-team runner permissions broader than the individual techniques being tested.

## 10. Recommended attack scenarios for the demo

Choose only a small number of scenarios that produce meaningful telemetry and demonstrate MedShield's strengths.

### Scenario A: Identity compromise / privilege abuse

Target:

`identity_service -> pharmacy_api -> device_gateway`

Goal:

Demonstrate that MedShield can recognize an identity compromise whose reachable path has clinical significance.

### Scenario B: Cloud control-plane defense

Use a Stratus Red Team technique supported in the sandbox that creates observable AWS control-plane activity. MedShield should detect the relevant CloudTrail event and reason about the affected HomeoCare asset.

### Scenario C: Data access / exfiltration precursor

Represent unauthorized access to the synthetic patient database or storage layer. The response should focus on credential/permission containment and protection of synthetic records.

The exact Stratus technique identifiers should be selected only after checking the current supported-technique catalogue and ensuring the chosen technique is safe and reversible in the sandbox.

## 11. Deployment model

The recommended hackathon deployment is:

```text
                    AWS ACCOUNT: HOMEOCARE-SANDBOX

  +------------------------------------------------------------+
  |                                                            |
  |  VPC / logical zones                                      |
  |                                                            |
  |   API Gateway --> Lambda clinical services                |
  |                      |                                     |
  |                      +--> DynamoDB                         |
  |                      +--> S3                               |
  |                                                            |
  |   IAM identities / roles                                  |
  |                                                            |
  |   CloudTrail -----------------------------------+          |
  |                                                   |         |
  |   CloudWatch ------------------------------------+--+      |
  |                                                       |     |
  |   EventBridge ----------------------------------------+     |
  |                                                       |     |
  |   MedShield Agent / API <------------------------------+     |
  |                                                            |
  +------------------------------------------------------------+

                    ^
                    |
             controlled test activity
                    |
             Stratus Red Team
```

Do not deploy the local Gemma 4 12B weights into Lambda. The local Gemma fallback is a local inference service and not part of the AWS runtime.

## 12. Infrastructure-as-code

Use AWS SAM/CloudFormation or Terraform. For a six-hour hackathon, prefer the existing AWS SAM approach if it is already present in the repository.

Infrastructure should be reproducible from a single command and include:

- API Gateway
- Lambda functions
- DynamoDB table(s)
- S3 bucket(s) with strict naming and retention appropriate for synthetic data
- EventBridge rules
- CloudTrail configuration required for the demo
- IAM roles/policies
- CloudWatch log groups
- optional Secrets Manager secret reference

Tag resources:

```text
Project=MedShield
Environment=HomeoCare-Sandbox
Purpose=Hackathon
DataClass=Synthetic
```

## 13. Isolation and safety requirements

These are non-negotiable.

1. HomeoCare is synthetic.
2. The AWS account/environment must be dedicated to the demo or otherwise explicitly isolated.
3. Never include real patient data, real credentials, or real medical devices.
4. Stratus Red Team is only permitted against explicitly authorized sandbox resources.
5. The attack runner should have the minimum IAM permissions required for the selected technique set.
6. Every technique used during the demo must have a documented revert/cleanup path.
7. MedShield's automated defensive actions must target only allow-listed HomeoCare resources.
8. Any destructive-looking action must be implemented as a controlled sandbox action, not a generic arbitrary AWS command executor.
9. The UI must clearly label the environment as `HomeoCare Sandbox` and the device gateway as simulated.

## 14. Success criteria for the digital twin

The digital twin is considered complete when all of the following are true:

- HomeoCare resources deploy reproducibly into AWS.
- The asset graph can identify the relationships between identity, applications, data, and the device gateway.
- Security-relevant AWS activity appears in CloudTrail/CloudWatch and can reach MedShield through the event pipeline.
- At least one selected Stratus Red Team technique can be executed against the sandbox and then reverted/cleaned up.
- MedShield can correlate a raw security event with a HomeoCare asset.
- MedShield can calculate an attack path and clinical blast radius from the twin graph.
- MedShield can recommend and execute a constrained defensive action inside the sandbox.
- The attack simulator/red-team action can be retried and the environment can be restored.
