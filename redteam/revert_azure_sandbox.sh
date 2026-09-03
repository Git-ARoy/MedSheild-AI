#!/usr/bin/env bash
# Revert HomeoCare Sandbox to Clean Baseline State
set -euo pipefail

API_URL="${MEDSHIELD_API:-http://localhost:8000}"

echo "================================================================="
echo "[RED TEAM CLEANUP] Restoring HomeoCare Sandbox to Clean Baseline"
echo "================================================================="

curl -s -X POST "$API_URL/api/redteam/revert" \
  -H "Content-Type: application/json" \
  -d '{"cleanup_nsg": true, "restore_identities": true}' | python3 -m json.tool || true

echo ""
echo "[CLEANUP COMPLETE] HomeoCare Digital Twin restored to healthy baseline."
