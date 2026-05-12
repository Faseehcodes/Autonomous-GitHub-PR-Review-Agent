# Autonomous GitHub PR Review Agent

FastAPI backend for an autonomous GitHub pull request review agent.

This scaffold follows the PRD/TRD with one important change: Groq is used for both fast triage and the security-focused pass.

## Local Setup

Use Python 3.11 locally or on Render.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload --port 8000
```

## Required Environment Variables

- `GITHUB_APP_SECRET`: GitHub webhook secret.
- `GITHUB_TOKEN`: GitHub token with repository/PR permissions.
- `GROQ_API_KEY`: API key from Groq.
- `GOOGLE_API_KEY`: Optional for Gemini deep analysis. If omitted, Groq handles analysis too.
- `SUPABASE_URL`: Optional until persistence is enabled.
- `SUPABASE_SERVICE_KEY`: Optional until persistence is enabled.

## Webhook

Set your GitHub webhook URL to:

```text
https://your-public-url/webhook/github
```

Subscribe to pull request events.
