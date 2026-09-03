# MedShield AI Design Language

## 1. Purpose

This document defines the visual, interaction, information hierarchy, and UX rules for MedShield AI. It is intended to be consumed directly by an AI coding agent implementing or redesigning the MedShield frontend.

MedShield is a healthcare cybersecurity command-center product. The UI must communicate three things immediately:

1. A cyber incident is being detected and analyzed.
2. The system understands the incident in a healthcare context, including clinical risk.
3. The system can recommend and simulate containment actions, while retaining human authorization for real-world actions.

The product should look like a credible modern security operations center, not a generic healthcare dashboard and not a generic AI chatbot.

---

## 2. Product Personality

The interface should feel:

- Mission-critical
- Technical
- Controlled
- Precise
- High-signal
- Modern
- Operational rather than decorative
- Trustworthy without pretending that AI decisions are infallible

Avoid a friendly consumer-health aesthetic. MedShield is a security operations interface for trained users.

The visual language should combine:

- dark SOC/observability aesthetics
- restrained medical/clinical cues
- strong semantic severity states
- dense but readable information presentation
- subtle AI intelligence cues

The product should feel closer to a premium cybersecurity platform such as a SOC/SIEM console than to a hospital appointment application.

---

## 3. Primary Users

### Security Analyst

Needs to rapidly determine:

- what happened
- whether the activity is malicious
- which systems are affected
- whether a medical/clinical system is involved
- how severe the situation is
- what action should be taken next

### Security Lead / Incident Commander

Needs a higher-level view:

- active incidents
- risk distribution
- affected hospital assets
- clinical exposure
- response status
- AI-generated recommendations

### Hackathon Judge / Demonstration Viewer

Needs to understand the product within seconds without reading documentation. The core story must be visible visually:

`Cyber Event → Attack Chain → Clinical Risk → AI Analysis → Containment`

---

## 4. Design Principles

### 4.1 Signal over decoration

Every visual element must communicate operational information. Do not add charts, glows, animations, cards, or illustrations merely to make the UI look sophisticated.

### 4.2 Severity must be visually unambiguous

Threat severity is the primary state system. Critical incidents must visually dominate benign activity.

### 4.3 AI should be observable

Do not hide Gemini behind a generic "AI analyzed this" badge. The interface should expose:

- what evidence was considered
- the resulting classification
- confidence
- reconstructed attack chain
- clinical-risk reasoning
- recommended actions

### 4.4 Human-in-the-loop by default

The product must distinguish between:

- AI recommendation
- analyst approval
- simulated execution
- real-world execution

The hackathon MVP only simulates execution.

### 4.5 Progressive disclosure

Show the most important information first. Detailed logs and reasoning should be available without overwhelming the default view.

### 4.6 Consistency over novelty

Use one component system and one visual vocabulary throughout the application. Do not create one-off cards or colors for individual screens.

---

## 5. Overall Layout

Desktop-first design is the priority because the product is a security operations console.

Recommended minimum design target:

- 1440px wide desktop viewport
- 1280px should remain usable
- mobile is not the primary target

### Global layout

```text
┌──────────────────────────────────────────────────────────────────┐
│ TOP BAR                                                          │
│ MedShield AI     Environment    System Status     Operator       │
├──────────────┬───────────────────────────────────────────────────┤
│              │                                                   │
│ SIDEBAR      │ MAIN WORKSPACE                                    │
│              │                                                   │
│ Overview     │ Page header                                       │
│ Incidents    │                                                   │
│ Attack Sim   │ Content                                           │
│ Assets       │                                                   │
│ Playbooks    │                                                   │
│              │                                                   │
└──────────────┴───────────────────────────────────────────────────┘
```

Use a persistent left navigation on desktop.

The main dashboard should never feel like a collection of unrelated cards. Use a deliberate grid with clear hierarchy.

---

## 6. Navigation

Recommended navigation items:

- Overview
- Incidents
- Attack Simulation
- Hospital Assets
- Response Playbooks

