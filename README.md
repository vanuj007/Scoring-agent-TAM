# TAM Scoring Agent

Answers: "Is this company part of my addressable universe?" — based on the
rubric in `TAM_Scoring_Agent___Version_1.md`.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000 for the web form, or use the API directly.

## API

### `POST /score`

Structured input, deterministic scoring — no LLM call.

```bash
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{
    "company_type": "Startup",
    "employee_count": 200,
    "funding_status": "VC-backed",
    "revenue_band": "$1M-$100M",
    "geography": "US"
  }'
```

### `POST /score/freetext`

Free-text company description. Uses Claude to extract the structured fields,
then runs the same deterministic scorer. Requires `ANTHROPIC_API_KEY` to be
set in the environment.

```bash
curl -X POST http://localhost:8000/score/freetext \
  -H "Content-Type: application/json" \
  -d '{"text": "Acme is a VC-backed startup, ~200 employees, remote across US and Europe, ~$10M ARR."}'
```

Both endpoints return:

```json
{
  "tam_score": 82,
  "tam_decision": "Yes",
  "tam_category": "Qualified TAM",
  "reason_codes": ["...", "...", "...", "...", "..."]
}
```

## Tests

```bash
pytest
```

## Deployment

This is a stateless FastAPI app with no database — deploy to any container
host (Render, Railway, Fly.io) or serverless platform that supports ASGI.
Set `ANTHROPIC_API_KEY` as an environment variable if you want the
`/score/freetext` endpoint enabled.
