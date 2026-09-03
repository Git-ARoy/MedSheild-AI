# MedShield AI

Gemini-powered healthcare cybersecurity incident response demo for a 6-hour hackathon.

## Demo flow
1. Start the FastAPI backend.
2. Open `frontend/index.html` in a browser.
3. Click **Simulate Attack**.
4. Show the attack chain, cyber risk, clinical risk, evidence, and response playbook.
5. Click **Contain Attack** to demonstrate human-authorized simulated remediation.

## Local run
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="your-key"
uvicorn app:app --reload --port 8000
```

Open `frontend/index.html`.

Without `GEMINI_API_KEY`, the backend uses the deterministic demo analysis, so the complete UI still works offline.

## AWS
The `infra/template.yaml` is an AWS SAM starting point for API Gateway HTTP API -> Lambda -> Gemini. Store the Gemini key in AWS Secrets Manager using the secret name `medshield/gemini` and JSON like `{ "api_key": "..." }`.

For a fast hackathon deployment:
```bash
sam build --template-file infra/template.yaml
sam deploy --guided
```

Then point the frontend at the returned API URL by running:
```js
localStorage.setItem('MEDSHIELD_API', 'https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com')
```

## Safety position
This is a decision-support and simulated-response system. It does not control real medical devices or make patient diagnoses. Human authorization is required for real-world containment.


## AI provider resilience

Gemini API is the primary incident-analysis provider. If Gemini is unavailable, MedShield attempts a local Google Gemma 4 12B Instruct model (`google/gemma-4-12B-it`) through a configurable OpenAI-compatible inference endpoint. If neither model is available, the system uses deterministic demo analysis as the final fallback.

Recommended local environment variables:

```text
AI_PROVIDER=auto
LOCAL_GEMMA_BASE_URL=http://127.0.0.1:8080/v1
LOCAL_GEMMA_MODEL=gemma-4-12b-it
```
