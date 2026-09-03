#!/usr/bin/env bash
# Red Team Scenario B: Azure Cloud Control-Plane Tampering
set -euo pipefail

API_URL="${MEDSHIELD_API:-http://localhost:8000}"
CORRELATION_ID="RT-SCENARIO-B-$(date +%s)"
ACTOR="azure_service_operator"
SOURCE_IP="194.26.29.11"

echo "================================================================="
echo "[RED TEAM] Starting Scenario B: Azure Control-Plane Tampering"
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

# 1. Suspicious RBAC Assignment
post_event "MICROSOFT.AUTHORIZATION/ROLEASSIGNMENTS/WRITE" "Identity Gateway" "high" "Unauthorized Contributor role assignment created on resource group"

# 2. Diagnostic Setting Tampering (Defense Evasion)
post_event "MICROSOFT.INSIGHTS/DIAGNOSTICSETTINGS/DELETE" "Security Telemetry Pipeline" "critical" "Attempt to disable Log Analytics audit trail export"

# 3. Network Security Group modification
post_event "MICROSOFT.NETWORK/NETWORKSECURITYGROUPS/SECURITYRULES/WRITE" "EHR Admin API" "high" "NSG inbound rule opened on port 8080 from public IP"

# 4. Storage Key Access
post_event "MICROSOFT.STORAGE/STORAGEACCOUNTS/LISTKEYS/ACTION" "Patient Database" "high" "Storage account master key retrieved via control-plane API"

echo "================================================================="
echo "[RED TEAM] Scenario B Detonation Complete. Telemetry delivered to MedShield."
echo "================================================================="