The MVP may initially implement only Overview, Incidents, and Attack Simulation while keeping the rest visually present but disabled or marked as future functionality.

Navigation should be compact and icon-assisted, but labels must remain visible on the primary desktop layout.

Use active-state emphasis rather than heavy decorative backgrounds.

---

## 7. Color System

Use a predominantly dark interface.

### Base palette

Suggested semantic tokens:

```css
--bg-primary: #071019;
--bg-secondary: #0b151f;
--bg-tertiary: #101d29;
--surface: #0d1924;
--surface-elevated: #132231;
--border: #213342;
--border-strong: #304657;

--text-primary: #edf4f8;
--text-secondary: #a8b8c4;
--text-muted: #6f8290;

--accent-ai: #61e6c1;
--accent-cyan: #55d6e8;

--severity-critical: #ff4d5f;
--severity-high: #ff9f43;
--severity-medium: #f2c94c;
--severity-low: #53b7ff;
--severity-benign: #57c785;

--clinical-high: #ff5c7a;
--clinical-medium: #ffb347;
--clinical-low: #57c785;
```

These are semantic recommendations. Keep the exact implementation tokenized so the palette can be adjusted centrally.

### Color usage rules

Red is reserved for genuinely critical security or clinical states.

Orange is used for high severity.

Yellow is used for caution or medium severity.

Blue/cyan is used for information, system activity, and neutral technical states.

Green is used for healthy, contained, verified, or benign states.

The AI accent should not be used as another severity color. It represents analysis/intelligence, not danger.

Do not use red as a general brand color.

---

## 8. Typography

Use a clean modern sans-serif for the interface.

Recommended family:

- Inter, if available
- system sans-serif fallback

Recommended hierarchy:

```text
Page title:       28-32px / 700
Section title:    18-22px / 650-700
Card title:       14-16px / 600-700
Body:             13-15px / 400-500
Secondary:        12-13px / 400
Labels:            10-12px / 600-700
Metric values:    28-40px / 650-750
Code/log data:    12-13px / monospace
```

Security logs, IP addresses, timestamps, event IDs, API paths, and machine identifiers should use a monospace font.

Do not use oversized marketing typography inside the operational dashboard.

---

## 9. Spacing and Grid

Use a compact 4px/8px spacing system.

Preferred increments:

`4, 8, 12, 16, 20, 24, 32, 40`

Typical dashboard card padding:

- compact: 16px
- normal: 20px
- major hero panel: 24px

Maintain consistent 16-24px gaps between major panels.

Do not create excessive whitespace. This is an operations console and should have high information density.

---

## 10. Borders, Radius, and Elevation

Use subtle borders rather than strong shadows.

Recommended:

```text
Card radius:      10-14px
Input radius:      8-10px
Button radius:     8-10px
Pill radius:      999px
Border:            1px solid semantic border token
```

Avoid excessive glassmorphism.

A small amount of transparency may be used for overlays, but the application must remain readable and operational.

Avoid oversized rounded cards with heavy shadows because they make the interface look like a generic AI SaaS landing page.

---

## 11. Dashboard Information Hierarchy

The Overview screen should answer, in order:

1. Is the hospital currently under attack?
2. How severe is the active threat?
3. What systems are affected?
4. Does the incident create clinical/patient-safety exposure?
5. What is the attack chain?
6. What does Gemini recommend?
7. What containment action can the analyst take?

Recommended composition:

