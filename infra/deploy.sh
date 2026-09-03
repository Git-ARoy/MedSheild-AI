#!/usr/bin/env bash
set -euo pipefail
: "${GEMINI_API_KEY:?Set GEMINI_API_KEY first}"
SECRET_NAME="medshield/gemini"
if ! aws secretsmanager describe-secret --secret-id "$SECRET_NAME" >/dev/null 2>&1; then
  aws secretsmanager create-secret --name "$SECRET_NAME" --secret-string "{\"api_key\":\"$GEMINI_API_KEY\"}" >/dev/null
else
  aws secretsmanager put-secret-value --secret-id "$SECRET_NAME" --secret-string "{\"api_key\":\"$GEMINI_API_KEY\"}" >/dev/null
fi
sam build --template-file infra/template.yaml
sam deploy --guided
