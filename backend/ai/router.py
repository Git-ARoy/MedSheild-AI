import os, json
from typing import Dict, Any, Optional
import httpx
from .schemas import IncidentAnalysis, Finding, RecommendedAction, VerificationReport

try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None

class AIProviderRouter:
    """
    Enterprise AI Provider Router for MedShield AI.
    Routes between Gemini API (Primary), Local Gemma 4 12B MLX (Apple Silicon local fallback),
    and deterministic safety fallback.
    """

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.local_gemma_url = os.getenv("LOCAL_GEMMA_BASE_URL", "http://localhost:11434/v1")
        self.local_gemma_model = os.getenv("LOCAL_GEMMA_MODEL", "gemma4:12b-mlx")
        self.timeout = int(os.getenv("AI_PROVIDER_TIMEOUT_SECONDS", "60"))

    def analyze(self, incident_context: Dict[str, Any]) -> IncidentAnalysis:
        pref = os.getenv("AI_PROVIDER", "auto").lower()

        if pref == "auto":
            try:
                return self._gemini_analysis(incident_context)
            except Exception as e1:
                try:
                    return self._local_gemma_analysis(incident_context)
                except Exception as e2:
                    return self._deterministic_analysis(incident_context, reason=f"Gemini error: {str(e1)} | Local Gemma error: {str(e2)}")

        elif pref == "gemini":
            try:
                return self._gemini_analysis(incident_context)
            except Exception as e:
                return self._deterministic_analysis(incident_context, reason=str(e))

        elif pref == "local_gemma":
            try:
                return self._local_gemma_analysis(incident_context)
            except Exception as e:
                return self._deterministic_analysis(incident_context, reason=str(e))

        else:
            return self._deterministic_analysis(incident_context)

    def _gemini_analysis(self, context: Dict[str, Any]) -> IncidentAnalysis:
        api_key = self.gemini_api_key
        if not api_key:
            raise Exception("Gemini API key not configured")

        prompt = (
            "You are MedShield AI, an autonomous defensive healthcare cybersecurity engine protecting the HomeoCare Azure sandbox. "
            "Analyze the supplied incident context, reconstruct the attack chain, explain cyber risk vs clinical patient safety impact, "
            "and recommend the optimal constrained response action that minimizes clinical disruption while containing the threat.\n\n"
            f"INCIDENT CONTEXT:\n{json.dumps(context, indent=2)}\n\n"
            "Respond ONLY with a valid JSON object matching the IncidentAnalysis schema."
        )

        if genai is not None:
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=self.gemini_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=IncidentAnalysis,
                        temperature=0.1,
                    ),
                )
                res = IncidentAnalysis.model_validate_json(response.text)
                res.provider = "gemini"
                res.model = self.gemini_model
                return res
            except Exception:
                pass

        # Direct REST API fallback for Gemini
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={api_key}"
        with httpx.Client(timeout=self.timeout) as http_client:
            resp = http_client.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1},
                },
            )
            resp.raise_for_status()
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            res = IncidentAnalysis.model_validate_json(text)
            res.provider = "gemini"
            res.model = self.gemini_model
            return res

    def _local_gemma_analysis(self, context: Dict[str, Any]) -> IncidentAnalysis:
        prompt = (
            "You are MedShield AI, a healthcare cybersecurity decision-support engine for HomeoCare. "
            "Analyze this incident and return ONLY valid JSON matching IncidentAnalysis schema:\n"
            f"{json.dumps(context, indent=2)}"
        )

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.local_gemma_url.rstrip('/')}/chat/completions",
                json={
                    "model": self.local_gemma_model,
                    "messages": [
                        {"role": "system", "content": "You are MedShield AI. Output ONLY valid JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1,
                    "max_tokens": 4096,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip()
            if "```json" in content:
                content = content.split("```json", 1)[1].split("```", 1)[0].strip()
            elif "```" in content:
                content = content.split("```", 1)[1].split("```", 1)[0].strip()
            if not content.startswith("{") and "{" in content:
                content = content[content.find("{"):content.rfind("}")+1]

            res = IncidentAnalysis.model_validate_json(content)
            res.provider = "local_gemma"
            res.model = f"{self.local_gemma_model} (MLX/Local)"
            return res

    def _deterministic_analysis(self, context: Dict[str, Any], reason: Optional[str] = None) -> IncidentAnalysis:
        inc_id = context.get("incident_id", "INC-2026-0001")
        assessment = context.get("clinical_assessment", {})
        actor = context.get("primary_actor", "nurse_admin")
        chain = context.get("attack_chain", ["Identity Compromise", "Privilege Escalation", "Device Gateway Access"])
        affected = context.get("affected_assets", ["identity_service", "pharmacy_api", "device_gateway"])
        trade_offs = context.get("candidate_trade_offs", {})

        return IncidentAnalysis(
            incident_id=inc_id,
            provider="demo_fallback",
            model="deterministic",
            provider_reason=reason,
            status="investigating",
            threat_level="CRITICAL" if assessment.get("clinical_risk_level") == "CRITICAL" else "HIGH",
            cyber_risk_score=94,
            clinical_risk_score=assessment.get("clinical_risk_score", 91),
            clinical_risk_level=assessment.get("clinical_risk_level", "CRITICAL"),
            attack_stage="lateral_movement",
            attack_type="Compromised Privileged Identity with Lateral Movement toward Device Gateway",
            attack_chain=chain,
            affected_assets=affected,
            findings=[
                Finding(name="Credential & Identity Anomaly", evidence=f"Compromised credential burst for actor '{actor}' across HomeoCare APIs."),
                Finding(name="Clinical System Traversal", evidence="Activity touched Pharmacy API and attempted session establishment with Device Gateway."),
                Finding(name="Medical Device Boundary Exposure", evidence="Reconnaissance detected against the simulated Infusion Pump Gateway boundary."),
            ],
            clinical_implications=[
                "Potential disruption to automated medication scheduling.",
                "Bedside infusion pump delivery control plane exposed to untrusted commands.",
                "Patient record integrity at risk if lateral movement reaches Patient Database.",
            ],
            patient_safety_impact=assessment.get(
                "patient_safety_impact",
                "CRITICAL: The adversary has traversed clinical tiers toward the simulated Medical Device Gateway. "
                "Immediate containment required to isolate bedside drug infusion delivery channels.",
            ),
            analyst_summary=(
                f"Incident {inc_id}: Actor '{actor}' engaged in multi-stage lateral movement traversing from "
                "identity service to clinical APIs. Bounded identity revocation provides 94% containment with low clinical disruption."
            ),
            recommended_action=RecommendedAction(
                tool="revoke_identity_access",
                target=actor,
                expected_cyber_effect="Immediately revokes Entra ID OAuth refresh tokens and session grants.",
                expected_clinical_effect="Maintains continuous operation of Pharmacy and EHR services for legitimate staff.",
            ),
            recommended_actions=[
                f"Revoke sign-in access and active sessions for '{actor}'",
                "Block malicious source IP at Azure NSG perimeter",
                "Isolate Medical Device Gateway network segment until forensic validation is complete",
                "Review audit logs for unauthorized medication dispensing orders",
            ],
            candidate_trade_offs=trade_offs,
            confidence=0.96,
            verification=VerificationReport(state="pending"),
        )