```text
┌──────────────────────┬──────────────────────┬──────────────────────┐
│ ACTIVE INCIDENTS     │ CYBER RISK           │ CLINICAL RISK        │
│ 03                   │ 91 / 100             │ HIGH                 │
└──────────────────────┴──────────────────────┴──────────────────────┘

┌───────────────────────────────────────┬────────────────────────────┐
│ ACTIVE INCIDENT / ATTACK CHAIN        │ HOSPITAL ASSET STATUS      │
│                                       │                            │
│ Brute Force                           │ EHR            ● Healthy   │
│      ↓                                │ Patient DB     ● Warning   │
│ Account Compromise                    │ Pharmacy API   ● Warning   │
│      ↓                                │ Medical IoT     ● Critical  │
│ Privilege Escalation                  │                            │
│      ↓                                │                            │
│ Medical Device Access                 │                            │
└───────────────────────────────────────┴────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│ GEMINI INCIDENT ANALYSIS                                           │
│                                                                   │
│ Classification   CRITICAL       Confidence   94%                  │
│ Clinical risk    HIGH           ...                              │
│                                                                   │
│ Evidence + explanation                                            │
│ Recommended response                                               │
│ [Generate Playbook]          [Contain Incident]                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## 12. Critical Incident Presentation

The critical incident is the primary hackathon demo moment.

When the simulated attack escalates to critical:

- update the threat status prominently
- animate the attack timeline subtly
- highlight affected assets
- display clinical risk
- surface Gemini analysis
- show recommended containment

Do not use flashing red screens or aggressive alarm animations. The interface should feel controlled, not theatrical.

A subtle pulsing indicator on the critical status badge is acceptable.

---

## 13. Threat Level Components

Threat levels must be represented consistently everywhere.

Example:

```text
● CRITICAL
● HIGH
● MEDIUM
● LOW
● BENIGN
```

Preferred presentation:

- semantic dot
- label
- optional numeric score

Example:

```text
● CRITICAL   91/100
```

Do not communicate severity using color alone. Include explicit text.

This is particularly important for accessibility and rapid scanning.

---

## 14. Clinical Risk Presentation

Clinical risk is a first-class concept and must be visually separated from cyber risk.

Example:

```text
CYBER RISK
91 / 100

CLINICAL RISK
HIGH

PATIENT SAFETY
POTENTIAL IMPACT
```

The product must avoid claiming confirmed patient harm when only cybersecurity evidence is available.

Use wording such as:

- Potential patient-safety impact
- Potential clinical disruption
- Clinical system exposure
- Medical-device access detected

Avoid statements such as:

- Patient is in danger
- Patient has been harmed
- AI confirmed patient injury

unless such facts are explicitly represented by a trusted external system, which is outside the current MVP.

---

## 15. Attack Chain Visualization

The attack chain is a major differentiator and should not be buried in a table.

Preferred form:

```text
[Initial Access]
       ↓
[Credential Compromise]
       ↓
[Privilege Escalation]
       ↓
[Patient DB Access]
       ↓
[Medication Service]
       ↓
