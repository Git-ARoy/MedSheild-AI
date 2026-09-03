#!/usr/bin/env bash
# Red Team Scenario A: Identity Compromise & Clinical Traversal toward Device Gateway
set -euo pipefail

API_URL="${MEDSHIELD_API:-http://localhost:8000}"
CORRELATION_ID="RT-SCENARIO-A-$(date +%s)"
ACTOR="nurse_admin"
SOURCE_IP="185.91.22.14"

echo "================================================================="
echo "[RED TEAM] Starting Scenario A: Identity Compromise & Clinical Traversal"
echo "Correlation ID: $CORRELATION_ID | Target: HomeoCare Sandbox"
echo "================================================================="

post_event() {
  local op="$1"
  local asset="$2"
  local sev="$3"
  local details="$4"
  local time_str="$(date -u +"%H:%M:%S")"

  curl -s -X POST "$API_URL/api/telemetry/ingest" \
    -H "Content-Type: application/json" \
    -d "{
      \"timestamp\": \"$time_str\",
      \"user\": \"$ACTOR\",
      \"source_ip\": \"$SOURCE_IP\",
      \"action\": \"$op\",
      \"asset\": \"$asset\",
      \"severity\": \"$sev\",
      \"details\": \"$details\",
      \"source\": \"azure_activity_log\"
    }" >/dev/null
  echo "  [DETONATE] $time_str | $op -> $asset ($sev)"
  sleep 1
}

# 1. Credential Anomaly / Brute-force burst
post_event "FAILED_LOGIN_BURST" "Identity Gateway" "medium" "17 failed logins in 31 seconds from unauthorized IP"
post_event "LOGIN_SUCCESS" "Identity Gateway" "high" "Successful authentication following brute-force anomaly"

# 2. Privilege Escalation
post_event "ROLE_ASSIGNMENT_ESCALATE" "Identity Gateway" "high" "Role elevated to system administrator via Entra ID RBAC"

# 3. Patient Data Access
post_event "DATA_QUERY_BULK" "Patient Database" "high" "Bulk synthetic patient record query executed"

# 4. Medication Workflow Traversal
post_event "API_ENUMERATION" "Medication Service" "high" "Medication configuration and pharmacy endpoints mapped"

# 5. Device Gateway Access Attempt
post_event "DEVICE_SESSION_ESTABLISH" "Infusion Pump Gateway" "critical" "Unauthorized session established on simulated Medical Device Gateway"

echo "================================================================="
echo "[RED TEAM] Scenario A Detonation Complete. Telemetry delivered to MedShield."
echo "================================================================="
