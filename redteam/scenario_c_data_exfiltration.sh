#!/usr/bin/env bash
# Red Team Scenario C: Synthetic Patient Data Exfiltration
set -euo pipefail

API_URL="${MEDSHIELD_API:-http://localhost:8000}"
CORRELATION_ID="RT-SCENARIO-C-$(date +%s)"
ACTOR="compromised_billing_agent"
SOURCE_IP="91.240.118.82"

echo "================================================================="
echo "[RED TEAM] Starting Scenario C: Synthetic Patient Records Exfiltration"
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

# 1. SAS Token generation
post_event "BLOB_SAS_GENERATION" "Patient Database" "medium" "Shared Access Signature (SAS) token generated with 48h read/list access"

# 2. Bulk Container Listing
post_event "STORAGE_BLOB_LIST" "Patient Database" "high" "Enumeration of all synthetic patient record blobs in 'patient-records' container"

# 3. High-volume bulk download
post_event "STORAGE_BLOB_BULK_READ" "Patient Database" "critical" "540 synthetic patient encounter summaries downloaded in 14 seconds"

# 4. EHR Archive Extraction
post_event "EHR_ARCHIVE_EXPORT" "EHR Admin API" "critical" "Direct export requested for restricted oncology and inpatient charts"

echo "================================================================="
echo "[RED TEAM] Scenario C Detonation Complete. Telemetry delivered to MedShield."
echo "================================================================="