[Medical IoT Gateway]
```

Each node may include:

- stage name
- timestamp
- affected asset
- event count
- severity

Use directional connectors to make progression visually obvious.

The current attack step may be highlighted.

The chain should remain readable on a 1280px desktop viewport.

---

## 16. Incident Event Timeline

The timeline should present machine events in chronological order.

Example:

```text
12:41:08  FAILED_LOGIN       nurse_admin       185.xxx.xxx.xxx
12:41:15  LOGIN_SUCCESS      nurse_admin       185.xxx.xxx.xxx
12:41:20  PRIV_ESCALATION    nurse_admin       host-17
12:41:32  DB_ACCESS          patient_db        host-17
12:41:45  API_ACCESS         medication_api    host-17
12:42:01  DEVICE_ACCESS      infusion_gateway  host-17
```

Use monospace for event metadata.

Events should visually increase in severity as the attack progresses.

---

## 17. Gemini Analysis Panel

Gemini's output should look like an analyst-assistance module, not a conversational chat window.

Recommended sections:

### Classification

```text
CRITICAL
Credential Compromise
```

### Confidence

```text
94%
```

### Evidence

Show concise evidence bullets or evidence chips extracted from the structured analysis.

Example:

```text
17 failed logins
Privileged account
Lateral movement
Medication API access
Medical IoT access
```

### Clinical impact

Use a concise statement, not a long AI essay.

### Recommended response

Render as ordered actions.

Do not display raw model JSON to end users. Keep raw JSON available for debugging/developer mode only.

---

## 18. AI Status Indicators

The interface should visibly distinguish AI processing states.

### Idle

`Gemini ready`

### Analyzing

`Analyzing incident...`

Use a subtle animated activity indicator.

### Complete

`Analysis complete`

### Fallback

`Local deterministic analysis`

The fallback state must not pretend that Gemini ran.

---

## 19. Buttons and Actions

Use clear operational verbs.

Primary actions:

- Simulate Attack
- Analyze Incident
- Generate Playbook
- Contain Incident
- View Evidence
- View Full Timeline

Avoid vague actions such as:

- Explore
- Magic
- Optimize
- Ask AI

### Destructive/high-impact visual treatment

`Contain Incident` should use a strong semantic treatment and confirmation step.

In the MVP, the action is simulated. The UI should explicitly state:

`Simulation only. No real hospital systems are modified.`

---

## 20. Attack Simulation UX

Attack Simulation is the primary demo control.

The screen should provide predefined scenarios rather than requiring users to construct attacks manually.

Initial scenarios:

### Scenario 1: Credential Compromise → Medical Device Access

```text
Brute Force
→ Account Takeover
→ Privilege Escalation
→ Patient DB
→ Medication Service
→ Medical IoT
```

### Scenario 2: Healthcare Ransomware

Use as a secondary demo scenario after the first core flow is stable.

The first scenario should be optimized for the judging demo.

Simulation should visibly stream or reveal events in sequence rather than instantly dumping every event onto the dashboard.

---

## 21. Response Playbook Design

The playbook should be visually structured as a response sequence.

Example:

```text
01  Disable compromised account
    Identity containment

02  Block source IP
    Network containment

03  Isolate medical-device gateway
    Clinical-system containment

04  Preserve authentication logs
    Forensic preservation
```

Each action should include:

- action name
- action category
- rationale
- status

Status options:

- Recommended
- Pending approval
- Simulated
- Completed

For the hackathon MVP, after pressing containment, show simulated completion states.

---

## 22. Asset Status Visualization

Hospital assets should use simple operational states.

Example:

```text
EHR Server             ● HEALTHY
Patient Database       ● WARNING
Medication Service     ● WARNING
Infusion Pump Gateway  ● CRITICAL
```

Asset names should remain human-readable.

Do not use fictional medical details about actual patients.

---

## 23. Charts and Data Visualization

Charts must answer an operational question.

Good examples:

- incidents by severity
- risk over time
- attack-stage progression
- affected asset count
- response status

Avoid:

- decorative donut charts with no actionable meaning
- 3D charts
- overly colorful dashboards
- more than 3-4 chart types in the MVP

For the hackathon, prioritize the attack chain and timeline over complex analytics.

---

## 24. Tables and Logs

Use tables for machine-level detail.

Recommended columns:

```text
Timestamp | Event | Actor | Source | Asset | Severity
```

Use sticky headers where appropriate.

Rows should have restrained hover states.

Avoid alternating zebra colors unless a table becomes difficult to scan without them.

---

## 25. Motion and Animation

Motion should communicate change, not decoration.

Use:

- 150-250ms transitions for UI state changes
- subtle pulse for active critical indicators
- event reveal/slide-in for simulated attacks
- small loading indicator during Gemini analysis
- animated attack-chain progression when simulation is running

Avoid:

- excessive gradients moving across the screen
- spinning dashboards
- flashing alerts
- large page transitions
- animation on every component

The interface should remain usable during a live demo.

---

## 26. AI-Specific Visual Language

Gemini-related UI can use the AI accent color, but the product must not become visually dominated by AI branding.

AI elements should use subtle indicators such as:

- small AI marker
- thin accent border
- "Gemini analysis" label
- model-processing state

Example:

```text
✦ GEMINI ANALYSIS
```

The AI layer is a capability inside MedShield, not the product's visual identity.

---

## 27. Empty States

Empty states should explain the operational state.

Example:

```text
NO ACTIVE INCIDENTS

Hospital environment is currently stable.
Run Attack Simulation to demonstrate incident analysis.

[ Simulate Attack ]
```

Avoid generic messages such as "Nothing here yet."

---

## 28. Error States

Errors must be explicit and actionable. Provider fallback should not be presented as a hard error if the replacement model succeeds.

Example Gemini failure with local Gemma success:

```text
GEMINI UNAVAILABLE

MedShield has switched to Local Gemma 4 12B for this analysis.
Incident processing continues normally.

[ Retry Gemini ]
```

Example where both model paths fail:

```text
LIVE AI UNAVAILABLE

MedShield has switched to deterministic demo analysis so the
incident workflow can continue. This result was not generated
by Gemini or Gemma.

[ Retry AI ]
```

Do not show a successful AI state when the actual Gemini call failed.

---

## 29. Loading States

Never freeze the whole application while Gemini is analyzing.

During analysis:

- preserve existing incident details
- show processing state only on the affected panel
- keep navigation usable
- allow the user to inspect raw events

Recommended copy:

`Gemini is correlating security events and assessing clinical exposure...`

---

## 30. Accessibility

Minimum requirements:

- never use color as the only severity indicator
- ensure text meets accessible contrast requirements
- keyboard-accessible interactive controls
- visible focus states
- semantic button elements
- sufficient hit area for controls
- readable monospace text

Critical/high/medium/low labels must always be textual.

---

## 31. Responsive Behavior

Desktop is primary.

At widths below 1000px:

- collapse sidebar into a compact navigation
- stack dashboard panels vertically
- preserve severity metrics near the top

At mobile widths:

- prioritize active incident and Gemini analysis
- make attack chain horizontally scrollable if necessary
- avoid attempting to preserve the full desktop grid

Mobile is a fallback, not a first-class design target for the hackathon.

---

## 32. Component Taxonomy

Build reusable components rather than page-specific markup.

Recommended components:

```text
AppShell
TopBar
Sidebar
PageHeader
MetricCard
SeverityBadge
RiskScore
IncidentCard
IncidentTable
EventTimeline
AttackChain
AssetStatusList
GeminiAnalysisPanel
EvidenceChip
ClinicalRiskPanel
ResponsePlaybook
ActionButton
SimulationScenarioCard
SimulationControls
Toast
ConfirmationDialog
LoadingState
EmptyState
ErrorState
```

Shared tokens should control color, spacing, typography, borders, and motion.

---

## 33. Recommended Frontend Styling Strategy

Use Tailwind CSS or a similarly tokenized CSS approach.

Do not hardcode slightly different versions of the same color in individual components.

Prefer semantic classes/tokens such as:

```text
bg-surface
text-primary
text-muted
border-default
severity-critical
severity-high
risk-clinical
ai-accent
```

If Tailwind is used, define the MedShield palette in the central theme configuration.

---

## 34. Data Presentation Rules

The frontend should consume structured incident data and render it consistently.

Primary incident model fields include concepts equivalent to:

```text
incident_id
timestamp
threat_level
attack_type
cyber_risk
clinical_risk
confidence
affected_assets
attack_chain
evidence
clinical_impact
recommended_actions
```

Never make the UI depend on parsing Gemini prose.

Gemini output should be validated against the backend schema before rendering.

---

## 35. Demo-First Requirements

The product is being built under a six-hour hackathon constraint. Visual implementation must prioritize the judging flow.

The critical path is:

```text
Open Dashboard
      ↓
Click Simulate Attack
      ↓
Watch events arrive
      ↓
Threat escalates
      ↓
Gemini analyzes
      ↓
Clinical risk becomes visible
      ↓
Attack chain appears
      ↓
Response playbook generated
      ↓
Contain Incident
      ↓
Simulated actions complete
```

Every part of this path should work without navigating through unnecessary configuration screens.

---

## 36. Content and Language Rules

Use concise operational language.

Preferred:

- `Credential compromise detected`
- `Medical-device gateway accessed`
- `Potential clinical impact`
- `Recommended containment`
- `Human approval required`

Avoid:

- `Our AI thinks something bad happened`
- `Magic AI defense`
- `100% secure`
- `Guaranteed detection`
- `Patient is definitely at risk`

Do not use marketing copy inside the operational dashboard.

---

## 37. Visual Do/Don't Rules

### Do

- use dark surfaces with strong contrast
- use semantic severity colors
- make threat status obvious
- expose attack progression
- emphasize clinical impact
- keep Gemini analysis structured
- use subtle motion
- make the containment action visually important

### Don't

- build a generic chatbot layout
- use a light blue hospital/medical SaaS theme
- fill the screen with cards
- overuse neon effects
- use red everywhere
- show raw model prose as the primary UI
- imply autonomous control over real medical devices
- obscure the difference between AI recommendation and action

---

## 38. Brand Mark and Header

Product name:

**MedShield AI**

Recommended wordmark treatment:

`MedShield` in primary text with `AI` using the AI accent.

Optional icon direction:

- shield geometry
- subtle medical cross or pulse motif
- network node motif

Do not make the icon look like a generic hospital logo.

Header metadata may include:

```text
MEDSHIELD AI
HEALTHCARE SECURITY OPERATIONS

Environment: Demo Hospital
System: Operational
Gemini: Connected
```

---

## 39. Trust and Safety UI

The system must make the scope of the demo explicit.

Where containment controls appear, include a subtle but visible qualifier:

`Simulation environment. No real hospital systems are modified.`

When Gemini produces recommendations, use wording that signals assistance rather than certainty:

`Gemini recommendation`

`Analyst review required`

This is an important part of the product's credibility.

---

## 40. Definition of Visual Success

A first-time viewer should be able to answer these questions within approximately 10 seconds:

1. What is MedShield?
2. Is something currently under attack?
3. How severe is it?
4. Could this affect clinical systems?
5. What does the AI recommend?

A successful design makes the following relationship visually obvious:

```text
SECURITY TELEMETRY
        ↓
GEMINI CORRELATION
        ↓
THREAT UNDERSTANDING
        ↓
CLINICAL RISK
        ↓
RESPONSE PLAYBOOK
        ↓
CONTROLLED CONTAINMENT
```

That sequence is the core product narrative and should drive all future frontend design decisions.


## 41. AI Provider Status Language

The UI must distinguish the active AI provider without making the fallback path look like an error state when it is functioning correctly.

### Provider status

Recommended header status:

```text
AI ENGINE
Gemini       CONNECTED
Local Gemma  READY
Active       Gemini
```

When Gemini is unavailable but local Gemma succeeds:

```text
AI ENGINE
Gemini       UNAVAILABLE
Local Gemma  ACTIVE
```

Use neutral operational language such as:

`Gemini unavailable. Switched to Local Gemma 4 12B.`

Do not use:

`AI FAILED`
`Emergency AI mode`
`Fallback catastrophe`

The local model is a planned resilience capability, not a product failure.

## 42. Provider Attribution in Incident Analysis

Every AI-generated analysis panel should show a small provider/model attribution line. Examples:

```text
Gemini analysis · <model>
```

or

```text
Local analysis · Gemma 4 12B Instruct
```

For deterministic fallback:

```text
Demo fallback · deterministic scenario analysis
```

Never label deterministic output as Gemini or Gemma output.

## 43. Local-model privacy cue

When local Gemma is active, a subtle status cue may state:

`Processing locally`

This is especially appropriate next to synthetic event data or telemetry panels. Do not claim that local processing guarantees security or compliance.

## 44. Provider Transition Motion

When routing changes from Gemini to Local Gemma during an incident analysis:

- keep the incident content on screen;
- update only the AI provider status;
- use a 150-250ms transition;
- avoid full-page reloads;
- preserve event timeline and scores;
- clearly attribute the resulting analysis to Local Gemma.

A provider transition should feel like graceful continuity, not a crash recovery screen.
